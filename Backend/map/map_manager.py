import math
import requests
import time

class MapManager:
    def __init__(self):
        self.locations = []

    def search_location(self, location: str):
        """
        Search for a location by name.
        Returns the first matching location or None if not found.
        """
        API_URL = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json"}
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: your_real_email@domain.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://your-real-project-url.com/"
        }
        try:
            response = requests.get(API_URL, params=params, headers=headers)
            print(f"Request URL: {response.url}")
        except Exception as e:
            print(f"Request failed: {e}")
            return None

        if response.status_code == 403:
            print("API request failed with status code 403 (Forbidden). You may be rate-limited or blocked. Try again later.")
            return None
        if response.status_code == 200:
            data = response.json()
            if data and "lat" in data[0] and "lon" in data[0]:
                try:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    # Respect Nominatim's usage policy: 1 request per second
                    time.sleep(1)
                    return {"latitude": lat, "longitude": lon}
                except ValueError:
                    print(f"Error parsing coordinates: {data[0]}")
            else:
                print(f"Invalid data received: {data}")
        else:
            print(f"API request failed with status code {response.status_code}")
        return None
    
    def get_directions(self, origin: str, destination: str) -> dict:
        """
        Get directions between two locations using OpenStreetMap's API.
        Returns a dictionary with route information or an error message.
        """
        API_URL = "https://router.project-osrm.org/route/v1/driving"
        params = {"overview": "full", "geometries": "geojson"}
        
        origin_coords = self.search_location(origin)
        destination_coords = self.search_location(destination)
        
        if not origin_coords or not destination_coords:
            return {"error": "Unable to find one or both locations."}
        
        origin_str = f"{origin_coords['longitude']},{origin_coords['latitude']}"
        destination_str = f"{destination_coords['longitude']},{destination_coords['latitude']}"
        headers = {
            "User-Agent": "OrionMapManager/1.0 (your_email@example.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://yourproject.example.com/"
        }
        response = requests.get(f"{API_URL}/{origin_str};{destination_str}", params=params, headers=headers)
        print(f"Request URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and data["routes"]:
                route = data["routes"][0]
                distance_km = round(route["distance"] / 1000, 2)
                duration_sec = route["duration"]
                hours = int(duration_sec // 3600)
                minutes = int((duration_sec % 3600) // 60)
                duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"
                return {
                    "distance": f"{distance_km} km",
                    "duration": duration_str,
                    # "geometry": route["geometry"]
                }
        return {"error": "Unable to retrieve directions."}
    
    def add_location(self, name, lat, lon):
        self.locations.append((name, float(lat), float(lon)))

    def get_locations(self):
        return self.locations

    def clear_locations(self):
        self.locations = []

    def get_coordinates(self):
        return [(lat, lon) for (_, lat, lon) in self.locations]

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    def get_route_distances(self):
        routes = []
        total = 0
        for i in range(len(self.locations) - 1):
            name1, lat1, lon1 = self.locations[i]
            name2, lat2, lon2 = self.locations[i + 1]
            dist = self.calculate_distance(lat1, lon1, lat2, lon2)
            total += dist
            routes.append((f"{name1} → {name2}", dist))
        return routes, total

    def get_place_id(self, location: str) -> str:
        """
        Get the place_id for a location name using Nominatim search.
        Returns the place_id as a string, or None if not found.
        """
        API_URL = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json"}
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: your_real_email@domain.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://your-real-project-url.com/"
        }
        try:
            response = requests.get(API_URL, params=params, headers=headers)
            print(f"Request URL: {response.url}")
        except Exception as e:
            print(f"Request failed: {e}")
            return None

        if response.status_code == 200:
            data = response.json()
            if data and "place_id" in data[0]:
                return data[0]["place_id"]
            else:
                print(f"No place_id found for location: {location}")
        else:
            print(f"API request failed with status code {response.status_code}")
        return None

    def get_place_details(self, place_name: str) -> dict:
        """
        Get detailed information for a place using its place_id from Nominatim.
        Returns a dictionary with place details or an error message.
        """
        place_id = self.get_place_id(place_name)
        if not place_id:
            return {"error": "Place not found or invalid place_id."}
        API_URL = "https://nominatim.openstreetmap.org/details.php"
        params = {
            "place_id": place_id,
            "format": "json"
        }
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: your_real_email@domain.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://your-real-project-url.com/"
        }
        try:
            response = requests.get(API_URL, params=params, headers=headers)
            print(f"Request URL: {response.url}")
        except Exception as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"API request failed with status code {response.status_code}")
            return {"error": f"Status code {response.status_code}"}