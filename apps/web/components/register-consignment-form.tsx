"use client";

import { CheckCircle2, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { apiFetch, type Advisory, type Consignment, type Location } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { submitRegistration } from "@/lib/registration-submit";
import { loadLocationReferences } from "@/lib/location-references";

const localDateTime = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
const consignmentControlClass = "h-16 w-full appearance-auto rounded-xl border border-line bg-white px-4 py-0 text-base leading-6 text-ink";

export function RegisterConsignmentForm() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<Consignment | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [queued, setQueued] = useState(false);
  const [isOtherSpecies, setIsOtherSpecies] = useState(false);

  useEffect(() => {
    loadLocationReferences().then(setLocations).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const values = new FormData(event.currentTarget);
    const origin = Number(values.get("origin_location_id"));
    const destination = Number(values.get("destination_location_id"));
    const selectedSpecies = String(values.get("species"));
    const species = selectedSpecies === "Other" ? String(values.get("other_species") || "").trim() : selectedSpecies;

    if (origin === destination) {
      setError("Origin and destination must be different.");
      return;
    }
    if (!species) {
      setError("Specify species is required when Other is selected.");
      return;
    }

    setSubmitting(true);
    const payload = {
      origin_location_id: origin,
      destination_location_id: destination,
      species,
      animal_count: Number(values.get("animal_count")),
      vehicle_reference: String(values.get("vehicle_reference")),
      departure_at: new Date(String(values.get("departure_at"))).toISOString(),
      vaccination_evidence: String(values.get("vaccination_evidence")),
    };
    const result = await submitRegistration<Consignment>("create_consignment", payload, (id) => `/consignments/${id}`);
    if (result.kind === "central") setCreated(result.entity); else setQueued(true);
    setSubmitting(false);
  }

  async function evaluate() {
    if (!created) return;
    setError("");
    setEvaluating(true);
    try {
      const advisory = await apiFetch<Advisory>("/advisories/evaluate", { method: "POST", body: JSON.stringify({ consignment_id: created.id }) });
      window.location.assign(`/advisories/${advisory.id}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not evaluate movement risk.");
      setEvaluating(false);
    }
  }

  if (queued) return <Card className="max-w-2xl p-7 text-center"><CheckCircle2 className="mx-auto text-risk-amber" size={40} aria-hidden="true" /><h2 className="mt-4 font-display text-3xl font-semibold tracking-tight">Saved on this device. Pending sync.</h2><p className="mt-3 text-sm leading-6 text-slate-600">This consignment has not reached the central database. Offline records remain on this device until a successful sync is confirmed.</p><Link className="mt-6 inline-flex text-sm font-bold text-teal hover:underline" href="/">Return to dashboard</Link></Card>;
  if (created) return <Card className="max-w-2xl p-7 text-center"><CheckCircle2 className="mx-auto text-risk-green" size={40} aria-hidden="true" /><h2 className="mt-4 font-display text-3xl font-semibold tracking-tight">Consignment registered</h2><p className="mt-3 text-sm leading-6 text-slate-600">The synthetic {created.species.toLowerCase()} consignment from {created.origin_location.name} to {created.destination_location.name} is saved. Evaluate it now to receive a deterministic advisory.</p>{error && <p role="alert" className="mt-5 rounded-lg bg-[#FDECEC] p-4 text-sm text-risk-red">{error}</p>}<div className="mt-6 flex flex-col items-center gap-3"><Button type="button" onClick={evaluate} disabled={evaluating}>{evaluating && <LoaderCircle className="animate-spin" size={17} />}Evaluate Movement Risk</Button><Link className="text-sm font-bold text-teal hover:underline" href="/">Return to dashboard</Link></div></Card>;
  if (loading) return <div className="grid min-h-52 place-items-center rounded-xl border border-line bg-white"><p className="inline-flex items-center gap-2 text-sm font-semibold"><LoaderCircle className="animate-spin text-teal" size={18} />Loading location options…</p></div>;
  if (error && locations.length === 0) return <p role="alert" className="rounded-lg bg-[#FDECEC] p-4 text-sm text-risk-red">{error}</p>;

  return (
    <Card className="max-w-4xl p-5 md:p-8">
      <form onSubmit={submit} className="space-y-7">
        <p className="rounded-lg bg-[#FFF3E0] p-4 text-sm leading-6 text-[#704007]">Synthetic data only. This registers a local demo movement record and does not issue a movement permit or risk advisory.</p>
        <fieldset className="grid gap-5 md:grid-cols-2">
          <LocationSelect label="Origin" name="origin_location_id" placeholder="Select origin" locations={locations} />
          <LocationSelect label="Destination" name="destination_location_id" placeholder="Select destination" locations={locations} />
          <SelectField label="Species" name="species" placeholder="Select species" onChange={(event) => setIsOtherSpecies(event.target.value === "Other")}>
            <option value="Cattle">Cattle</option><option value="Buffalo">Buffalo</option><option value="Goat">Goat</option><option value="Sheep">Sheep</option><option value="Pig">Pig</option><option value="Poultry">Poultry</option><option value="Other">Other</option>
          </SelectField>
          {isOtherSpecies && <Field label="Specify species" name="other_species" placeholder="Enter species" required />}
          <Field label="Approximate animal count" name="animal_count" type="number" min="1" max="100000" placeholder="Enter animal count" required />
          <Field label="Vehicle reference" name="vehicle_reference" placeholder="Enter vehicle reference" minLength={3} required />
          <Field label="Departure date and time" name="departure_at" type="datetime-local" defaultValue={localDateTime()} required />
          <SelectField label="Vaccination evidence" name="vaccination_evidence" placeholder="Select vaccination evidence">
            <option value="verified">Verified</option><option value="declared">Declared</option><option value="unknown">Unknown</option>
          </SelectField>
        </fieldset>
        <p className="text-sm leading-6 text-slate-600">Vehicle references match existing synthetic vehicles when available; a new reference creates a local synthetic vehicle record.</p>
        {error && <p role="alert" className="rounded-lg bg-[#FDECEC] p-4 text-sm text-risk-red">{error}</p>}
        <div className="flex justify-end"><Button type="submit" disabled={submitting}>{submitting && <LoaderCircle className="animate-spin" size={17} />}Register consignment</Button></div>
      </form>
    </Card>
  );
}

function Field({ label, name, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) {
  return <label className="block text-sm font-bold text-ink">{label}<input className={`mt-2 ${consignmentControlClass}`} name={name} {...props} /></label>;
}

function SelectField({ label, name, placeholder, children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement> & { label: string; name: string; placeholder: string }) {
  return <label className="block text-sm font-bold text-ink">{label}<select required defaultValue="" className={`mt-2 ${consignmentControlClass}`} name={name} {...props}><option value="" disabled>{placeholder}</option>{children}</select></label>;
}

function LocationSelect({ label, name, placeholder, locations }: { label: string; name: string; placeholder: string; locations: Location[] }) {
  return <SelectField label={label} name={name} placeholder={placeholder}>{locations.map((location) => <option key={location.id} value={location.id}>{location.name} · {location.type.replace("_", " ")}</option>)}</SelectField>;
}
