import requests
import time

class MapManager:
    def __init__(self):
        self.locations = []  # List of (name, lat, lon) or (name,)

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

    def add_location(self, name, lat=None, lon=None):
        """
        Add a location by name, optionally with coordinates.
        """
        if lat is not None and lon is not None:
            self.locations.append((name, float(lat), float(lon)))
        else:
            self.locations.append((name,))

    def get_locations(self):
        """
        Return a list of all location names.
        """
        return [loc[0] for loc in self.locations]

    def get_coordinates(self):
        """
        Return a list of [lat, lon] for locations that have coordinates.
        """
        coords = []
        for loc in self.locations:
            if len(loc) == 3:
                coords.append([loc[1], loc[2]])
        return coords

    def clear_locations(self):
        """
        Clear all stored locations.
        """
        self.locations = []

    def get_route_distances(self):
        """
        Return a list of (route, distance) tuples and total distance if coordinates exist, else None.
        """
        routes = []
        total = 0
        for i in range(len(self.locations) - 1):
            loc1 = self.locations[i]
            loc2 = self.locations[i + 1]
            name1 = loc1[0]
            name2 = loc2[0]
            if len(loc1) == 3 and len(loc2) == 3:
                dist = self.calculate_distance(loc1[1], loc1[2], loc2[1], loc2[2])
                total += dist
                routes.append((f"{name1} → {name2}", dist))
            else:
                routes.append((f"{name1} → {name2}", None))
        return routes, total if routes and routes[0][1] is not None else None

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points (Haversine formula).
        """
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth radius in kilometers
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return round(R * c, 2)

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

    def get_location_tuples(self):
        """
        Return the raw list of location tuples (name, lat, lon) or (name,).
        """
        return self.locations