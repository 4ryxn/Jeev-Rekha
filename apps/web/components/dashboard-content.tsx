"use client";

import { Activity, AlertCircle, ArrowUpRight, ClipboardCheck, LoaderCircle, MapPinned, ShieldAlert, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { type Advisory, type Consignment, type Outbreak, apiFetch } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";
import { ReviewActivity } from "@/components/review-activity";
import { ReportActivity } from "@/components/report-activity";

type LoadState = "loading" | "ready" | "error";

export function DashboardContent() {
  const [state, setState] = useState<LoadState>("loading");
  const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);
  const [consignments, setConsignments] = useState<Consignment[]>([]);
  const [advisories, setAdvisories] = useState<Advisory[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([apiFetch<Outbreak[]>("/outbreaks"), apiFetch<Consignment[]>("/consignments"), apiFetch<Advisory[]>("/advisories")])
      .then(([loadedOutbreaks, loadedConsignments, loadedAdvisories]) => { setOutbreaks(loadedOutbreaks); setConsignments(loadedConsignments); setAdvisories(loadedAdvisories); setState("ready"); })
      .catch((reason: Error) => { setError(reason.message); setState("error"); });
  }, []);

  if (state === "loading") return <LoadingDashboard />;
  if (state === "error") return <ApiError message={error} />;

  const counts = { confirmed: outbreaks.filter((item) => item.status === "confirmed").length, suspected: outbreaks.filter((item) => item.status === "suspected").length, closed: outbreaks.filter((item) => item.status === "closed").length };
  const advisoryCounts = { green: advisories.filter((item) => item.risk_state === "green").length, amber: advisories.filter((item) => item.risk_state === "amber").length, red: advisories.filter((item) => item.risk_state === "red").length, grey: advisories.filter((item) => item.risk_state === "grey").length };
  return <div className="space-y-8">
    <section aria-label="Outbreak summary" className="overflow-hidden rounded-xl bg-ink text-white"><div className="grid gap-6 px-6 py-7 lg:grid-cols-[1.1fr_1.9fr] lg:items-center lg:px-8"><div><p className="text-xs font-bold uppercase tracking-[0.15em] text-lime">Synthetic operations data</p><h2 className="mt-3 font-display text-3xl font-semibold leading-tight tracking-[-0.04em]">{counts.confirmed + counts.suspected} active outbreak{counts.confirmed + counts.suspected === 1 ? "" : "s"} require attention.</h2><p className="mt-3 max-w-sm text-sm leading-6 text-white/70">Fictional records for demonstration only. No live government or disease-surveillance feed is connected.</p></div><div className="grid gap-3 sm:grid-cols-3"><Metric value={counts.confirmed} label="confirmed" tone="border-[#B42318]" /><Metric value={counts.suspected} label="suspected" tone="border-[#B45309]" /><Metric value={counts.closed} label="closed" tone="border-slate-400" /></div></div></section>
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,0.85fr)]"><Card className="overflow-hidden"><div className="flex items-start justify-between gap-4 border-b border-line p-5 md:p-6"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Outbreak register</p><h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Recent outbreak records</h2></div><Link href="/register/outbreak" className="inline-flex min-h-11 items-center gap-1 text-sm font-bold text-teal hover:underline">Record outbreak <ArrowUpRight size={16} /></Link></div>{outbreaks.length === 0 ? <div className="p-6"><EmptyState title="No outbreak records yet" description="Create a synthetic outbreak record to begin the operations view." /></div> : <div className="divide-y divide-line">{outbreaks.slice(0, 4).map((outbreak) => <article className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between" key={outbreak.id}><div><p className="font-bold text-ink">{outbreak.disease_name} <span className="font-normal text-slate-500">· {outbreak.species}</span></p><p className="mt-1 text-sm text-slate-600">{outbreak.location.name} · detected {formatDate(outbreak.detected_at)}</p></div><OutbreakStatusLabel status={outbreak.status} /></article>)}</div>}</Card><Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Movement advisories</p><h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Evaluated results</h2><div className="mt-6 grid grid-cols-2 gap-3"><AdvisoryMetric state="green" value={advisoryCounts.green} /><AdvisoryMetric state="amber" value={advisoryCounts.amber} /><AdvisoryMetric state="red" value={advisoryCounts.red} /><AdvisoryMetric state="grey" value={advisoryCounts.grey} /></div><p className="mt-5 text-sm leading-6 text-slate-600">Each result includes visible reasons, a coverage score, and a recommended action.</p></Card></div>
    <section className="grid gap-6 lg:grid-cols-2 xl:grid-cols-4"><Card className="p-5 md:p-6"><div className="flex items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Recent evaluated consignments</p><h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Open an advisory</h2></div><Link href="/register/consignment" aria-label="Register consignment" className="rounded-lg p-2 text-teal hover:bg-teal/10"><ArrowUpRight aria-hidden="true" /></Link></div>{advisories.length === 0 ? <p className="mt-5 text-sm leading-6 text-slate-600">No consignments have been evaluated.</p> : <div className="mt-5 divide-y divide-line">{advisories.slice(0, 4).map((item) => <Link className="flex items-center justify-between gap-3 py-3 hover:bg-paper" href={`/advisories/${item.id}`} key={item.id}><div><p className="text-sm font-bold">{item.consignment.species} · {item.consignment.animal_count} animals</p><p className="mt-1 text-sm text-slate-600">{item.consignment.origin_location.name} → {item.consignment.destination_location.name}</p></div><StatusBadge state={item.risk_state} label={item.risk_state.toUpperCase()} /></Link>)}</div>}</Card><Card className="p-5 md:p-6"><div className="flex items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Map & advisories</p><h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Evidence first</h2></div><MapPinned className="text-ink/40" aria-hidden="true" /></div><p className="mt-4 text-sm leading-6 text-slate-600">Risk status reflects persisted synthetic outbreak and evidence records. Review outbreak zones, advisory records, and controlled route context in one operational view.</p><Link href="/map" className="mt-5 inline-flex min-h-11 items-center font-semibold text-teal hover:underline">Open Map & Advisories <ArrowUpRight className="ml-1" size={16} /></Link></Card><ReviewActivity/><ReportActivity/></section>
  </div>;
}

