"use client";

import { CheckCircle2, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { apiFetch, type Location, type Outbreak } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { submitRegistration } from "@/lib/registration-submit";
import { loadLocationReferences } from "@/lib/location-references";

const nowForInput = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
const outbreakControlClass = "h-16 w-full appearance-auto rounded-xl border border-line bg-white px-4 py-0 text-base leading-6 text-ink";

export function RegisterOutbreakForm() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<Outbreak | null>(null);
  const [queued, setQueued] = useState(false);
  const [isOtherDisease, setIsOtherDisease] = useState(false);
  const [isOtherSpecies, setIsOtherSpecies] = useState(false);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);

  useEffect(() => {
    loadLocationReferences().then(setLocations).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const values = new FormData(event.currentTarget);
    const selectedDisease = String(values.get("disease_name"));
    const selectedSpecies = String(values.get("species"));
    const diseaseName = selectedDisease === "Other" ? String(values.get("other_disease") || "").trim() : selectedDisease;
    const species = selectedSpecies === "Other" ? String(values.get("other_species") || "").trim() : selectedSpecies;

    if (!diseaseName || !species) {
      setError("Specify disease and species are required when Other is selected.");
      return;
    }

    setSubmitting(true);
    const payload = {
      disease_name: diseaseName,
      species,
      status: String(values.get("status")),
      location_id: Number(values.get("location_id")),
      detected_at: new Date(String(values.get("detected_at"))).toISOString(),
      confirmed_at: values.get("confirmed_at") ? new Date(String(values.get("confirmed_at"))).toISOString() : null,
      suspected_cases: Number(values.get("suspected_cases")),
      confirmed_cases: Number(values.get("confirmed_cases")),
      mortality_count: Number(values.get("mortality_count")),
      verification_level: String(values.get("verification_level")),
      notes: String(values.get("notes")) || null,
    };
    const result = await submitRegistration<Outbreak>("create_outbreak", payload, (id) => `/outbreaks/${id}`);
    if (result.kind === "central") setCreated(result.entity); else setQueued(true);
    setSubmitting(false);
  }

  if (queued) return <Success title="Saved on this device. Pending sync." detail="This outbreak record has not reached the central database. Offline records remain on this device until a successful sync is confirmed." />;
  if (created) return <Success title="Outbreak record created" detail={`${created.disease_name} was added to the synthetic operations dataset.`} />;
  if (loading) return <Loading label="Loading location options…" />;
  if (error && locations.length === 0) return <ErrorMessage message={error} />;

  return (
    <Card className="max-w-4xl p-5 md:p-8">
      <form onSubmit={submit} className="space-y-7">
        <p className="rounded-lg bg-[#FFF3E0] p-4 text-sm leading-6 text-[#704007]">Synthetic data only. This workflow does not submit a real animal-health notification or issue an official alert.</p>
        <fieldset className="grid gap-5 md:grid-cols-2">
          <SelectField label="Disease name" name="disease_name" placeholder="Select disease" onChange={(event) => setIsOtherDisease(event.target.value === "Other")}>
            <option value="Foot-and-mouth disease">Foot-and-mouth disease</option><option value="Peste des petits ruminants">Peste des petits ruminants</option><option value="Haemorrhagic septicaemia">Haemorrhagic septicaemia</option><option value="Anthrax">Anthrax</option><option value="Brucellosis">Brucellosis</option><option value="Other">Other</option>
          </SelectField>
          {isOtherDisease && <Field label="Specify disease" name="other_disease" placeholder="Enter disease" required />}
          <SelectField label="Species" name="species" placeholder="Select species" onChange={(event) => setIsOtherSpecies(event.target.value === "Other")}>
            <option value="Cattle">Cattle</option><option value="Buffalo">Buffalo</option><option value="Goat">Goat</option><option value="Sheep">Sheep</option><option value="Pig">Pig</option><option value="Poultry">Poultry</option><option value="Other">Other</option>
          </SelectField>
          {isOtherSpecies && <Field label="Specify species" name="other_species" placeholder="Enter species" required />}
          <SelectField label="Outbreak status" name="status" placeholder="Select outbreak status">
            <option value="suspected">Suspected</option><option value="confirmed">Confirmed</option><option value="closed">Closed</option>
          </SelectField>
          <div><SelectField label="Location" name="location_id" placeholder="Select location" onChange={(event) => setSelectedLocationId(Number(event.target.value) || null)}>
            {locations.map((location) => <option key={location.id} value={location.id}>{location.name} · {location.type.replace("_", " ")}</option>)}
          </SelectField>{locations.find((location) => location.id === selectedLocationId)?.data_source === "pilot_entered" && <p className="mt-2 text-xs font-bold text-teal">Pilot-entered location</p>}</div>
          <Field label="Detected at" name="detected_at" type="datetime-local" defaultValue={nowForInput()} required />
          <Field label="Confirmed at (optional)" name="confirmed_at" type="datetime-local" />
          <SelectField label="Verification level" name="verification_level" placeholder="Select verification level">
            <option value="reported">Reported</option><option value="veterinary_verified">Veterinary verified</option><option value="laboratory_confirmed">Laboratory confirmed</option>
          </SelectField>
          <Field label="Suspected cases" name="suspected_cases" type="number" min="0" placeholder="Enter suspected cases" required />
          <Field label="Confirmed cases" name="confirmed_cases" type="number" min="0" placeholder="Enter confirmed cases" required />
          <Field label="Mortality count" name="mortality_count" type="number" min="0" placeholder="Enter mortality count" required />
          <TextArea label="Notes" name="notes" placeholder="Add optional field notes" />
        </fieldset>
        {error && <ErrorMessage message={error} />}
        <div className="flex justify-end"><Button disabled={submitting} type="submit">{submitting && <LoaderCircle className="animate-spin" size={17} />}Create outbreak record</Button></div>
      </form>
    </Card>
  );
}

