from flask import Flask, render_template, request, redirect, jsonify
from Backend.map.map_manager import MapManager

app = Flask(__name__)

manager = MapManager()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        print("Form submitted:", request.form)
        if name and lat and lon:
            manager.add_location(name, lat, lon)
            return redirect("/")
        elif name:
            manager.add_location(name)
            return redirect("/")
    coords = manager.get_coordinates()
    locations = manager.get_locations()
    routes, total = manager.get_route_distances()
    # Only show routes if there are at least 2 coords
    if len(coords) < 2:
        routes, total = [], None
    return render_template("map.html",
        coords=coords,
        locations=locations,
        routes=routes,
        total=total,
        default_name="Home",
        default_lat="24.8607",
        default_lon="67.0011"
    )

@app.route("/clear")
def clear():
    manager.clear_locations()
    return redirect("/")

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

if __name__ == "__main__":
    app.run(debug=True)
