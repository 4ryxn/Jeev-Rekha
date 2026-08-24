"use client";

import { Database } from "lucide-react";
import { dataContextDescription, dataContextLabel, type DataContext, useDataContext } from "@/lib/data-context";

export function DataContextControl() { const { context, setContext } = useDataContext(); return <label className="hidden min-w-0 items-center gap-2 rounded-lg border border-line bg-white px-2 py-1 text-xs font-semibold text-ink lg:flex"><Database size={15} className="text-teal" aria-hidden="true" /><span className="sr-only">Data context</span><select aria-label="Data context" value={context} onChange={event => setContext(event.target.value as DataContext)} className="max-w-32 bg-transparent py-1 outline-none"><option value="demo_seed">Demo data</option><option value="pilot_entered">Pilot records</option><option value="all">All records</option></select><span className="sr-only">{dataContextDescription(context)}</span></label>; }
export function DataContextLabel() { const { context } = useDataContext(); return <p className="inline-flex items-center gap-1 rounded-full border border-line bg-white px-3 py-1 text-xs font-bold text-slate-700"><Database size={13} aria-hidden="true" />Data context: {dataContextLabel(context)}</p>; }
