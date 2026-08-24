"use client";

import { useEffect, useState } from "react";

import { RouteRiskMap } from "@/components/route-risk-map";
import { PilotGeographicMap } from "@/components/pilot-geographic-map";
import { PilotAdvisoryEvidence } from "@/components/pilot-advisory-evidence";
import { Card } from "@/components/ui/card";
import { apiFetch, type Advisory, type Location, type Outbreak, type RouteAssessment } from "@/lib/api";

export function SafeCorridor({ advisory }: { advisory: Advisory }) {
  const [assessment, setAssessment] = useState<RouteAssessment | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      apiFetch<RouteAssessment>("/routes/assess", { method: "POST", body: JSON.stringify({ consignment_id: advisory.consignment_id }) }),
      apiFetch<Location[]>("/locations"),
      apiFetch<Outbreak[]>("/outbreaks"),
    ]).then(([loadedAssessment, loadedLocations, loadedOutbreaks]) => {
      setAssessment(loadedAssessment);
      setLocations(loadedLocations);
      setOutbreaks(loadedOutbreaks);
    }).catch((reason: Error) => setError(reason.message));
  }, [advisory.consignment_id]);

  if (error) return <Card className="p-5">Route assessment unavailable: {error}</Card>;
  if (!assessment) return <Card className="p-5">Loading route assessment…</Card>;
  if (advisory.data_source === "pilot_entered") return <section className="space-y-5"><h3 className="font-display text-3xl font-semibold">Pilot road-route display</h3><PilotGeographicMap assessment={assessment} locations={locations.filter(x => x.data_source === "pilot_entered")} outbreaks={outbreaks.filter(x => x.data_source === "pilot_entered")} /><Card className="p-5"><h4 className="font-bold">Informational route</h4><p className="mt-3">{assessment.route_geometry ? `${assessment.preferred_distance_km} km · ${assessment.preferred_minutes} min` : `${assessment.preferred_distance_km} km direct geographic distance`}</p><p className="mt-2 text-sm text-slate-600">{assessment.route_fallback_reason ?? "Road route is based on the configured provider and is not navigation guidance."}</p></Card><p className="rounded-lg border border-line bg-white p-4 text-sm font-semibold">Route advice is decision support only. It is not a legal movement permit.</p></section>;

  return <section className="space-y-5"><h3 className="font-display text-3xl font-semibold">Safe Corridor</h3><RouteRiskMap assessment={assessment} locations={locations} outbreaks={outbreaks} routeOrigin={advisory.consignment.origin_location} routeDestination={advisory.consignment.destination_location} /><p className="text-xs font-bold">Legend: Teal node = fictional location · Red zone = confirmed outbreak record · Amber zone = suspected outbreak record · Dashed slate line = assessed movement route · Solid teal line = safer route when available.</p><div className="grid gap-4 md:grid-cols-2"><Card className="p-5"><h4 className="font-bold">Your requested route</h4><p className="mt-3">{assessment.preferred_distance_km} km · {assessment.preferred_minutes} min</p><p className="mt-2 text-sm text-slate-600">{assessment.route_reasons[0]}</p></Card><Card className="p-5"><h4 className="font-bold">{assessment.safer_route ? "Safer alternative" : "No safer route"}</h4>{assessment.safer_route ? <><p className="mt-3">{assessment.safer_distance_km} km · {assessment.safer_minutes} min</p><p className="mt-2 text-sm">Added: {(assessment.safer_distance_km! - assessment.preferred_distance_km).toFixed(1)} km · {assessment.safer_minutes! - assessment.preferred_minutes} min · Risk: {assessment.risk_reduction}</p></> : <p className="mt-3 text-sm">No safer route is currently available. Authorised veterinary guidance is required.</p>}</Card></div><p className="text-sm text-slate-700">Text route summary: {assessment.route_reasons.join(" ")}</p><p className="rounded-lg border border-line bg-white p-4 text-sm font-semibold">Route advice is decision support only. It is not a legal movement permit.</p></section>;
}

export function SafeCorridorByAdvisory({ id }: { id: number }) {
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Advisory>(`/advisories/${id}`).then(setAdvisory).catch((reason: Error) => setError(reason.message));
  }, [id]);

  if (error) return <Card className="p-5">Route assessment unavailable: {error}</Card>;
  if (!advisory) return <Card className="p-5">Loading synthetic movement network and assessment…</Card>;
  return <>{advisory.data_source === "pilot_entered" && <PilotAdvisoryEvidence advisory={advisory} />}<SafeCorridor advisory={advisory} /></>;
}
