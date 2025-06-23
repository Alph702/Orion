import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
from googlesearch import search
import re
from dotenv import load_dotenv
import os
from Brain.ChatBot import Chatbot

# Load environment variables from .env
load_dotenv(dotenv_path='../.env')

class RealTimeInformation:
    def __init__(self):
        self.location_data = None
        self.api_key = os.getenv('ipapiKey')
        
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

    async def get_detailed_weather(self, query):
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

        Chatbot(query=f"""This realtime information from web and other ways of getting information is not always accurate, so please verify it with other sources if you can. Here are the results: 
                ---
                📍 Location: {self.location_data['city']}
                🌤️ Condition: {self.interpret_weather_code(condition)}
                🌡️ Temperature: {temp_c}°C
                🌬️ Wind: {wind_speed} km/h from {self.degrees_to_compass(wind_dir)}
                --- 
                This is users query: {query}
                ---
                Now, please respond to the user with the best possible answer based on the information you have and the query provided. If you don't know the answer, just say 'I don't know'."""
        )

    def get_time_info(self, query):
        now = datetime.now()
        Chatbot(query=f"""This realtime information from web and other ways of getting information is not always accurate, so please verify it with other sources if you can. Here are the results: 
---
🗕️ Date: {now.strftime('%A, %d %B %Y')}
🕰️ Time: {now.strftime('%I:%M %p')}
🌍 Timezone: {self.location_data['timezone']}
--- 
This is users query: {query}
---
Now, please respond to the user with the best possible answer based on the information you have and the query provided. If you don't know the answer, just say 'I don't know'."""
        )

    async def get_location_info(self, query):
        if not self.location_data:
            self.location_data = await self.get_location()
            if "error" in self.location_data:
                return f"❌ Error fetching location: {self.location_data['error']}"
        Chatbot(query=f"""This realtime information from web and other ways of getting information is not always accurate, so please verify it with other sources if you can. Here are the results: 
                --- 
                📍 City: {self.location_data['city']}
                🗺️ Region: {self.location_data['region']}
                🌐 Country: {self.location_data['country']}
                📌 Coordinates: {self.location_data['latitute']}, {self.location_data['longitude']}
                --- 
                This is users query: {query}
                --- 
                Now, please respond to the user with the best possible answer based on the information you have and the query provided. If you don't know the answer, just say 'I don't know'."""
        )

    async def perform_search(self, query, max_results=3):
        try:
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
                except Exception:
                    pass

            Chatbot(query=f"""This realtime information from web and other ways of getting information is not always accurate, so please verify it with other sources if you can. Here are the results: 
                ---
                {results}
                --- 
                This is users query: {query}
                --- 
                Now, please respond to the user with the best possible answer based on the information you have and the query provided. If you don't know the answer, just say 'I don't know'."""
            )
        except Exception as e:
            return f"❌ Error during search: {str(e)}"

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