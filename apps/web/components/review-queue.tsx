"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, type ReviewCase, type ReviewCaseType, type SampleStatus } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataContextLabel } from "@/components/data-context-control";
import { sourcePath, useDataContext } from "@/lib/data-context";

const caseTypeOptions: { value: ReviewCaseType | "all"; label: string }[] = [
  { value: "all", label: "All case types" },
  { value: "evidence_gap", label: "Evidence gap" },
  { value: "sync_exception", label: "Sync exception" },
  { value: "trace_contact", label: "Trace contact" },
  { value: "lab_referral", label: "Lab referral" },
];

const sampleStatusOrder: SampleStatus[] = ["none", "collected", "sent_to_lab", "result_received"];

export function ReviewQueue() {
  const { context } = useDataContext();
  const [cases, setCases] = useState<ReviewCase[]>([]);
  const [selected, setSelected] = useState<ReviewCase | null>(null);
  const [caseType, setCaseType] = useState<ReviewCaseType | "all">("all");
  const [note, setNote] = useState("");

  const load = useCallback(() => {
    const path = caseType === "all" ? "/review-cases" : `/review-cases?category=${caseType}`;
    return apiFetch<ReviewCase[]>(sourcePath(path, context)).then(setCases);
  }, [caseType, context]);

  useEffect(() => { load(); }, [load]);

  const pilot = (item: ReviewCase) => item.source_type === "advisory" && item.data_source === "pilot_entered";
  const nextSampleStatus = selected?.sample_status ? sampleStatusOrder[sampleStatusOrder.indexOf(selected.sample_status) + 1] : undefined;

  async function update(status: "acknowledged" | "resolved") {
    if (!selected) return;
    const updated = await apiFetch<ReviewCase>(`/review-cases/${selected.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status, resolution_note: note }),
    });
    setSelected(updated);
    setNote("");
    load();
  }

  async function advanceSampleStatus() {
    if (!selected || !nextSampleStatus) return;
    const updated = await apiFetch<ReviewCase>(`/review-cases/${selected.id}/sample-status`, {
      method: "PATCH",
      body: JSON.stringify({ sample_status: nextSampleStatus }),
    });
    setSelected(updated);
    load();
  }

  return (
    <div className="space-y-6">
      <DataContextLabel />
      <p className="rounded border border-line bg-paper p-4 text-sm">Review decisions organise evidence for authorised follow-up; they do not alter the source record.</p>
      <label className="block max-w-sm text-sm font-bold">
        Case type
        <select value={caseType} onChange={(event) => { setCaseType(event.target.value as ReviewCaseType | "all"); setSelected(null); }} className="mt-2 min-h-11 w-full rounded border border-line bg-white px-3">
          {caseTypeOptions.map((option) => <option value={option.value} key={option.value}>{option.label}</option>)}
        </select>
      </label>
      <Card className="divide-y">
        {cases.map((item) => <button key={item.id} onClick={() => { setSelected(item); setNote(""); }} className="block w-full p-4 text-left hover:bg-paper">
          <b>{item.priority} priority · {item.title}</b>
          <span className="ml-2 rounded-full border border-line px-2 py-1 text-xs font-bold">{item.case_type.replaceAll("_", " ")}</span>
          {pilot(item) && <span className="ml-2 rounded-full border border-line px-2 py-1 text-xs font-bold">Pilot advisory</span>}
          <p className="text-sm">{item.summary}</p>
        </button>)}
        {!cases.length && <p className="p-5">No persisted review cases match this data context.</p>}
      </Card>
      {selected && <Card className="p-5">
        <h2 className="text-xl font-bold">{selected.title}</h2>
        <p className="mt-2 text-xs font-bold uppercase text-slate-500">{selected.case_type.replaceAll("_", " ")} · {selected.status}</p>
        {selected.case_type === "lab_referral" && <p className="mt-2 text-sm font-semibold">Sample status: {selected.sample_status.replaceAll("_", " ")}</p>}
        {pilot(selected) && <p className="mt-2 text-sm font-bold">Pilot advisory</p>}
        <p className="mt-2">{selected.source_summary}</p>
        <Link className="mt-3 inline-block text-teal underline" href={selected.source_href}>{pilot(selected) ? "Open pilot advisory evidence" : "Open original evidence"}</Link>
        {selected.case_type === "lab_referral" && selected.status === "open" && nextSampleStatus && <Button className="mt-4" onClick={advanceSampleStatus}>Mark sample {nextSampleStatus.replaceAll("_", " ")}</Button>}
        {selected.status === "open" && <Button className="mt-3 block" onClick={() => update("acknowledged")}>Acknowledge case</Button>}
        {selected.status !== "resolved" && <div className="mt-3">
          <textarea aria-label="Resolution note" placeholder="Optional result note for lab referrals" value={note} onChange={(event) => setNote(event.target.value)} className="block w-full border" />
          <Button className="mt-2" disabled={selected.case_type !== "lab_referral" && !note.trim()} onClick={() => update("resolved")}>Resolve case</Button>
        </div>}
      </Card>}
    </div>
  );
}
