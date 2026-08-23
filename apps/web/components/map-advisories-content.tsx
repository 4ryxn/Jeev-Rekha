"use client";

import { AlertCircle, ArrowUpRight, LoaderCircle, MapPinned, Route } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { RouteRiskMap } from "@/components/route-risk-map";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";
import { type Advisory, type Location, type Outbreak, type RouteAssessment, apiFetch } from "@/lib/api";

export function MapAdvisoriesContent() {
  const [advisories, setAdvisories] = useState<Advisory[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);
  const [assessment, setAssessment] = useState<RouteAssessment | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([apiFetch<Advisory[]>("/advisories"), apiFetch<Location[]>("/locations"), apiFetch<Outbreak[]>("/outbreaks")])
      .then(async ([loadedAdvisories, loadedLocations, loadedOutbreaks]) => {
        setAdvisories(loadedAdvisories); setLocations(loadedLocations); setOutbreaks(loadedOutbreaks);
        if (loadedAdvisories[0]) {
          const existingAssessments = await apiFetch<RouteAssessment[]>(`/consignments/${loadedAdvisories[0].consignment_id}/route-assessments`);
          setAssessment(existingAssessments[0] ?? null);
        }
        setState("ready");
      })
      .catch((reason: Error) => { setError(reason.message); setState("error"); });
  }, []);

  if (state === "loading") return <section className="grid min-h-72 place-items-center rounded-xl border border-line bg-white"><div className="text-center"><LoaderCircle className="mx-auto animate-spin text-teal" /><p className="mt-3 text-sm font-semibold">Loading persisted synthetic map data…</p></div></section>;
  if (state === "error") return <section role="alert" className="rounded-xl border border-[#F1B7B2] bg-[#FDECEC] p-6"><AlertCircle className="text-risk-red" /><h2 className="mt-3 font-display text-2xl font-semibold">Map data could not be loaded.</h2><p className="mt-2 text-sm text-slate-700">Confirm that the local API is running, then refresh. Detail: {error}</p></section>;

  const counts = { confirmed: outbreaks.filter((outbreak) => outbreak.status === "confirmed").length, suspected: outbreaks.filter((outbreak) => outbreak.status === "suspected").length };
  const advisoryCounts = ["green", "amber", "red", "grey"].map((risk) => ({ risk, count: advisories.filter((advisory) => advisory.risk_state === risk).length }));
  return <div className="space-y-6">
    <section className="rounded-xl bg-ink p-6 text-white md:p-7"><p className="text-xs font-bold uppercase tracking-[0.15em] text-lime">Synthetic operations map</p><div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><h2 className="font-display text-3xl font-semibold tracking-tight">Outbreak context and movement advisories</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-white/75">Fictional persisted data only. No live INAPH, NADRES, IDSP, LGD, or government integration is connected. Results require authorised veterinary review.</p></div><div className="flex gap-3"><MapMetric value={counts.confirmed} label="Confirmed zones" /><MapMetric value={counts.suspected} label="Suspected zones" /></div></div></section>
    <Card className="p-5 md:p-6"><div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Controlled synthetic map</p><h2 className="mt-2 font-display text-2xl font-semibold">Active outbreak zones and latest route</h2></div>{advisories[0] ? <Link href={`/advisories/${advisories[0].id}`} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-[10px] bg-teal px-4 text-sm font-bold text-white hover:bg-[#0b625c]">View Safe Corridor <ArrowUpRight size={16} /></Link> : null}</div><div className="mt-5">{locations.length ? <RouteRiskMap assessment={assessment ?? undefined} locations={locations} outbreaks={outbreaks} /> : <EmptyState title="No map locations available" description="The local synthetic location dataset has not been seeded." />}</div><p className="mt-3 text-sm font-semibold text-slate-700">Legend: Teal marker = fictional location · Red zone = confirmed outbreak record · Amber zone = suspected outbreak record · Red line = requested route · Teal line = safer route when available.</p><p className="mt-2 text-sm leading-6 text-slate-600">The controlled route display supports veterinary review. It is not navigation, a movement permit, or a legal restriction.</p></Card>
    <section className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]"><Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Advisory totals</p><h2 className="mt-2 font-display text-2xl font-semibold">Evaluated movement results</h2><div className="mt-5 grid grid-cols-2 gap-3">{advisoryCounts.map(({ risk, count }) => <div key={risk} className="rounded-lg border border-line bg-paper p-3"><StatusBadge state={risk as Advisory["risk_state"]} label={risk.toUpperCase()} /><p className="mt-3 font-display text-3xl font-semibold">{count}</p></div>)}</div></Card><Card className="p-5 md:p-6"><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Recent advisories</p><h2 className="mt-2 font-display text-2xl font-semibold">Open an evidence record</h2></div><Route className="text-teal" aria-hidden="true" /></div>{advisories.length === 0 ? <div className="mt-5"><EmptyState title="No evaluated consignments yet" description="Register and evaluate a synthetic consignment to view its advisory and route assessment." /></div> : <div className="mt-5 divide-y divide-line">{advisories.slice(0, 5).map((advisory) => <Link key={advisory.id} href={`/advisories/${advisory.id}`} className="flex items-center justify-between gap-3 py-3 hover:bg-paper"><div><p className="text-sm font-bold text-ink">{advisory.consignment.origin_location.name} → {advisory.consignment.destination_location.name}</p><p className="mt-1 text-sm text-slate-600">{advisory.consignment.species} · {advisory.consignment.animal_count} animals</p></div><StatusBadge state={advisory.risk_state} label={advisory.risk_state.toUpperCase()} /></Link>)}</div>}</Card></section>
  </div>;
}

function MapMetric({ value, label }: { value: number; label: string }) { return <div className="rounded-lg border border-white/15 bg-white/5 px-4 py-3"><p className="font-display text-2xl font-semibold">{value}</p><p className="text-xs font-semibold text-white/70">{label}</p></div>; }
