import React, { useRef, useState, useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-routing-machine";
import "./map-widget.css";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "/static/marker-icon.png",
  shadowUrl: "/static/marker-shadow.png"
});

export default function MapWidget() {
  const mapRef = useRef(null);
  const mapDivRef = useRef(null);
  const routingRef = useRef(null);
  const widgetRef = useRef(null);

  const [origin] = useState("Karachi");
  const [destination] = useState("Hyderabad");
  const [open, setOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const position = useRef({ x: 40, y: 40 });

  const closeWidget = () => setOpen(false);

  const initMap = () => {
    if (!mapRef.current && mapDivRef.current) {
      mapRef.current = L.map(mapDivRef.current).setView([24.86, 67.01], 10);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(mapRef.current);
    }
  };

  const fetchCoords = async (location) => {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location })
    });
    const data = await res.json();
    return data.location || null;
  };

  const drawRoute = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/directions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ origin, destination })
      });
      const data = await res.json();

      if (!data || data.error) {
        alert("Route not found.");
        return;
      }

      const originCoords = await fetchCoords(origin);
      const destCoords = await fetchCoords(destination);

      if (!originCoords || !destCoords) return;

      if (routingRef.current) {
        mapRef.current.removeControl(routingRef.current);
      }

      routingRef.current = L.Routing.control({
        waypoints: [
          L.latLng(originCoords.latitude, originCoords.longitude),
          L.latLng(destCoords.latitude, destCoords.longitude)
        ],
        routeWhileDragging: false,
        addWaypoints: false,
        draggableWaypoints: false,
        show: false,
        createMarker: () => null
      }).addTo(mapRef.current);

    } catch (err) {
      console.error(err);
      alert("Error loading route.");
    } finally {
      setLoading(false);
    }
  };

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e) => {
      if (e.key === "Escape") closeWidget();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  // 🧲 Drag widget from header
  useEffect(() => {
    const widget = widgetRef.current;
    const header = widget?.querySelector(".map-destination-header");
    if (!widget || !header) return;

    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    const onPointerDown = (e) => {
      isDragging = true;
      const rect = widget.getBoundingClientRect();
      offsetX = e.clientX - rect.left;
      offsetY = e.clientY - rect.top;
      document.body.style.userSelect = "none";
      header.setPointerCapture(e.pointerId);
    };

    const onPointerMove = (e) => {
      if (!isDragging) return;
      const x = e.clientX - offsetX;
      const y = e.clientY - offsetY;
      widget.style.left = `${x}px`;
      widget.style.top = `${y}px`;
      position.current = { x, y };
    };

    const onPointerUp = (e) => {
      isDragging = false;
      document.body.style.userSelect = "";
      header.releasePointerCapture(e.pointerId);
    };

    header.addEventListener("pointerdown", onPointerDown);
    header.addEventListener("pointermove", onPointerMove);
    header.addEventListener("pointerup", onPointerUp);

    return () => {
      header.removeEventListener("pointerdown", onPointerDown);
      header.removeEventListener("pointermove", onPointerMove);
      header.removeEventListener("pointerup", onPointerUp);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    initMap();
    drawRoute();
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="floating-map-widget"
      ref={widgetRef}
      style={{ left: position.current.x, top: position.current.y }}
    >
      <div className="map-destination-header route-header">
        <span>🧭 Route: {origin} → {destination}</span>
        <button
          onClick={closeWidget}
          className="close-map-widget"
          title="Close Map Widget"
          aria-label="Close"
        >
          &times;
        </button>
      </div>
      <div ref={mapDivRef} className="widget-map"></div>
    </div>
  );
}
