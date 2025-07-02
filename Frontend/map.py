from flask import Flask, request, jsonify
import os
import asyncio
from Backend.map_manager import MapManager

app = Flask(__name__, static_folder="../Frontend/dist", static_url_path="/")
manager = MapManager()

@app.route("/api/search", methods=["POST"])
def search_location():
    data = request.get_json()
    location = data.get("location")
    if not location:
        return jsonify({"error": "Missing location"}), 400

    result = asyncio.run(manager.search_location(location))
    if result:
        return jsonify({"location": result})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/directions", methods=["POST"])
def get_directions():
    data = request.get_json()
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"error": "Missing origin or destination"}), 400

    result = asyncio.run(manager.get_directions(origin, destination))
    return jsonify(result)

@app.route("/api/details", methods=["POST"])
def get_details():
    data = request.get_json()
    place = data.get("place")
    if not place:
        return jsonify({"error": "Missing place"}), 400

    result = asyncio.run(manager.get_place_details(place))
    return jsonify(result)

# React App routing
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    target_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(target_path):
        return app.send_static_file(path)
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)