function Metric({ value, label, tone }: { value: number; label: string; tone: string }) { return <div className={`rounded-lg border-l-4 bg-white/5 p-4 ${tone}`}><p className="font-display text-4xl font-semibold">{value}</p><p className="mt-1 text-sm capitalize text-white/70">{label}</p></div>; }
function AdvisoryMetric({ state, value }: { state: Advisory["risk_state"]; value: number }) { return <div className="rounded-lg border border-line bg-paper p-3"><StatusBadge state={state} label={state.toUpperCase()} /><p className="mt-3 font-display text-3xl font-semibold">{value}</p></div>; }
function OutbreakStatusLabel({ status }: { status: Outbreak["status"] }) { const labels = { confirmed: ["red", "Confirmed"], suspected: ["amber", "Suspected"], closed: ["grey", "Closed"] } as const; const [state, label] = labels[status]; return <StatusBadge state={state} label={label} />; }
function Priority({ icon: Icon, title, detail, tone }: { icon: typeof ShieldAlert; title: string; detail: string; tone: string }) { return <article className="flex gap-3 border-b border-line pb-4 last:border-0 last:pb-0"><span className={`mt-0.5 ${tone}`}><Icon size={19} aria-hidden="true" /></span><div><h3 className="text-sm font-bold text-ink">{title}</h3><p className="mt-1 text-sm leading-5 text-slate-600">{detail}</p></div></article>; }
function LoadingDashboard() { return <div className="grid min-h-[440px] place-items-center rounded-xl border border-line bg-white"><div className="text-center"><LoaderCircle className="mx-auto animate-spin text-teal" aria-hidden="true" /><p className="mt-4 text-sm font-semibold">Loading synthetic operations data…</p></div></div>; }
function ApiError({ message }: { message: string }) { return <section role="alert" className="rounded-xl border border-[#F1B7B2] bg-[#FDECEC] p-6"><AlertCircle className="text-risk-red" aria-hidden="true" /><h2 className="mt-3 font-display text-2xl font-semibold">The operations data could not be loaded.</h2><p className="mt-2 text-sm leading-6 text-slate-700">Confirm that the FastAPI service is running on port 8000, then refresh this page. Technical detail: {message}</p></section>; }
function formatDate(value: string) { return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(value)); }
