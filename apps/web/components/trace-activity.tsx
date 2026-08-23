"use client";

import { ArrowUpRight, FlaskConical, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { type Outbreak, type TraceRun, apiFetch } from "@/lib/api";

export function TraceActivity() {
  const [trace, setTrace] = useState<TraceRun | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    apiFetch<Outbreak[]>("/outbreaks")
      .then(async (outbreaks) => {
        const confirmed = outbreaks.filter((outbreak) => outbreak.status === "confirmed");
        const runs = (await Promise.all(confirmed.map((outbreak) => apiFetch<TraceRun[]>(`/outbreaks/${outbreak.id}/traces`)))).flat();
        runs.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setTrace(runs[0] ?? null);
        setState("ready");
      })
      .catch(() => setState("error"));
  }, []);

  if (state === "loading") return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Trace activity</p><div className="mt-5 flex items-center gap-3 text-sm text-slate-600"><LoaderCircle className="animate-spin text-teal" size={18} />Loading persisted trace activity…</div></Card>;
  if (state === "error") return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Trace activity</p><p className="mt-4 text-sm leading-6 text-slate-600">Trace activity could not be loaded. Open Trace Lab to retry.</p><Link href="/trace-lab" className="mt-4 inline-flex min-h-11 items-center font-bold text-teal hover:underline">Open Trace Lab <ArrowUpRight className="ml-1" size={16} /></Link></Card>;
  if (!trace) return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Trace activity</p><div className="mt-4"><EmptyState title="No trace runs yet" description="Open Trace Lab to create a persisted Rewind or Fast-forward veterinary review." /></div><Link href="/trace-lab" className="mt-4 inline-flex min-h-11 items-center font-bold text-teal hover:underline">Open Trace Lab <ArrowUpRight className="ml-1" size={16} /></Link></Card>;
  return <Card className="p-5 md:p-6"><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-teal">Trace activity</p><h2 className="mt-2 font-display text-2xl font-semibold tracking-tight">Latest persisted review</h2></div><FlaskConical className="text-teal" aria-hidden="true" /></div><p className="mt-5 text-sm font-bold text-ink">{trace.direction === "rewind" ? "Rewind contacts" : "Fast-forward exposure"}</p><p className="mt-1 text-sm text-slate-600">{trace.outbreak.disease_name} · {trace.outbreak.location.name}</p><p className="mt-3 text-sm text-slate-600">{trace.impacted_counts.findings} findings · {formatDate(trace.created_at)}</p><Link href={`/trace-lab?traceId=${trace.id}`} className="mt-5 inline-flex min-h-11 items-center font-bold text-teal hover:underline">View trace <ArrowUpRight className="ml-1" size={16} /></Link></Card>;
}

function formatDate(value: string) { return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(value)); }
