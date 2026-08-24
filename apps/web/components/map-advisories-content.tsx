"use client";

import { AlertCircle, ArrowUpRight, CheckCircle2, LoaderCircle, MapPinned, Route } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { RouteRiskMap } from "@/components/route-risk-map";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";
import { type Advisory, type Location, type Outbreak, type RouteAssessment, apiFetch } from "@/lib/api";
import { DataContextLabel } from "@/components/data-context-control";
import { sourcePath, useDataContext } from "@/lib/data-context";
import { DataSourceBadge } from "@/components/data-source-badge";
import { PilotGeographicMap } from "@/components/pilot-geographic-map";

export function MapAdvisoriesContent() {
  const { context } = useDataContext();
  const [advisories, setAdvisories] = useState<Advisory[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);
  const [selectedAdvisoryId, setSelectedAdvisoryId] = useState<number | null>(null);
  const [assessment, setAssessment] = useState<RouteAssessment | null>(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([apiFetch<Advisory[]>(sourcePath("/advisories", context)), apiFetch<Location[]>(sourcePath("/locations", context)), apiFetch<Outbreak[]>(sourcePath("/outbreaks", context))])
      .then(([loadedAdvisories, loadedLocations, loadedOutbreaks]) => {
        setAdvisories(loadedAdvisories);
        setLocations(loadedLocations);
        setOutbreaks(loadedOutbreaks);
        setSelectedAdvisoryId(loadedAdvisories[0]?.id ?? null);
        setState("ready");
      })
      .catch((reason: Error) => {
        setError(reason.message);
        setState("error");
      });
  }, [context]);

  useEffect(() => {
    const selected = advisories.find((advisory) => advisory.id === selectedAdvisoryId);
    if (!selected) {
      setAssessment(null);
      return;
    }
    let active = true;
    setRouteLoading(true);
    setAssessment(null);
    apiFetch<RouteAssessment[]>(`/consignments/${selected.consignment_id}/route-assessments`)
      .then(async (assessments) => { const item = assessments[0] ?? (selected.data_source === "pilot_entered" ? await apiFetch<RouteAssessment>("/routes/assess", { method: "POST", body: JSON.stringify({ consignment_id: selected.consignment_id }) }) : null); if (active) setAssessment(item); })
      .catch(() => { if (active) setAssessment(null); })
      .finally(() => { if (active) setRouteLoading(false); });
    return () => { active = false; };
  }, [advisories, selectedAdvisoryId]);

  if (state === "loading") return <section className="grid min-h-72 place-items-center rounded-xl border border-line bg-white"><div className="text-center"><LoaderCircle className="mx-auto animate-spin text-teal" /><p className="mt-3 text-sm font-semibold">Loading persisted synthetic map data…</p></div></section>;
  if (state === "error") return <section role="alert" className="rounded-xl border border-[#F1B7B2] bg-[#FDECEC] p-6"><AlertCircle className="text-risk-red" /><h2 className="mt-3 font-display text-2xl font-semibold">Map data could not be loaded.</h2><p className="mt-2 text-sm text-slate-700">Confirm that the local API is running, then refresh. Detail: {error}</p></section>;

  const selectedAdvisory = advisories.find((advisory) => advisory.id === selectedAdvisoryId) ?? null;
  const counts = { confirmed: outbreaks.filter((outbreak) => outbreak.status === "confirmed").length, suspected: outbreaks.filter((outbreak) => outbreak.status === "suspected").length };
  const advisoryCounts = ["green", "amber", "red", "grey"].map((risk) => ({ risk, count: advisories.filter((advisory) => advisory.risk_state === risk).length }));

  return <div className="space-y-6"><DataContextLabel />
    <section className="rounded-xl bg-ink p-6 text-white md:p-7"><p className="text-xs font-bold uppercase tracking-[0.15em] text-lime">Synthetic operations map</p><div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><h2 className="font-display text-3xl font-semibold tracking-tight">Outbreak context and movement advisories</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-white/75">Fictional persisted data only. No live INAPH, NADRES, IDSP, LGD, or government integration is connected. Results require authorised veterinary review.</p></div><div className="flex gap-3"><MapMetric value={counts.confirmed} label="Confirmed zones" /><MapMetric value={counts.suspected} label="Suspected zones" /></div></div></section>

    <Card className="p-5 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">{context === "pilot_entered" ? "Pilot Geographic View" : context === "all" ? "Separated data views" : "Synthetic movement network"}</p><h2 className="mt-2 font-display text-2xl font-semibold">{context === "pilot_entered" ? "Pilot geographic locations and routes" : "Outbreak context and assessed movement network"}</h2></div>{selectedAdvisory ? <Link href={`/advisories/${selectedAdvisory.id}`} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-[10px] bg-teal px-4 text-sm font-bold text-white hover:bg-[#0b625c]">View Safe Corridor <ArrowUpRight size={16} /></Link> : null}</div>
      {selectedAdvisory && <div className="mt-5 flex flex-col gap-3 rounded-xl border border-line bg-paper p-4 sm:flex-row sm:items-center sm:justify-between"><div className="flex items-start gap-3"><MapPinned className="mt-0.5 shrink-0 text-teal" size={19} aria-hidden="true" /><div><p className="text-sm font-bold text-ink">Displaying advisory route: {selectedAdvisory.consignment.origin_location.name} → {selectedAdvisory.consignment.destination_location.name}</p><p className="mt-1 text-sm text-slate-600">Latest route assessment for this persisted synthetic consignment.</p></div></div><StatusBadge state={selectedAdvisory.risk_state} label={`${selectedAdvisory.risk_state.toUpperCase()} — veterinary review required`} /></div>}
      <p className="mt-4 text-sm leading-6 text-slate-600">This network shows recorded synthetic location relationships, not real road navigation.</p>
      <div className="mt-5">{context === "all" ? <EmptyState title="Choose a data source view" description="Select Demo data or Pilot records in the Data Context control before displaying a map. Demo and pilot geography are intentionally kept separate." /> : !locations.length ? <EmptyState title="No map locations available" description="No active locations are available in this data context." /> : context === "pilot_entered" ? <PilotGeographicMap locations={locations} outbreaks={outbreaks} assessment={assessment} /> : <RouteRiskMap assessment={assessment ?? undefined} locations={locations} outbreaks={outbreaks} routeOrigin={selectedAdvisory?.consignment.origin_location} routeDestination={selectedAdvisory?.consignment.destination_location} />}</div>
      {routeLoading && <p className="mt-3 text-sm font-semibold text-slate-600">Loading the selected assessed route…</p>}
      {!routeLoading && selectedAdvisory && !assessment && <p className="mt-3 text-sm font-semibold text-slate-600">No persisted route assessment is available for the selected advisory.</p>}
      {!selectedAdvisory && <p className="mt-3 text-sm font-semibold text-slate-600">Select a recent advisory to display its persisted assessed movement route.</p>}
      <ul className="mt-4 grid gap-2 text-sm font-semibold text-slate-700 sm:grid-cols-2" aria-label="Map legend"><li>Teal node = fictional location</li><li>Red zone = confirmed outbreak record</li><li>Amber zone = suspected outbreak record</li><li>Dashed slate line = assessed movement route</li><li>Solid teal line = safer route when available</li></ul>
      <p className="mt-3 text-sm leading-6 text-slate-600">The controlled route display supports veterinary review. It is not navigation, a movement permit, or a legal restriction.</p>
    </Card>

    <section className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
      <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Advisory totals</p><h2 className="mt-2 font-display text-2xl font-semibold">Evaluated movement results</h2><div className="mt-5 grid grid-cols-2 gap-3">{advisoryCounts.map(({ risk, count }) => <div key={risk} className="rounded-lg border border-line bg-paper p-3"><StatusBadge state={risk as Advisory["risk_state"]} label={risk.toUpperCase()} /><p className="mt-3 font-display text-3xl font-semibold">{count}</p></div>)}</div></Card>
      <Card className="p-5 md:p-6"><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Recent advisories</p><h2 className="mt-2 font-display text-2xl font-semibold">Select a route to display</h2></div><Route className="text-teal" aria-hidden="true" /></div>{advisories.length === 0 ? <div className="mt-5"><EmptyState title="No evaluated consignments yet" description="Register and evaluate a record in this data context to view its advisory and route assessment." /></div> : <div className="mt-5 space-y-2">{advisories.slice(0, 5).map((advisory) => { const selected = advisory.id === selectedAdvisoryId; return <button type="button" aria-pressed={selected} onClick={() => setSelectedAdvisoryId(advisory.id)} key={advisory.id} className={`flex w-full items-center justify-between gap-3 rounded-xl border p-3 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal ${selected ? "border-2 border-teal bg-paper" : "border-line hover:bg-paper"}`}><div className="flex min-w-0 items-start gap-2"><CheckCircle2 className={selected ? "mt-0.5 shrink-0 text-teal" : "mt-0.5 shrink-0 text-slate-400"} size={17} aria-hidden="true" /><div><p className="text-sm font-bold text-ink">{advisory.consignment.origin_location.name} → {advisory.consignment.destination_location.name}</p><p className="mt-1 text-sm text-slate-600">{advisory.consignment.species} · {advisory.consignment.animal_count} animals</p>{context === "all" && <span className="mt-2 inline-block"><DataSourceBadge source={advisory.data_source} /></span>}{selected && <p className="mt-2 text-xs font-bold text-teal">Selected route on map</p>}</div></div><StatusBadge state={advisory.risk_state} label={advisory.risk_state.toUpperCase()} /></button>; })}</div>}</Card>
    </section>
  </div>;
}

function MapMetric({ value, label }: { value: number; label: string }) { return <div className="rounded-lg border border-white/15 bg-white/5 px-4 py-3"><p className="font-display text-2xl font-semibold">{value}</p><p className="text-xs font-semibold text-white/70">{label}</p></div>; }
