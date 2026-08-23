"use client";

import { AlertCircle, CheckCircle2, CircleHelp, LoaderCircle, ShieldAlert, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { apiFetch, type Advisory, type RiskState } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { SafeCorridor } from "@/components/safe-corridor";

const presentation: Record<RiskState, { headline: string; icon: typeof CheckCircle2; band: string }> = {
  green: { headline: "Lower risk with sufficient evidence", icon: CheckCircle2, band: "bg-[#E8F5ED] text-[#124A31]" },
  amber: { headline: "Precaution required", icon: TriangleAlert, band: "bg-[#FFF3E0] text-[#713B08]" },
  red: { headline: "High-risk exposure identified", icon: ShieldAlert, band: "bg-[#FDECEC] text-[#831D16]" },
  grey: { headline: "Evidence is insufficient", icon: CircleHelp, band: "bg-[#EDF0F3] text-[#334155]" },
};

export function AdvisoryResult({ advisoryId }: { advisoryId: number }) {
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<Advisory>(`/advisories/${advisoryId}`).then(setAdvisory).catch((reason: Error) => setError(reason.message)); }, [advisoryId]);
  if (error) return <section role="alert" className="rounded-xl border border-[#F1B7B2] bg-[#FDECEC] p-6"><AlertCircle className="text-risk-red" /><h2 className="mt-3 font-display text-2xl font-semibold">Advisory unavailable</h2><p className="mt-2 text-sm">{error}</p></section>;
  if (!advisory) return <div className="grid min-h-80 place-items-center rounded-xl border border-line bg-white"><p className="inline-flex items-center gap-2 text-sm font-semibold"><LoaderCircle className="animate-spin text-teal" size={18} />Loading advisory…</p></div>;
  const view = presentation[advisory.risk_state]; const Icon = view.icon;
  return <div className="space-y-6"><section className={`rounded-xl p-6 md:p-9 ${view.band}`}><StatusBadge state={advisory.risk_state} label={advisory.risk_state.toUpperCase()} /><div className="mt-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"><div><Icon size={34} aria-hidden="true" /><h2 className="mt-4 font-display text-4xl font-semibold tracking-[-0.04em]">{view.headline}</h2><p className="mt-3 max-w-2xl text-base leading-7">{advisory.recommended_action}</p></div><div className="rounded-xl border border-current/20 bg-white/45 px-5 py-4"><p className="text-xs font-bold uppercase tracking-wider">Evidence Coverage Score</p><p className="mt-1 font-display text-4xl font-semibold">{advisory.evidence_coverage_score}<span className="text-lg">/100</span></p></div></div></section><div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]"><Card className="p-5 md:p-6"><h3 className="font-display text-2xl font-semibold tracking-tight">Why this result?</h3><ul className="mt-5 space-y-3">{advisory.reasons.slice(0, 4).map((reason) => <li className="flex gap-3 text-sm leading-6 text-slate-700" key={reason.code}><span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-teal" aria-hidden="true" />{reason.text}</li>)}</ul><details className="mt-7 rounded-lg border border-line p-4"><summary className="cursor-pointer text-sm font-bold text-ink">View factor-by-factor evidence</summary><div className="mt-4 divide-y divide-line">{advisory.evidence_factors.map((factor) => <div className="py-4" key={factor.key}><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-bold">{factor.label}</p><p className="mt-1 text-sm leading-5 text-slate-600">{factor.explanation}</p>{factor.freshness_date && <p className="mt-2 text-xs text-slate-500">Evidence date: {formatDateTime(factor.freshness_date)}</p>}</div><p className="shrink-0 text-sm font-bold text-teal">{factor.score}/{factor.max_score}</p></div></div>)}</div></details></Card><Card className="p-5 md:p-6"><h3 className="font-display text-2xl font-semibold tracking-tight">Consignment</h3><dl className="mt-5 space-y-4 text-sm"><Pair label="Route" value={`${advisory.consignment.origin_location.name} → ${advisory.consignment.destination_location.name}`} /><Pair label="Animals" value={`${advisory.consignment.animal_count} ${advisory.consignment.species}`} /><Pair label="Vehicle" value={advisory.consignment.vehicle.vehicle_reference} /><Pair label="Departure" value={formatDateTime(advisory.consignment.departure_at)} /><Pair label="Evaluated" value={formatDateTime(advisory.evaluated_at)} /></dl></Card></div><p className="rounded-lg border border-line bg-white p-4 text-sm font-semibold text-slate-700">Advisory only—authorised veterinary decisions remain with officials.</p><Link href="/register/consignment" className="inline-flex min-h-11 items-center rounded-[10px] bg-teal px-4 text-sm font-bold text-white">Register another consignment</Link></div>;
}

function Pair({ label, value }: { label: string; value: string }) { return <div><dt className="text-xs font-bold uppercase tracking-wider text-slate-500">{label}</dt><dd className="mt-1 font-semibold text-ink">{value}</dd></div>; }
function formatDateTime(value: string) { return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)); }
