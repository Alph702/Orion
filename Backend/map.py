import os
import requests
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

# Load .env file for API key
load_dotenv()
API_KEY = os.getenv("TOMTOM_API_KEY")


class TomTomManager:
    def __init__(self):
        if not API_KEY:
            raise ValueError("TOMTOM_API_KEY not found in .env")

    def search_place(self, query: str) -> dict:
        url = f"https://api.tomtom.com/search/2/search/{query}.json"
        params = {
            "key": API_KEY,
            "limit": 1
        }
        response = requests.get(url, params=params)
        return response.json()

    def geocode(self, address: str) -> dict:
        url = f"https://api.tomtom.com/search/2/geocode/{address}.json"
        params = {"key": API_KEY}
        response = requests.get(url, params=params)
        return response.json()

    def get_directions(self, origin: str, destination: str) -> dict:
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin}:{destination}/json"
        params = {
            "key": API_KEY,
            "travelMode": "car",
            "instructionsType": "text",
            "language": "en-US"
        }
        response = requests.get(url, params=params)
        return response.json()

    def fetch_static_map(self, lat, lng, zoom=17, layer="hybrid",
                         style="main", view="Unified", width=800, height=600):
        url = (
            f"https://api.tomtom.com/map/1/staticimage?"
            f"key={API_KEY}&center={lat},{lng}&zoom={zoom}"
            f"&layer={layer}&style={style}&view={view}"
            f"&width={width}&height={height}&format=png"
        )
        print("[TomTomManager] Map URL:", url)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content

class MapWidget(ttk.Frame):
    def __init__(self, parent, image_bytes, marker_path="marker.png", width=800, height=600):
        super().__init__(parent)
        self.width = width
        self.height = height

        # Load base map image
        base_img = Image.open(BytesIO(image_bytes))
        base_img = base_img.resize((self.width, self.height), Image.Resampling.LANCZOS)

        # Overlay marker
        marker = Image.open(marker_path).convert("RGBA")
        mw, mh = marker.size
        position = ((self.width - mw) // 2, (self.height - mh) // 2)
        base_img.paste(marker, position, marker)

        # Convert to Tk image
        self.tk_image = ImageTk.PhotoImage(base_img)
        self.label = ttk.Label(self, image=self.tk_image)
        self.label.pack()

def main():
    root = tk.Tk()
    root.title("Orion Map with Marker")
    root.geometry("820x650")

    def show_map():
        manager = TomTomManager()
        img_bytes = manager.fetch_static_map(lat=24.8607, lng=67.0011)
        widget = MapWidget(root, img_bytes)
        widget.pack(pady=10)

    btn = tk.Button(root, text="Load Karachi Map ↑", command=show_map)
    btn.pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()