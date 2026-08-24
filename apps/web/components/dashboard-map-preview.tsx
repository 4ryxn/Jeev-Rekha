"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { RouteRiskMap } from "@/components/route-risk-map";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { apiFetch, type Advisory, type Location, type Outbreak, type RouteAssessment } from "@/lib/api";

export function DashboardMapPreview() {
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [assessment, setAssessment] = useState<RouteAssessment | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);

  useEffect(() => {
    Promise.all([apiFetch<Advisory[]>("/advisories"), apiFetch<Location[]>("/locations"), apiFetch<Outbreak[]>("/outbreaks")]).then(([advisories, loadedLocations, loadedOutbreaks]) => {
      setAdvisory(advisories[0] ?? null);
      setLocations(loadedLocations);
      setOutbreaks(loadedOutbreaks);
      if (advisories[0]) apiFetch<RouteAssessment>("/routes/assess", { method: "POST", body: JSON.stringify({ consignment_id: advisories[0].consignment_id }) }).then(setAssessment);
    });
  }, []);

  if (!advisory) return <EmptyState title="No evaluated route yet" description="Evaluate a consignment to see its persisted route assessment here." />;

  return <Card className="p-5 md:p-6"><div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-wider text-teal">Synthetic movement network</p><h2 className="mt-2 font-display text-2xl font-semibold">Latest evaluated route</h2></div><Link href={`/advisories/${advisory.id}`} className="min-h-11 rounded-[10px] bg-teal px-4 py-3 text-sm font-bold text-white">View route assessment</Link></div>{assessment ? <div className="mt-5"><RouteRiskMap assessment={assessment} locations={locations} outbreaks={outbreaks} routeOrigin={advisory.consignment.origin_location} routeDestination={advisory.consignment.destination_location} /><p className="mt-3 text-xs font-bold">Legend: Teal node = fictional location · Red zone = confirmed outbreak record · Amber zone = suspected outbreak record · Dashed slate line = assessed movement route · Solid teal line = safer route when available.</p></div> : <p className="mt-5 text-sm">Loading latest assessed movement network…</p>}</Card>;
}
