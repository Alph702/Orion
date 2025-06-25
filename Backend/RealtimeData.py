import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
from googlesearch import search
import re
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv(dotenv_path='../.env')

class RealTimeInformation:
    def __init__(self):
        self.location_data = None
        self.api_key = os.getenv('ipapiKey')
        
    async def get(self, module, query):
        """Handle different types of information requests based on the module."""
        if module == "WEATHER":
            return await self.get_detailed_weather()
        elif module == "TIME":
            return await self.get_time_info()
        elif module == "LOCATION":
            return await self.get_location_info()
        elif module == "SEARCH":
            return await self.perform_search(query)
        else:
            return f"❌ Unknown module: {module}"
        
    async def get_location(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://ipinfo.io/json") as response:
                    ip_info = await response.json()
                    ip = ip_info.get("ip", "Unknown")
                
                async with session.get(f"https://api.ipapi.is?q={ip}&key={self.api_key}") as response:
                    data = await response.json()
                    location = data.get("location", {})
                    city = location.get("city", "Unknown")
                    region = location.get("state", "")
                    country = location.get("country", "")
                    lat = location.get("latitude", "")
                    lon = location.get("longitude", "")
                    return {
                        "city": city,
                        "region": region,
                        "country": country,
                        "latitute": lat,
                        "longitude": lon,
                        "timezone": location.get("timezone", "Unknown")
                    }
            except Exception as e:
                return {
                    "city": "Unknown", "region": "", "country": "",
                    "latitute": "", "longitude": "", "timezone": "", "error": str(e)
                }

    async def get_detailed_weather(self):
        if not self.location_data:
            self.location_data = await self.get_location()
            if "error" in self.location_data:
                return f"❌ Error fetching location: {self.location_data['error']}"
        lat = self.location_data["latitute"]
        lon = self.location_data["longitude"]
        if not lat or not lon:
            return "Location not found."

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
            f"&hourly=precipitation_probability,wind_speed_10m,wind_direction_10m"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        current = data["current_weather"]
        wind_dir = current.get("winddirection", 0)
        wind_speed = current.get("windspeed", 0)
        temp_c = current.get("temperature", 0)
        condition = current.get("weathercode", 0)

        return (
            f"📍 Location: {self.location_data['city']}\n"
            f"🌤️ Condition: {self.interpret_weather_code(condition)}\n"
            f"🌡️ Temperature: {temp_c}°C\n"
            f"🌬️ Wind: {wind_speed} km/h from {self.degrees_to_compass(wind_dir)}"
        )

    async def get_time_info(self):
        if not self.location_data:
            self.location_data = await self.get_location()
            if "error" in self.location_data:
                return f"❌ Error fetching location: {self.location_data['error']}"
        now = datetime.now()
        return (
            f"🗕️ Date: {now.strftime('%A, %d %B %Y')}\n"
            f"🕰️ Time: {now.strftime('%I:%M %p')}\n"
            f"🌍 Timezone: {self.location_data['timezone']}"
        )

    async def get_location_info(self):
        if not self.location_data:
            self.location_data = await self.get_location()
            if "error" in self.location_data:
                return f"❌ Error fetching location: {self.location_data['error']}"
        return (
            f"📍 City: {self.location_data['city']}\n"
            f"🗺️ Region: {self.location_data['region']}\n"
            f"🌐 Country: {self.location_data['country']}\n"
            f"📌 Coordinates: {self.location_data['latitute']}, {self.location_data['longitude']}"
        )

    async def perform_search(self, query, max_results=3):
        if not query or not isinstance(query, str):
            return f"❌ Invalid search query: {query}"
            
        try:
            # Validate input
            if not query or not isinstance(query, str) or query.strip() == "":
                error_msg = "❌ Search query cannot be empty"
                print(error_msg)
                return error_msg
                
            # Convert max_results to integer if it's a string
            if isinstance(max_results, str):
                try:
                    max_results = int(max_results)
                except ValueError:
                    max_results = 3  # Default if conversion fails
            
            # Ensure max_results is within reasonable bounds
            max_results = min(max(1, max_results), 10)  # Between 1 and 10
            
            print(f"🔍 Searching for: {query} (max results: {max_results})")
            searcher = search(query, num_results=max_results, lang="en")
            links = list(searcher)

            valid_links = [
                link for link in links if all(bad not in link for bad in [
                    "gstatic", "google.com/search", "accounts.google.com", ".jpg", ".png", ".webp"
                ])
            ][:max_results]

            results = []
            for link in valid_links:
                summary = await self.scrape_summary(link)
                results.append(f"🔗 {link}\n📜 {summary or 'Summary not available'}")

            # Integrated Wikipedia inside search system
            title = re.sub(r"[^\w\s]", "", query).strip().replace(" ", "_").title()
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(wiki_url) as response:
                        data = await response.json()
                        if 'extract' in data:
                            results.append(f"📘 Wikipedia Summary:\n{data['extract']}")
                except Exception as e:
                    print(f"Wikipedia lookup failed: {e}")
            
            search_results = f"🔍 Search Results for '{query}':\n\n{"\n\n".join(results) if results else "❌ No useful results found."}"
            print(f"Found {len(results)} results for query: {query}")
            return search_results
        except Exception as e:
            error_msg = f"❌ Error during search: {str(e)}"
            print(error_msg)
            return error_msg  # Always return a string, never None

    async def scrape_summary(self, url):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=7) as response:
                    html = await response.text()

            soup = BeautifulSoup(html, "html.parser")
            for p in soup.find_all("p"):
                text = p.get_text().strip()
                if len(text) > 80:
                    return text
            return None
        except:
            return None

    def interpret_weather_code(self, code):
        code_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog",
            48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Heavy drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 71: "Light snow",
            73: "Moderate snow", 75: "Heavy snow", 80: "Rain showers", 81: "Heavy showers",
            82: "Violent rain", 95: "Thunderstorm", 96: "Storm with hail", 99: "Violent storm with hail"
        }
        return code_map.get(code, "Unknown condition")

    def degrees_to_compass(self, degree):
        dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        ix = int((degree + 22.5) / 45.0) % 8
        return dirs[ix]

# RealTimeInformation = RealTimeInformation()
# # Example usage:
# asyncio.run(RealTimeInformation.get_location_info("Where am I?"))