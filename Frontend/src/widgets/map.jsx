// src/widgets/MapWidget.jsx
import React, { useEffect, useRef, useState, useCallback } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css";
import "leaflet-routing-machine";
import "./map-widget.css";

export default function MapWidget({ apiUrl = "/api/locations", pollingInterval = 10000 }) {
  const [open, setOpen] = useState(true);
  const [destination, setDestination] = useState("karachi");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const mapRef = useRef(null);
  const mapDivRef = useRef(null);
  const routingRef = useRef(null);
  const markersRef = useRef([]);
  const widgetRef = useRef(null);

  const position = useRef({ x: 40, y: 40 });

  // 🗺️ Initialize map only once
  const initMap = useCallback(() => {
    if (!mapRef.current && mapDivRef.current) {
      const map = L.map(mapDivRef.current, {
        zoomControl: false,
        attributionControl: false,
      }).setView([24.86, 67.01], 10);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        detectRetina: true,
        reuseTiles: true,
        updateWhenIdle: true,
      }).addTo(map);

      mapRef.current = map;
    }
  }, []);

  // 🧹 Clear old markers/routes
  const clearMapLayers = () => {
    markersRef.current.forEach(marker => mapRef.current.removeLayer(marker));
    markersRef.current = [];

    if (routingRef.current) {
      try {
        mapRef.current.removeControl(routingRef.current);
      } catch {}
      routingRef.current = null;
    }

    mapRef.current.eachLayer(layer => {
      if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
        mapRef.current.removeLayer(layer);
      }
    });
  };

  // 🔄 Fetch and update map
  const updateMap = useCallback(async () => {
    if (!mapRef.current) return;

    setLoading(true);
    setError("");
    try {
      const res = await fetch(apiUrl);
      const data = await res.json();

      clearMapLayers();

      if (!data.coords || !data.coords.length) {
        setDestination("");
        return;
      }

      setDestination(data.locations?.[data.locations.length - 1] || "");

      data.coords.forEach((coord, i) => {
        const marker = L.marker(coord);
        marker.bindPopup(data.locations?.[i] || `Point ${i + 1}`);
        marker.addTo(mapRef.current);
        markersRef.current.push(marker);
      });

      if (data.coords.length >= 2) {
        routingRef.current = L.Routing.control({
          waypoints: data.coords.map(c => L.latLng(c[0], c[1])),
          routeWhileDragging: false,
          addWaypoints: false,
          draggableWaypoints: false,
          fitSelectedRoutes: true,
          show: false,
          createMarker: () => null,
        }).addTo(mapRef.current);
      }
    } catch {
      setError("Failed to load map data.");
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    initMap();
    updateMap();
    const interval = setInterval(updateMap, pollingInterval);
    return () => clearInterval(interval);
  }, [initMap, updateMap, pollingInterval]);

  // 🧲 Drag Optimization (No glitching, super smooth)
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
  }, [destination, open]);
  

  if (!open) return null;

  return (
    <div
      className="floating-map-widget"
      ref={widgetRef}
      style={{ left: position.current.x, top: position.current.y }}
    >
      {destination && (
        <div className="map-destination-header route-header">
          <span className="route-title">🧭 Route to {destination}</span>
          <button
            onClick={() => setOpen(false)}
            className="close-map-widget"
            title="Close Map Widget"
            aria-label="Close"
          >
            &times;
          </button>
        </div>
      )}
      <div ref={mapDivRef} className="widget-map"></div>
    </div>
  );
}