function Field({ label, name, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) {
  return <label className="block text-sm font-bold text-ink">{label}<input name={name} className={`mt-2 ${outbreakControlClass}`} {...props} /></label>;
}

function SelectField({ label, name, placeholder, children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement> & { label: string; name: string; placeholder: string }) {
  return <label className="block text-sm font-bold text-ink">{label}<select required defaultValue="" name={name} className={`mt-2 ${outbreakControlClass}`} {...props}><option value="" disabled>{placeholder}</option>{children}</select></label>;
}

function TextArea({ label, name, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string; name: string }) {
  return <label className="block text-sm font-bold text-ink">{label} <span className="font-normal text-slate-500">(optional)</span><textarea name={name} className={`mt-2 ${outbreakControlClass} resize-y`} maxLength={2000} {...props} /></label>;
}

function Loading({ label }: { label: string }) { return <div className="grid min-h-52 place-items-center rounded-xl border border-line bg-white"><p className="inline-flex items-center gap-2 text-sm font-semibold"><LoaderCircle className="animate-spin text-teal" size={18} />{label}</p></div>; }
function ErrorMessage({ message }: { message: string }) { return <p role="alert" className="rounded-lg bg-[#FDECEC] p-4 text-sm leading-6 text-risk-red">{message}</p>; }
function Success({ title, detail }: { title: string; detail: string }) { return <Card className="max-w-2xl p-7 text-center"><CheckCircle2 className="mx-auto text-risk-green" size={40} aria-hidden="true" /><h2 className="mt-4 font-display text-3xl font-semibold tracking-tight">{title}</h2><p className="mt-3 text-sm leading-6 text-slate-600">{detail}</p><Link className="mt-6 inline-flex min-h-11 items-center rounded-[10px] bg-teal px-4 text-sm font-bold text-white" href="/">Return to dashboard</Link></Card>; }
