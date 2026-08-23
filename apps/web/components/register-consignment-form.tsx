"use client";

import { CheckCircle2, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { apiFetch, type Advisory, type Consignment, type Location } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const localDateTime = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60_000).toISOString().slice(0, 16);

export function RegisterConsignmentForm() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<Consignment | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  useEffect(() => { apiFetch<Location[]>("/locations").then(setLocations).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false)); }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError("");
    const values = new FormData(event.currentTarget);
    const origin = Number(values.get("origin_location_id")); const destination = Number(values.get("destination_location_id"));
    if (origin === destination) { setError("Origin and destination must be different."); return; }
    setSubmitting(true);
    try {
      setCreated(await apiFetch<Consignment>("/consignments", { method: "POST", body: JSON.stringify({ origin_location_id: origin, destination_location_id: destination, species: String(values.get("species")), animal_count: Number(values.get("animal_count")), vehicle_reference: String(values.get("vehicle_reference")), departure_at: new Date(String(values.get("departure_at"))).toISOString(), vaccination_evidence: String(values.get("vaccination_evidence")) }) }));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not register consignment."); } finally { setSubmitting(false); }
  }

  async function evaluate() {
    if (!created) return;
    setError(""); setEvaluating(true);
    try { const advisory = await apiFetch<Advisory>("/advisories/evaluate", { method: "POST", body: JSON.stringify({ consignment_id: created.id }) }); window.location.assign(`/advisories/${advisory.id}`); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not evaluate movement risk."); setEvaluating(false); }
  }

  if (created) return <Card className="max-w-2xl p-7 text-center"><CheckCircle2 className="mx-auto text-risk-green" size={40} aria-hidden="true" /><h2 className="mt-4 font-display text-3xl font-semibold tracking-tight">Consignment registered</h2><p className="mt-3 text-sm leading-6 text-slate-600">The synthetic {created.species.toLowerCase()} consignment from {created.origin_location.name} to {created.destination_location.name} is saved. Evaluate it now to receive a deterministic advisory.</p>{error && <p role="alert" className="mt-5 rounded-lg bg-[#FDECEC] p-4 text-sm text-risk-red">{error}</p>}<div className="mt-6 flex flex-col items-center gap-3"><Button type="button" onClick={evaluate} disabled={evaluating}>{evaluating && <LoaderCircle className="animate-spin" size={17} />}Evaluate Movement Risk</Button><Link className="text-sm font-bold text-teal hover:underline" href="/">Return to dashboard</Link></div></Card>;
  if (loading) return <div className="grid min-h-52 place-items-center rounded-xl border border-line bg-white"><p className="inline-flex items-center gap-2 text-sm font-semibold"><LoaderCircle className="animate-spin text-teal" size={18} />Loading location options…</p></div>;
  if (error && locations.length === 0) return <p role="alert" className="rounded-lg bg-[#FDECEC] p-4 text-sm text-risk-red">Unable to load locations: {error}</p>;
  return <Card className="max-w-4xl p-5 md:p-8"><form onSubmit={submit} className="space-y-7"><p className="rounded-lg bg-[#FFF3E0] p-4 text-sm leading-6 text-[#704007]">Synthetic data only. This registers a local demo movement record and does not issue a movement permit or risk advisory.</p><fieldset className="grid gap-5 md:grid-cols-2"><Select label="Origin" name="origin_location_id" locations={locations} /><Select label="Destination" name="destination_location_id" locations={locations} /><Field label="Species" name="species" placeholder="e.g. Cattle" required /><Field label="Approximate animal count" name="animal_count" type="number" min="1" max="100000" required /><Field label="Vehicle reference" name="vehicle_reference" placeholder="e.g. KA-01-JR-1042" minLength={3} required /><Field label="Departure date and time" name="departure_at" type="datetime-local" defaultValue={localDateTime()} required /><label className="block text-sm font-bold text-ink">Vaccination evidence<select name="vaccination_evidence" className="mt-2 min-h-11 w-full rounded-[10px] border border-line bg-white px-3 text-base"><option value="verified">Verified</option><option value="declared">Declared</option><option value="unknown">Unknown</option></select></label></fieldset><p className="text-sm leading-6 text-slate-600">Vehicle references match existing synthetic vehicles when available; a new reference creates a local synthetic vehicle record.</p>{error && <p role="alert" className="rounded-lg bg-[#FDECEC] p-4 text-sm text-risk-red">{error}</p>}<div className="flex justify-end"><Button type="submit" disabled={submitting}>{submitting && <LoaderCircle className="animate-spin" size={17} />}Register consignment</Button></div></form></Card>;
}

function Field({ label, name, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) { return <label className="block text-sm font-bold text-ink">{label}<input className="mt-2 min-h-11 w-full rounded-[10px] border border-line px-3 text-base" name={name} {...props} /></label>; }
function Select({ label, name, locations }: { label: string; name: string; locations: Location[] }) { return <label className="block text-sm font-bold text-ink">{label}<select name={name} className="mt-2 min-h-11 w-full rounded-[10px] border border-line bg-white px-3 text-base">{locations.map((location) => <option key={location.id} value={location.id}>{location.name} · {location.type.replace("_", " ")}</option>)}</select></label>; }
