"use client";

import { AlertCircle, ArrowRight, CalendarDays, CircleDot, Clock3, LoaderCircle, MapPinned, RotateCcw, Route, ShieldAlert, Stethoscope } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { TraceInvestigationMap } from "@/components/trace-investigation-map";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";
import { type Outbreak, type TraceConfiguration, type TraceDirection, type TraceRun, apiFetch } from "@/lib/api";
import { DataContextLabel } from "@/components/data-context-control";
import { sourcePath, useDataContext } from "@/lib/data-context";

export function TraceLab() {
  const { context } = useDataContext();
  const searchParams = useSearchParams();
  const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);
  const [selectedOutbreakId, setSelectedOutbreakId] = useState<number | null>(null);
  const [configuration, setConfiguration] = useState<TraceConfiguration | null>(null);
  const [trace, setTrace] = useState<TraceRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<TraceDirection | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const traceId = searchParams.get("traceId");
    Promise.all([apiFetch<Outbreak[]>(sourcePath("/outbreaks", context)), traceId ? apiFetch<TraceRun>(`/traces/${traceId}`) : Promise.resolve(null)])
      .then(([records, existingTrace]) => {
        const confirmed = records.filter((record) => record.status === "confirmed");
        setOutbreaks(confirmed);
        if (existingTrace) {
          setTrace(existingTrace);
          setSelectedOutbreakId(existingTrace.outbreak.id);
          setConfiguration({ disease_name: existingTrace.outbreak.disease_name, review_window_days: existingTrace.review_window_days, source_label: existingTrace.source_label });
        } else if (confirmed[0]) setSelectedOutbreakId(confirmed[0].id);
      })
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
  }, [searchParams, context]);

  useEffect(() => {
    if (!selectedOutbreakId || trace?.outbreak.id === selectedOutbreakId) return;
    setConfiguration(null);
    apiFetch<TraceConfiguration>(`/outbreaks/${selectedOutbreakId}/trace-configuration`)
      .then(setConfiguration)
      .catch((reason: Error) => setError(reason.message));
  }, [selectedOutbreakId, trace]);

  async function execute(direction: TraceDirection) {
    if (!selectedOutbreakId) return;
    setError(""); setRunning(direction);
    try {
      const result = await apiFetch<TraceRun>(`/outbreaks/${selectedOutbreakId}/traces`, { method: "POST", body: JSON.stringify({ direction }) });
      setTrace(result);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Trace could not be created"); }
    finally { setRunning(null); }
  }

  if (loading) return <section className="grid min-h-72 place-items-center rounded-xl border border-line bg-white"><div className="text-center"><LoaderCircle className="mx-auto animate-spin text-teal" /><p className="mt-3 text-sm font-semibold">Loading confirmed synthetic outbreaks…</p></div></section>;
  if (error && !outbreaks.length) return <ErrorState message={error} />;
  if (!outbreaks.length) return <EmptyState title="No confirmed outbreaks available" description="A trace can only begin from a confirmed synthetic outbreak record." />;

  return <div className="space-y-6"><DataContextLabel />
    <Card className="p-5 md:p-6"><div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_auto]"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Trace controls</p><h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Start an evidence-backed review</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">Trace results identify recorded contacts for veterinary review. They do not determine disease transmission or assign responsibility.</p></div><label className="block text-sm font-bold text-ink">Confirmed outbreak<select value={selectedOutbreakId ?? ""} onChange={(event) => { setTrace(null); setSelectedOutbreakId(Number(event.target.value)); }} className="mt-2 block min-h-11 w-full rounded-lg border border-line bg-white px-3 text-sm font-normal focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal"><option value="" disabled>Select an outbreak</option>{outbreaks.map((outbreak) => <option value={outbreak.id} key={outbreak.id}>{outbreak.disease_name} · {outbreak.location.name}</option>)}</select></label></div>
      {configuration ? <div className="mt-5 rounded-lg border border-teal/20 bg-teal/5 p-4"><div className="flex gap-3"><CalendarDays className="mt-0.5 text-teal" aria-hidden="true" /><div><p className="font-bold">Configured review window: {configuration.review_window_days} days</p><p className="mt-1 text-sm leading-5 text-slate-700">{configuration.source_label}</p></div></div></div> : <p className="mt-5 text-sm text-slate-600">Loading configured review window…</p>}
      {error ? <p role="alert" className="mt-4 rounded-lg bg-[#FDECEC] p-3 text-sm text-[#8A1C15]">{error}</p> : null}
      <div className="mt-5 flex flex-col gap-3 sm:flex-row"><Button onClick={() => execute("rewind")} disabled={!configuration || running !== null}><RotateCcw size={17} aria-hidden="true" />{running === "rewind" ? "Creating rewind trace…" : "Rewind contacts"}</Button><Button variant="secondary" onClick={() => execute("fast_forward")} disabled={!configuration || running !== null}><ArrowRight size={17} aria-hidden="true" />{running === "fast_forward" ? "Creating fast-forward trace…" : "Fast-forward exposure"}</Button></div></Card>
    {trace ? <TraceResult trace={trace} /> : <EmptyState title="Choose a trace direction" description="Select a confirmed outbreak, review the configured window, then run Rewind or Fast-forward to create a persisted synthetic trace." />}
  </div>;
}

