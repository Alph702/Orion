from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
import os
from Backend.map.map_manager import MapManager

app = Flask(
    __name__,
    static_folder="../../Frontend/dist",  # Adjust path if needed
    static_url_path="/"
)

manager = MapManager()

# Legacy/admin template route (optional)
@app.route("/legacy-map", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        print("Form submitted:", request.form)
        if name and lat and lon:
            manager.add_location(name, lat, lon)
            return redirect("/legacy-map")
        elif name:
            manager.add_location(name)
            return redirect("/legacy-map")
    coords = manager.get_coordinates()
    locations = manager.get_locations()
    routes, total = manager.get_route_distances()
    if len(coords) < 2:
        routes, total = [], None
    # Remove default_name/default_lat/default_lon; frontend handles initial state
    return render_template(
        "map.html",
        coords=coords,
        locations=locations,
        routes=routes,
        total=total,
    )

@app.route("/clear")
def clear():
    manager.clear_locations()
    return redirect("/legacy-map")

@app.route("/api/locations", methods=["POST"])
def api_locations():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "reason": "Missing data"}), 400
    location = data.get("location")
    lat = data.get("lat")
    lon = data.get("lon")
    if location and lat and lon:
        manager.add_location(location, lat, lon)
    elif location:
        coords = manager.search_location(location)
        if coords:
            manager.add_location(location, coords["latitude"], coords["longitude"])
        else:
            manager.add_location(location)
    else:
        return jsonify({"status": "error", "reason": "Missing data"}), 400
    all_coords = manager.get_coordinates()
    all_locations = manager.get_locations()
    all_tuples = manager.get_location_tuples()
    routes, total = manager.get_route_distances()
    if len(all_coords) < 2:
        routes, total = [], None
    return jsonify({
        "status": "ok",
        "all_coords": all_coords,
        "all_locations": all_locations,
        "all_tuples": all_tuples,
        "routes": routes,
        "total": total
    })

@app.route("/api/locations", methods=["GET"])
def api_locations_get():
    coords = manager.get_coordinates()
    locations = manager.get_locations()
    all_tuples = manager.get_location_tuples()
    routes, total = manager.get_route_distances()
    if len(coords) < 2:
        routes, total = [], None
    return jsonify({
        "coords": coords,
        "locations": locations,
        "all_tuples": all_tuples,
        "routes": routes,
        "total": total
    })

@app.route("/api/clear", methods=["POST"])
def api_clear():
    manager.clear_locations()
    return jsonify({"status": "ok"})

@app.route("/api/directions", methods=["POST"])
def api_directions():
    data = request.get_json()
    origin = data.get("origin")
    destination = data.get("destination")
    if not origin or not destination:
        return jsonify({"error": "Missing origin or destination"}), 400
    result = manager.get_directions(origin, destination)
    return jsonify(result)

@app.route("/api/place_details", methods=["POST"])
def api_place_details():
    data = request.get_json()
    place = data.get("place")
    if not place:
        return jsonify({"error": "Missing place"}), 400
    result = manager.get_place_details(place)
    return jsonify(result)

# Serve React build files (for integration)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True)
