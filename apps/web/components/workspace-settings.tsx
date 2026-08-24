"use client";

import { CheckCircle2, Settings2, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { LocationRegistry } from "@/components/location-registry";

type Health = "loading" | "healthy" | "unavailable";
type MapMode = "controlled" | "enhanced";

function applyPreferences(reducedMotion: boolean, mapPresentation: MapMode) {
  document.documentElement.dataset.reducedMotion = String(reducedMotion);
  document.documentElement.dataset.mapPresentation = mapPresentation;
  localStorage.setItem("jeevrekha-reduced-motion", String(reducedMotion));
  localStorage.setItem("jeevrekha-map-presentation", mapPresentation);
}

export function WorkspaceSettings() {
  const [health, setHealth] = useState<Health>("loading");
  const [reducedMotion, setReducedMotion] = useState(false);
  const [mapPresentation, setMapPresentation] = useState<MapMode>("enhanced");

  useEffect(() => {
    const storedMotion = localStorage.getItem("jeevrekha-reduced-motion") === "true";
    const storedMap = (localStorage.getItem("jeevrekha-map-presentation") as MapMode) || "enhanced";
    setReducedMotion(storedMotion); setMapPresentation(storedMap); applyPreferences(storedMotion, storedMap);
    apiFetch<{ status: string }>("/health").then((value) => setHealth(value.status === "ok" ? "healthy" : "unavailable")).catch(() => setHealth("unavailable"));
  }, []);

  const update = (motion: boolean, map: MapMode) => { setReducedMotion(motion); setMapPresentation(map); applyPreferences(motion, map); };
  return <div className="space-y-6">
    <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Workspace status</p><h2 className="mt-2 font-display text-2xl font-semibold">Local synthetic demonstration</h2><div className="mt-5 grid gap-3 md:grid-cols-2"><Status icon={Settings2} label="Data mode" detail="Fictional synthetic records only" good /><Status icon={health === "healthy" ? CheckCircle2 : TriangleAlert} label="API health" detail={health === "loading" ? "Checking local API…" : health === "healthy" ? "Healthy local service" : "Local API unavailable"} good={health === "healthy"} /></div><p className="mt-5 text-sm leading-6 text-slate-700">No live government integration is connected. INAPH, NADRES, IDSP, LGD, and other government systems are not linked.</p></Card>
    <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Local-device display preferences</p><h2 className="mt-2 font-display text-2xl font-semibold">Presentation</h2><p className="mt-2 text-sm text-slate-600">These preferences are saved only in this browser on this device.</p><div className="mt-5 grid gap-4 md:grid-cols-2"><label className="rounded-lg border border-line p-4"><span className="font-bold">Reduced motion</span><select value={reducedMotion ? "on" : "off"} onChange={(event) => update(event.target.value === "on", mapPresentation)} className="mt-3 block min-h-11 w-full rounded border border-line bg-white px-3"><option value="off">Off</option><option value="on">On</option></select><span className="mt-2 block text-xs text-slate-600">Stops non-essential motion immediately.</span></label><label className="rounded-lg border border-line p-4"><span className="font-bold">Map presentation</span><select value={mapPresentation} onChange={(event) => update(reducedMotion, event.target.value as MapMode)} className="mt-3 block min-h-11 w-full rounded border border-line bg-white px-3"><option value="controlled">Synthetic movement network</option><option value="enhanced">Enhanced map background</option></select><span className="mt-2 block text-xs text-slate-600">The synthetic movement network remains the operational data layer in both modes.</span></label></div></Card>
    <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Offline and PWA information</p><h2 className="mt-2 font-display text-2xl font-semibold">Device queue safety</h2><p className="mt-3 text-sm leading-6 text-slate-700">Offline records remain on this device until a successful sync is confirmed. Device sync exceptions are separate from Review Queue cases. Use Device sync in the top bar to review local queue status.</p><Link className="mt-4 inline-block font-bold text-teal underline" href="/register">Open Register</Link></Card>
    <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Data boundaries</p><h2 className="mt-2 font-display text-2xl font-semibold">Decision support only</h2><p className="mt-3 text-sm leading-6 text-slate-700">Advisories, traces, Safe Corridor, containment scenarios, and review decisions support authorised veterinary review. They do not issue permits, legal restrictions, or automatic decisions.</p><p className="mt-3 text-sm font-semibold">Demo data is controlled fictional data for the SIH demonstration. Pilot-entered data is manually maintained by authorised local operations staff. Neither source is imported from INAPH, NADRES, IDSP, LGD, or another government platform.</p></Card>
    <LocationRegistry />
  </div>;
}

function Status({ icon: Icon, label, detail, good }: { icon: typeof CheckCircle2; label: string; detail: string; good: boolean }) {
  return <div className="flex gap-3 rounded-lg border border-line bg-paper p-4"><Icon className={good ? "text-teal" : "text-risk-amber"} aria-hidden="true" /><div><p className="font-bold">{label}</p><p className="text-sm text-slate-600">{detail}</p></div></div>;
}