function TraceResult({ trace }: { trace: TraceRun }) {
  const direction = trace.direction === "rewind" ? "Rewind contacts" : "Fast-forward exposure";
  return <div className="space-y-6"><section className="rounded-xl bg-ink px-5 py-6 text-white md:px-7"><p className="text-xs font-bold uppercase tracking-[0.15em] text-lime">Persisted trace result</p><div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><h2 className="font-display text-3xl font-semibold tracking-tight">{direction}</h2><p className="mt-2 text-sm text-white/75">{trace.outbreak.disease_name} · {trace.outbreak.location.name} · {formatDate(trace.window_start)} to {formatDate(trace.window_end)}</p></div><StatusBadge state={trace.direction === "rewind" ? "amber" : "red"} label={trace.direction === "rewind" ? "Rewind review" : "Forward review"} /></div><p className="mt-5 max-w-3xl text-sm leading-6 text-white/80">{trace.disclaimer}</p></section>
    <section aria-label="Trace counts" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Count label="Findings" value={trace.impacted_counts.findings} icon={ShieldAlert} /><Count label="Locations" value={trace.impacted_counts.locations} icon={MapPinned} /><Count label="Vehicles" value={trace.impacted_counts.vehicles} icon={Route} /><Count label="Consignments" value={trace.impacted_counts.consignments} icon={CircleDot} /></section>
    <section className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]"><Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Investigation map</p><h3 className="mt-2 font-display text-2xl font-semibold">Recorded location links</h3><p className="mt-2 text-sm leading-6 text-slate-600">Lines connect the outbreak origin to recorded impacted locations. They are not route navigation or proof of disease transmission.</p><div className="mt-5"><TraceInvestigationMap trace={trace} /></div></Card><Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Chronology</p><h3 className="mt-2 font-display text-2xl font-semibold">Investigation timeline</h3>{trace.timeline.length === 0 ? <p className="mt-5 text-sm leading-6 text-slate-600">No connected movement events were recorded inside this review window.</p> : <ol className="mt-5 space-y-4 border-l border-line pl-5">{trace.timeline.map((finding) => <li key={finding.id} className="relative"><span className="absolute -left-[27px] top-1.5 h-3 w-3 rounded-full border-2 border-white bg-teal" /><p className="text-xs font-bold uppercase tracking-wide text-slate-500">{formatDateTime(finding.event_timestamp)}</p><p className="mt-1 text-sm font-bold text-ink">{humanize(finding.relationship_type)}</p><p className="mt-1 text-sm leading-5 text-slate-600">{finding.explanation}</p></li>)}</ol>}</Card></section>
    <Card className="overflow-hidden"><div className="border-b border-line p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Evidence register</p><h3 className="mt-2 font-display text-2xl font-semibold">Findings requiring review</h3></div>{trace.findings.length === 0 ? <div className="p-6"><EmptyState title="No findings in this window" description="No recorded movement connection matched the selected review period." /></div> : <div className="divide-y divide-line">{trace.findings.map((finding) => <article className="grid gap-3 p-5 md:grid-cols-[150px_130px_1fr_auto] md:items-start" key={finding.id}><p className="text-sm text-slate-600"><Clock3 className="mr-1 inline text-teal" size={15} aria-hidden="true" />{formatDateTime(finding.event_timestamp)}</p><EvidenceBadge level={finding.evidence_level} /><div><p className="text-sm font-bold text-ink">{humanize(finding.relationship_type)}</p><p className="mt-1 text-sm leading-6 text-slate-600">{finding.explanation}</p></div><p className="inline-flex items-center gap-1 text-sm font-bold text-[#8A4B08]"><Stethoscope size={16} aria-hidden="true" />Veterinary review required</p></article>)}</div>}</Card>
  </div>;
}

function Count({ label, value, icon: Icon }: { label: string; value: number; icon: typeof ShieldAlert }) { return <Card className="p-4"><Icon className="text-teal" size={19} aria-hidden="true" /><p className="mt-4 font-display text-3xl font-semibold">{value}</p><p className="mt-1 text-sm font-semibold text-slate-600">{label}</p></Card>; }
function EvidenceBadge({ level }: { level: "direct" | "indirect" }) { return <span className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-xs font-bold ${level === "direct" ? "bg-[#FDECEC] text-[#8A1C15]" : "bg-[#FFF4E5] text-[#8A4B08]"}`}><CircleDot size={14} aria-hidden="true" />{level === "direct" ? "Direct evidence" : "Indirect evidence"}</span>; }
function ErrorState({ message }: { message: string }) { return <section role="alert" className="rounded-xl border border-[#F1B7B2] bg-[#FDECEC] p-6"><AlertCircle className="text-risk-red" /><h2 className="mt-3 font-display text-2xl font-semibold">Trace Lab could not load.</h2><p className="mt-2 text-sm text-slate-700">Confirm that the local API is running, then refresh. Detail: {message}</p></section>; }
function humanize(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase()); }
function formatDate(value: string) { return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(value)); }
function formatDateTime(value: string) { return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)); }
