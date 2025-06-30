from flask import Flask, render_template, request, redirect
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
    coords = manager.get_coordinates()
    locations = manager.get_locations()
    routes, total = manager.get_route_distances()
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

if __name__ == "__main__":
    app.run(debug=True)
