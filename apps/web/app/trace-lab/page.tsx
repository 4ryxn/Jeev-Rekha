import { AppShell } from "@/components/app-shell";
import { TraceLab } from "@/components/trace-lab";
import { PageHeader } from "@/components/ui/page-header";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Trace Lab" };

export default function TraceLabPage() {
  return <AppShell><div className="space-y-8"><PageHeader eyebrow="Operational investigation" title="Trace Lab" description="Select Rewind contacts or Fast-forward exposure to create a persisted trace." /><Suspense fallback={<div className="rounded-xl border border-line bg-white p-8 text-sm text-slate-600">Loading Trace Lab…</div>}><TraceLab /></Suspense></div></AppShell>;
}
import { Suspense } from "react";
