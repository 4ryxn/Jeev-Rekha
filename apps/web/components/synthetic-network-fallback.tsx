"use client";

import type { Location, Outbreak } from "@/lib/api";

export type NetworkLine = { coordinates: number[][]; color: string; label: string; dasharray?: number[] };
type Point = { x: number; y: number };

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

export function SyntheticNetworkFallback({
  locations,
  outbreaks,
  lines = [],
  origin,
  impacted = [],
  routeOrigin,
  routeDestination,
}: {
  locations: Location[];
  outbreaks: Outbreak[];
  lines?: NetworkLine[];
  origin?: Location;
  impacted?: Location[];
  routeOrigin?: Location;
  routeDestination?: Location;
}) {
  const allLocations = Array.from(new Map([...locations, ...(origin ? [origin] : []), ...impacted, ...(routeOrigin ? [routeOrigin] : []), ...(routeDestination ? [routeDestination] : [])].map((location) => [location.id, location])).values());
  const coordinates = [...allLocations.map((location) => [location.longitude, location.latitude] as const), ...lines.flatMap((line) => line.coordinates.map(([longitude, latitude]) => [longitude, latitude] as const))];
  const longitudes = coordinates.map(([longitude]) => longitude);
  const latitudes = coordinates.map(([, latitude]) => latitude);
  const minLon = Math.min(...longitudes, 77.48);
  const maxLon = Math.max(...longitudes, 77.56);
  const minLat = Math.min(...latitudes, 12.94);
  const maxLat = Math.max(...latitudes, 13.06);
  const project = ([longitude, latitude]: readonly number[]): Point => ({
    x: 16 + 148 * (longitude - minLon) / (maxLon - minLon || 1),
    y: 84 - 68 * (latitude - minLat) / (maxLat - minLat || 1),
  });
  const activeOutbreaks = outbreaks.filter((outbreak) => outbreak.status !== "closed");
  const outbreakStatusByLocation = new Map<number, "confirmed" | "suspected">();
  activeOutbreaks.forEach((outbreak) => {
    const current = outbreakStatusByLocation.get(outbreak.location_id);
    outbreakStatusByLocation.set(outbreak.location_id, current === "confirmed" || outbreak.status === "confirmed" ? "confirmed" : "suspected");
  });
  const impactedIds = new Set(impacted.map((location) => location.id));
  const labelLocations = new Map<number, Location>();
  activeOutbreaks.forEach((outbreak) => labelLocations.set(outbreak.location.id, outbreak.location));
  if (routeOrigin) labelLocations.set(routeOrigin.id, routeOrigin);
  if (routeDestination) labelLocations.set(routeDestination.id, routeDestination);

  const curvedPath = (line: NetworkLine) => {
    const points = line.coordinates.map(project);
    if (points.length < 2) return "";
    const offset = line.label === "Safer route" ? -7 : 7;
    return points.slice(1).reduce((path, end, pointIndex) => {
      const start = points[pointIndex];
      const midpoint = { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 };
      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const length = Math.hypot(dx, dy) || 1;
      const direction = pointIndex % 2 === 0 ? 1 : -1;
      const control = {
        x: clamp(midpoint.x - direction * offset * dy / length, 8, 172),
        y: clamp(midpoint.y + direction * offset * dx / length, 8, 92),
      };
      return `${path} Q ${control.x} ${control.y} ${end.x} ${end.y}`;
    }, `M ${points[0].x} ${points[0].y}`);
  };

  return <div className="relative h-72 overflow-hidden rounded-xl border border-line bg-[#10231f]" role="img" aria-label="Synthetic movement network using persisted fictional location and route relationships, not real road navigation">
    <svg viewBox="0 0 180 100" preserveAspectRatio="xMidYMid meet" className="h-full w-full">
      <defs>
        <pattern id="network-grid" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M 8 0 L 0 0 0 8" fill="none" stroke="#d9f4ea" strokeOpacity=".08" strokeWidth=".4" /><circle cx="4" cy="4" r=".45" fill="#d9f4ea" fillOpacity=".12" /></pattern>
      </defs>
      <rect width="180" height="100" fill="#10231f" />
      <rect width="180" height="100" fill="url(#network-grid)" />
      {activeOutbreaks.map((outbreak) => {
        const point = project([outbreak.location.longitude, outbreak.location.latitude]);
        return <circle key={`zone-${outbreak.id}`} cx={point.x} cy={point.y} r="8" fill={outbreak.status === "confirmed" ? "#b42318" : "#b45309"} fillOpacity=".18" stroke={outbreak.status === "confirmed" ? "#ef8379" : "#f2bd77"} strokeOpacity=".55" strokeWidth=".7" />;
      })}
      {lines.map((line, index) => <path key={`${line.label}-${index}`} d={curvedPath(line)} fill="none" stroke={line.color} strokeWidth="2.2" strokeOpacity=".95" strokeDasharray={line.dasharray?.join(" ")} strokeLinecap="round" vectorEffect="non-scaling-stroke" />)}
      {allLocations.map((location) => {
        const point = project([location.longitude, location.latitude]);
        const outbreakStatus = outbreakStatusByLocation.get(location.id);
        const fill = origin?.id === location.id || outbreakStatus === "confirmed" ? "#b42318" : impactedIds.has(location.id) || outbreakStatus === "suspected" ? "#b45309" : "#0f8b8d";
        const selected = routeOrigin?.id === location.id || routeDestination?.id === location.id;
        return <circle key={`location-${location.id}`} cx={point.x} cy={point.y} r={selected || outbreakStatus || origin?.id === location.id || impactedIds.has(location.id) ? "3.1" : "1.8"} fill={fill} stroke={selected ? "#f8fafc" : "#c8f2ea"} strokeWidth={selected ? "1.2" : ".55"} vectorEffect="non-scaling-stroke" />;
      })}
      {Array.from(labelLocations.values()).map((location, index) => {
        const point = project([location.longitude, location.latitude]);
        const width = clamp(location.name.length * 1.75 + 6, 17, 46);
        const x = clamp(point.x > 118 ? point.x - width - 4 : point.x + 4, 3, 177 - width);
        const y = clamp(point.y + (index % 2 === 0 ? -9 : 5), 4, 93);
        return <g key={`label-${location.id}`}><rect x={x} y={y} width={width} height="5.5" rx="1.5" fill="#f8fafc" fillOpacity=".96" /><text x={x + 2.3} y={y + 3.7} fill="#172033" fontSize="2.55" fontWeight="700">{location.name}</text></g>;
      })}
    </svg>
    <p className="absolute left-3 top-3 rounded bg-white/90 px-2 py-1 text-xs font-bold text-ink">Synthetic movement network</p>
  </div>;
}
