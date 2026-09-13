"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, type ReportIndex } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { DataContextLabel } from "@/components/data-context-control";
import { DataSourceBadge } from "@/components/data-source-badge";
import { sourcePath, useDataContext } from "@/lib/data-context";

export function ReportsHome() {
  const { context } = useDataContext();
  const [reports, setReports] = useState<ReportIndex | null>(null);

  useEffect(() => { apiFetch<ReportIndex>(sourcePath("/reports", context)).then(setReports); }, [context]);
  if (!reports) return <p>Loading persisted report sources…</p>;

  const groups = [
    ["Movement Advisory Brief", reports.advisories],
    ["Trace Contact Review Package", reports.traces],
    ["Containment Action Brief", reports.containment],
    ["Laboratory Referral Brief", reports.lab_referrals],
  ] as const;

  return <div className="space-y-5"><DataContextLabel /><p className="rounded border border-line bg-paper p-4 text-sm">Synthetic data only. These browser-printable briefs are decision support, not government certificates or orders.</p>{groups.map(([title, items]) => <Card key={title} className="p-5"><h2 className="font-display text-xl font-bold">{title}</h2>{items.length ? <ul className="mt-3 space-y-2">{items.map((item) => <li className="flex items-center gap-2" key={item.id}><Link className="text-teal underline" href={item.href}>{item.title}</Link>{context === "all" && <DataSourceBadge source={item.data_source} />}</li>)}</ul> : <p className="mt-3 text-sm">No persisted source is available yet.</p>}</Card>)}</div>;
}
