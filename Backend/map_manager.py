import httpx
import asyncio

class MapManager:
    def __init__(self):
        self._location_cache = {}

    async def search_location(self, query: str) -> dict:
        """
        Asynchronously search for a location using OpenStreetMap's Nominatim API.
        Returns a dictionary with latitude and longitude.
        """
        if query in self._location_cache:
            return self._location_cache[query]

        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json"}
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: amanat@example.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://orion.local"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                print(f"[search_location] Request URL: {response.url}")
            except Exception as e:
                print(f"[MapManager] Nominatim request failed: {e}")
                return None

        if response.status_code == 200:
            data = response.json()
            if data and "lat" in data[0] and "lon" in data[0]:
                try:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    result = {"latitude": lat, "longitude": lon}
                    self._location_cache[query] = result
                    return result
                except ValueError:
                    print("[search_location] Invalid coordinate format.")
        elif response.status_code == 403:
            print("[search_location] Rate limited or blocked by Nominatim.")
        else:
            print(f"[search_location] API returned status {response.status_code}")

        return None

    async def get_directions(self, origin: str, destination: str) -> dict:
        """
        Asynchronously get driving directions between two locations using OSRM API.
        Returns a dictionary with distance and duration.
        """
        origin_coords, destination_coords = await asyncio.gather(
            self.search_location(origin),
            self.search_location(destination)
        )

        if not origin_coords or not destination_coords:
            return {"error": "Unable to find one or both locations."}

        url = "https://router.project-osrm.org/route/v1/driving"
        params = {"overview": "full", "geometries": "geojson"}
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: amanat@example.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://orion.local"
        }

        origin_str = f"{origin_coords['longitude']},{origin_coords['latitude']}"
        destination_str = f"{destination_coords['longitude']},{destination_coords['latitude']}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{url}/{origin_str};{destination_str}", params=params, headers=headers)
                print(f"[get_directions] Request URL: {response.url}")
            except Exception as e:
                print(f"[MapManager] OSRM request failed: {e}")
                return {"error": "Unable to retrieve directions."}

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
                    "duration": duration_str
                    # "geometry": route["geometry"]  # Uncomment if needed
                }

        return {"error": "Unable to retrieve directions."}

    async def get_place_details(self, place_name: str) -> dict:
        """
        Asynchronously get detailed information for a place using its place_id.
        Returns a dictionary with place details or error.
        """
        place_id = await self.get_place_id(place_name)
        if not place_id:
            return {"error": "Place not found or invalid place_id."}

        url = "https://nominatim.openstreetmap.org/details.php"
        params = {"place_id": place_id, "format": "json"}
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: amanat@example.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://orion.local"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                print(f"[get_place_details] Request URL: {response.url}")
            except Exception as e:
                print(f"[MapManager] Place details request failed: {e}")
                return {"error": str(e)}

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code {response.status_code}"}

    async def get_place_id(self, location: str) -> str:
        """
        Asynchronously get the place_id for a location.
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json"}
        headers = {
            "User-Agent": "OrionMapManager/1.0 (contact: amanat@example.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://orion.local"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                print(f"[get_place_id] Request URL: {response.url}")
            except Exception as e:
                print(f"[MapManager] Place ID request failed: {e}")
                return None

        if response.status_code == 200:
            data = response.json()
            if data and "place_id" in data[0]:
                return data[0]["place_id"]

        return None