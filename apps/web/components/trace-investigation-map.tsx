"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import { MapPin, Route } from "lucide-react";
import * as maplibregl from "maplibre-gl";
import { useEffect, useRef, useState } from "react";

import type { Location, TraceRun } from "@/lib/api";
import { SyntheticNetworkFallback } from "@/components/synthetic-network-fallback";

type Coordinate = [number, number];

function coordinate(longitude: number, latitude: number): Coordinate | null {
  return Number.isFinite(longitude) && Number.isFinite(latitude) ? [longitude, latitude] : null;
}

function markerElement(label: string, colour: string) {
  const element = document.createElement("button");
  element.type = "button";
  element.setAttribute("aria-label", label);
  element.title = label;
  element.style.cssText = `width:18px;height:18px;border:3px solid #ffffff;border-radius:9999px;background:${colour};box-shadow:0 1px 5px rgba(15,23,42,.45);cursor:pointer;z-index:20;`;
  return element;
}

export function TraceInvestigationMap({ trace }: { trace: TraceRun }) {
  const mapElement = useRef<HTMLDivElement>(null);
  const [movementLinks, setMovementLinks] = useState<Array<{ x1: number; y1: number; x2: number; y2: number }>>([]);
  const [fallback, setFallback] = useState(false);

  useEffect(() => {
    if (!mapElement.current) return;
    try { const canvas = document.createElement("canvas"); if (!canvas.getContext("webgl") && !canvas.getContext("experimental-webgl")) { setFallback(true); return; } } catch { setFallback(true); return; }
    const origin = coordinate(trace.outbreak.location.longitude, trace.outbreak.location.latitude);
    if (!origin) return;
    const impacted = trace.impacted_locations
      .map((location) => ({ location, coordinate: coordinate(location.longitude, location.latitude) }))
      .filter((item): item is { location: Location; coordinate: Coordinate } => item.coordinate !== null);
    let cancelled = false;
    let rendered = false;
    setMovementLinks([]);
    const readyTimer = window.setTimeout(() => { if (!rendered) setFallback(true); }, 1800);
    const map = new maplibregl.Map({
      container: mapElement.current,
      style: {
        version: 8,
        sources: {},
        layers: [{ id: "synthetic-paper", type: "background", paint: { "background-color": "#dce6db" } }],
      },
      center: origin,
      zoom: 10,
    });

    const updateMovementLinks = () => {
      if (cancelled || !map.loaded()) return;
      const originPoint = map.project(origin);
      setMovementLinks(impacted.map(({ coordinate: destination }) => {
        const destinationPoint = map.project(destination);
        return { x1: originPoint.x, y1: originPoint.y, x2: destinationPoint.x, y2: destinationPoint.y };
      }));
    };

    const renderFeatures = () => {
      if (cancelled || rendered || !map.loaded()) return;
      rendered = true;
      window.clearTimeout(readyTimer);
      new maplibregl.Marker({ element: markerElement(`Confirmed outbreak origin: ${trace.outbreak.location.name}`, "#b42318") })
        .setLngLat(origin)
        .addTo(map);
      impacted.forEach(({ location, coordinate: locationCoordinate }) => {
        new maplibregl.Marker({ element: markerElement(`Impacted recorded location: ${location.name}`, "#b45309") })
          .setLngLat(locationCoordinate)
          .addTo(map);
      });

      const bounds = new maplibregl.LngLatBounds(origin, origin);
      impacted.forEach(({ coordinate: locationCoordinate }) => bounds.extend(locationCoordinate));
      requestAnimationFrame(() => {
        if (cancelled) return;
        map.resize();
        map.fitBounds(bounds, { padding: 48, maxZoom: 12, duration: 0 });
        updateMovementLinks();
      });
    };

    map.once("load", renderFeatures);
    map.once("error", () => setFallback(true));
    map.on("move", updateMovementLinks);
    map.on("zoom", updateMovementLinks);
    map.on("resize", updateMovementLinks);
    if (map.loaded()) requestAnimationFrame(renderFeatures);
    return () => {
      cancelled = true;
      window.clearTimeout(readyTimer);
      map.off("move", updateMovementLinks);
      map.off("zoom", updateMovementLinks);
      map.off("resize", updateMovementLinks);
      map.remove();
    };
  }, [trace]);

  const locationNames = trace.impacted_locations.map((location) => location.name).join(", ") || "No additional impacted locations were recorded.";
  return <figure className="overflow-hidden rounded-xl border border-line bg-white">
    <div className="relative h-72" aria-label="Interactive trace investigation map">
      <div ref={mapElement} className="absolute inset-0" />
      <svg aria-hidden="true" className="pointer-events-none absolute inset-0 z-10 h-full w-full overflow-visible">
        {movementLinks.map((link, index) => <line key={`${link.x1}-${link.y1}-${link.x2}-${link.y2}-${index}`} x1={link.x1} y1={link.y1} x2={link.x2} y2={link.y2} stroke="#0f8b8d" strokeWidth="5" strokeOpacity="0.95" strokeLinecap="round" />)}
      </svg>
      <div className="pointer-events-none absolute inset-0 z-20"><SyntheticNetworkFallback locations={[]} outbreaks={[]} origin={trace.outbreak.location} impacted={trace.impacted_locations} lines={trace.impacted_locations.map((location) => ({ coordinates: [[trace.outbreak.location.longitude, trace.outbreak.location.latitude], [location.longitude, location.latitude]], color: "#0f8b8d", label: "Recorded movement link" }))} /></div>
      {fallback&&<span className="sr-only">MapLibre background is unavailable; the controlled synthetic network view remains visible.</span>}
    </div>
    <figcaption className="border-t border-line p-4 text-sm text-slate-700">
      <div className="flex flex-wrap gap-x-5 gap-y-2 font-semibold text-ink" aria-label="Map legend"><span className="inline-flex items-center gap-2"><MapPin size={16} className="text-risk-red" aria-hidden="true" />Confirmed outbreak origin</span><span className="inline-flex items-center gap-2"><MapPin size={16} className="text-risk-amber" aria-hidden="true" />Impacted recorded location</span><span className="inline-flex items-center gap-2"><Route size={16} className="text-teal" aria-hidden="true" />Recorded movement link</span></div>
      <p className="mt-3 leading-6">Text alternative: outbreak origin at {trace.outbreak.location.name}. Linked recorded locations: {locationNames}.</p>
    </figcaption>
  </figure>;
}
