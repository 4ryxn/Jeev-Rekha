"use client";

import { RefreshCw } from "lucide-react";

export function RouteLoading({ label }: { label: string }) {
  return <main className="mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-9"><section aria-busy="true" className="rounded-xl border border-line bg-white p-8 text-sm text-slate-600">Loading {label}…</section></main>;
}

export function RouteError({ label, reset }: { label: string; reset: () => void }) {
  return <main className="mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-9"><section role="alert" className="rounded-xl border border-red/30 bg-white p-8"><h1 className="font-display text-2xl font-semibold">{label} could not load</h1><p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">The workspace could not confirm this data from the API. No record has been created or changed. Check connectivity and try again.</p><button type="button" onClick={reset} className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-[10px] bg-teal px-4 text-sm font-semibold text-white hover:bg-[#0b625c]"><RefreshCw size={16} aria-hidden="true" />Try again</button><p className="mt-5 text-xs leading-5 text-slate-500">Jeev Rekha is decision support only. Synthetic and pilot data remain clearly labelled; no live government integration is connected.</p></section></main>;
}
