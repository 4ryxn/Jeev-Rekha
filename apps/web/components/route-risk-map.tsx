"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useMemo, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";

import { SyntheticNetworkFallback, type NetworkLine } from "@/components/synthetic-network-fallback";
import type { Location, Outbreak, RouteAssessment } from "@/lib/api";

const noWebGL = () => {
  try {
    const canvas = document.createElement("canvas");
    return !canvas.getContext("webgl") && !canvas.getContext("experimental-webgl");
  } catch {
    return true;
  }
};

export function RouteRiskMap({
  assessment,
  locations,
  outbreaks,
  routeOrigin,
  routeDestination,
}: {
  assessment?: RouteAssessment;
  locations: Location[];
  outbreaks: Outbreak[];
  routeOrigin?: Location;
  routeDestination?: Location;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [fallback, setFallback] = useState(false);
  const lines = useMemo<NetworkLine[]>(
    () => [
      ...(assessment ? [{
        coordinates: assessment.preferred_route.coordinates,
        color: "#334155",
        label: "Assessed movement route",
        dasharray: [2.5, 2],
      }] : []),
      ...(assessment?.safer_route ? [{
        coordinates: assessment.safer_route.coordinates,
        color: "#0f8b8d",
        label: "Safer route",
      }] : []),
    ],
    [assessment],
  );

  useEffect(() => {
    if (!ref.current) return;
    if (noWebGL()) {
      setFallback(true);
      return;
    }

    let done = false;
    const timer = window.setTimeout(() => { if (!done) setFallback(true); }, 1800);
    const map = new maplibregl.Map({
      container: ref.current,
      style: { version: 8, sources: {}, layers: [{ id: "paper", type: "background", paint: { "background-color": "#e9eee5" } }] },
      center: [77.55, 13.03],
      zoom: 10,
    });
    const fail = () => setFallback(true);
    map.once("error", fail);
    map.once("load", () => {
      done = true;
      window.clearTimeout(timer);
      lines.forEach((line, index) => {
        map.addSource(`route-${index}`, { type: "geojson", data: { type: "Feature", geometry: { type: "LineString", coordinates: line.coordinates } } as never });
        map.addLayer({
          id: `route-${index}`,
          type: "line",
          source: `route-${index}`,
          paint: { "line-color": line.color, "line-width": 5, "line-opacity": 0.9, ...(line.dasharray ? { "line-dasharray": line.dasharray } : {}) },
        });
      });
      const points = locations.map((location) => ({ type: "Feature", geometry: { type: "Point", coordinates: [location.longitude, location.latitude] }, properties: { name: location.name } }));
      map.addSource("locations", { type: "geojson", data: { type: "FeatureCollection", features: points } as never });
      map.addLayer({ id: "locations", type: "circle", source: "locations", paint: { "circle-radius": 6, "circle-color": "#0f766e", "circle-stroke-color": "#fff", "circle-stroke-width": 2 } });
      const zones = outbreaks.filter((outbreak) => outbreak.status !== "closed").map((outbreak) => ({ type: "Feature", geometry: { type: "Point", coordinates: [outbreak.location.longitude, outbreak.location.latitude] }, properties: { status: outbreak.status } }));
      map.addSource("zones", { type: "geojson", data: { type: "FeatureCollection", features: zones } as never });
      map.addLayer({ id: "zones", type: "circle", source: "zones", paint: { "circle-radius": 16, "circle-color": ["match", ["get", "status"], "confirmed", "#b42318", "#b45309"], "circle-opacity": 0.35 } });
      if (assessment) {
        const bounds = new maplibregl.LngLatBounds();
        assessment.preferred_route.coordinates.forEach((coordinate) => bounds.extend(coordinate as [number, number]));
        map.fitBounds(bounds, { padding: 35, maxZoom: 12, duration: 0 });
      }
    });

    return () => {
      window.clearTimeout(timer);
      map.remove();
    };
  }, [assessment, locations, outbreaks, lines]);

  return <div className="relative h-72 overflow-hidden rounded-xl border border-line" aria-label="Interactive synthetic movement network"><div ref={ref} className="absolute inset-0" /><div className="pointer-events-none absolute inset-0 z-20"><SyntheticNetworkFallback locations={locations} outbreaks={outbreaks} lines={lines} routeOrigin={routeOrigin} routeDestination={routeDestination} /></div>{fallback && <span className="sr-only">MapLibre background is unavailable; the synthetic movement network remains visible.</span>}</div>;
}
