"use client";

import { useEffect, useState } from "react";
import { apiFetch, type ReviewCase } from "@/lib/api";

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const [referral, setReferral] = useState<ReviewCase | null>(null);

  useEffect(() => { params.then(({ id }) => apiFetch<ReviewCase>(`/reports/lab-referrals/${id}`).then(setReferral)); }, [params]);
  if (!referral) return <p>Loading laboratory referral brief…</p>;

  return <main className="mx-auto max-w-3xl p-8 print:p-4"><h1>Jeev Rekha — Laboratory Referral Brief</h1><p><b>{referral.title}</b></p><p>Case status: {referral.status} · Sample status: {referral.sample_status.replaceAll("_", " ")}</p><h2>Review summary</h2><p>{referral.summary}</p><h2>Resolution note</h2><p>{referral.resolution_note || "No result note recorded."}</p><p>Source evidence remains unchanged. This brief supports authorised veterinary review and does not confirm infection.</p><button onClick={() => window.print()}>Print referral brief</button></main>;
}
