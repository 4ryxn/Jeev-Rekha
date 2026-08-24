"use client";

import { Archive, Edit3, LoaderCircle, MapPinPlus, Search, X } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch, type Location, type LocationDataSource, type LocationRegistryPayload, type RegistryLocationType } from "@/lib/api";

const locationTypes: Array<[RegistryLocationType, string]> = [
  ["village", "Village"],
  ["livestock_market", "Livestock market"],
  ["checkpost", "Checkpost"],
  ["veterinary_centre", "Veterinary centre"],
];

type EditorState = { mode: "create" } | { mode: "edit"; location: Location } | null;

export function LocationRegistry() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<RegistryLocationType | "">("");
  const [sourceFilter, setSourceFilter] = useState<LocationDataSource | "">("");
  const [editor, setEditor] = useState<EditorState>(null);
  const [archiveTarget, setArchiveTarget] = useState<Location | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      setLocations(await apiFetch<Location[]>("/locations?include_inactive=true"));
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load locations.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const filtered = useMemo(() => locations.filter((location) => {
    const query = search.trim().toLowerCase();
    const matchesSearch = !query || [location.name, location.district, location.state].some((value) => value.toLowerCase().includes(query));
    return matchesSearch && (!typeFilter || location.location_type === typeFilter) && (!sourceFilter || location.data_source === sourceFilter);
  }), [locations, search, sourceFilter, typeFilter]);
  const activeCount = locations.filter((location) => location.is_active).length;
  const pilotCount = locations.filter((location) => location.data_source === "pilot_entered").length;
  const demoCount = locations.filter((location) => location.data_source === "demo_seed").length;

  return <Card className="p-5 md:p-6">
    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Local operations registry</p><h2 className="mt-2 font-display text-2xl font-semibold">Location Registry</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">Pilot-entered locations are manually maintained by the local operations team. They are not imported from INAPH, NADRES, IDSP, LGD, or another government system.</p></div>
      <Button type="button" onClick={() => setEditor({ mode: "create" })}><MapPinPlus size={17} aria-hidden="true" />Add location</Button>
    </div>
    <section className="mt-6 grid gap-3 sm:grid-cols-3" aria-label="Location summary">
      <Metric label="Active locations" value={activeCount} /><Metric label="Pilot-entered locations" value={pilotCount} /><Metric label="Demo locations" value={demoCount} />
    </section>
    <div className="mt-6 grid gap-3 lg:grid-cols-[1fr_190px_190px]">
      <label className="relative block"><span className="sr-only">Search locations</span><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={17} aria-hidden="true" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name, district, or state" className="min-h-11 w-full rounded-lg border border-line bg-white py-2 pl-10 pr-3 text-sm" /></label>
      <label><span className="sr-only">Filter location type</span><select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value as RegistryLocationType | "")} className="min-h-11 w-full rounded-lg border border-line bg-white px-3 text-sm"><option value="">All location types</option>{locationTypes.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
      <label><span className="sr-only">Filter data source</span><select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value as LocationDataSource | "")} className="min-h-11 w-full rounded-lg border border-line bg-white px-3 text-sm"><option value="">All sources</option><option value="pilot_entered">Pilot entered</option><option value="demo_seed">Demo seed</option></select></label>
    </div>
    {loading ? <div className="grid min-h-48 place-items-center"><p className="inline-flex items-center gap-2 text-sm font-semibold"><LoaderCircle className="animate-spin text-teal" size={18} />Loading local locations…</p></div> : error ? <p role="alert" className="mt-5 rounded-lg bg-[#FDECEC] p-4 text-sm font-semibold text-risk-red">{error}</p> : filtered.length === 0 ? <p className="mt-5 rounded-lg border border-dashed border-line p-5 text-sm text-slate-600">No locations match the current search and filters.</p> : <div className="mt-5 overflow-x-auto rounded-xl border border-line"><table className="w-full min-w-[900px] text-left text-sm"><thead className="bg-paper text-xs uppercase tracking-wide text-slate-600"><tr><th className="px-4 py-3">Location</th><th className="px-4 py-3">Type</th><th className="px-4 py-3">District, state</th><th className="px-4 py-3">Coordinates</th><th className="px-4 py-3">Source</th><th className="px-4 py-3">Status</th><th className="px-4 py-3"><span className="sr-only">Actions</span></th></tr></thead><tbody className="divide-y divide-line">{filtered.map((location) => <tr key={location.id} className={!location.is_active ? "bg-slate-50 text-slate-500" : "bg-white"}><td className="px-4 py-4 font-bold text-ink">{location.name}</td><td className="px-4 py-4">{typeLabel(location.location_type)}</td><td className="px-4 py-4">{location.district}, {location.state}</td><td className="px-4 py-4 tabular-nums">{location.latitude.toFixed(5)}, {location.longitude.toFixed(5)}</td><td className="px-4 py-4"><SourceBadge source={location.data_source} /></td><td className="px-4 py-4"><StatusBadge active={location.is_active} /></td><td className="px-4 py-4">{location.data_source === "pilot_entered" ? <div className="flex gap-2"><button type="button" onClick={() => setEditor({ mode: "edit", location })} className="inline-flex min-h-9 items-center gap-1 rounded-lg border border-line px-3 font-bold text-teal focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal"><Edit3 size={14} aria-hidden="true" />Edit</button>{location.is_active && <button type="button" onClick={() => setArchiveTarget(location)} className="inline-flex min-h-9 items-center gap-1 rounded-lg border border-line px-3 font-bold text-risk-red focus-visible:outline focus-visible:outline-2 focus-visible:outline-risk-red"><Archive size={14} aria-hidden="true" />Archive</button>}</div> : <span className="text-xs font-bold text-slate-500">Demo seed · read-only</span>}</td></tr>)}</tbody></table></div>}
    {editor && <LocationEditor state={editor} onClose={() => setEditor(null)} onSaved={async () => { setEditor(null); await load(); }} />}
    {archiveTarget && <ArchiveDialog location={archiveTarget} onClose={() => setArchiveTarget(null)} onArchived={async () => { setArchiveTarget(null); await load(); }} />}
  </Card>;
}

function LocationEditor({ state, onClose, onSaved }: { state: Exclude<EditorState, null>; onClose: () => void; onSaved: () => Promise<void> }) {
  const location = state.mode === "edit" ? state.location : null;
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload: LocationRegistryPayload = { name: String(form.get("name")).trim(), location_type: String(form.get("location_type")) as RegistryLocationType, district: String(form.get("district")).trim(), state: String(form.get("state")).trim(), latitude: Number(form.get("latitude")), longitude: Number(form.get("longitude")) };
    setSaving(true); setError("");
    try {
      await apiFetch<Location>(location ? `/locations/${location.id}` : "/locations", { method: location ? "PATCH" : "POST", body: JSON.stringify(payload) });
      await onSaved();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save location.");
    } finally { setSaving(false); }
  };
  return <Dialog title={location ? "Edit pilot location" : "Add pilot location"} onClose={onClose}><form onSubmit={submit} className="space-y-4"><p className="text-sm leading-6 text-slate-600">This creates a manually maintained pilot location. It does not import or verify government data.</p><div className="grid gap-4 sm:grid-cols-2"><RegistryField label="Location name" name="name" defaultValue={location?.name} required /><RegistrySelect label="Location type" name="location_type" defaultValue={location?.location_type} /><RegistryField label="District" name="district" defaultValue={location?.district} required /><RegistryField label="State" name="state" defaultValue={location?.state} required /><RegistryField label="Latitude" name="latitude" type="number" step="any" min="-90" max="90" defaultValue={location?.latitude} required /><RegistryField label="Longitude" name="longitude" type="number" step="any" min="-180" max="180" defaultValue={location?.longitude} required /></div>{error && <p role="alert" className="rounded-lg bg-[#FDECEC] p-3 text-sm font-semibold text-risk-red">{error}</p>}<div className="flex justify-end gap-3"><button type="button" onClick={onClose} className="min-h-11 rounded-lg border border-line px-4 font-bold">Cancel</button><Button type="submit" disabled={saving}>{saving && <LoaderCircle className="animate-spin" size={16} />}{location ? "Save changes" : "Add location"}</Button></div></form></Dialog>;
}

function ArchiveDialog({ location, onClose, onArchived }: { location: Location; onClose: () => void; onArchived: () => Promise<void> }) {
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const archive = async () => {
    setSaving(true); setError("");
    try { await apiFetch<Location>(`/locations/${location.id}/archive`, { method: "POST" }); await onArchived(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not archive location."); } finally { setSaving(false); }
  };
  return <Dialog title="Archive pilot location" onClose={onClose}><p className="text-sm leading-6 text-slate-700">Archive <strong>{location.name}</strong>? It will no longer appear in active location selectors. Referenced locations cannot be archived.</p>{error && <p role="alert" className="mt-4 rounded-lg bg-[#FDECEC] p-3 text-sm font-semibold text-risk-red">{error}</p>}<div className="mt-6 flex justify-end gap-3"><button type="button" onClick={onClose} className="min-h-11 rounded-lg border border-line px-4 font-bold">Cancel</button><button type="button" onClick={archive} disabled={saving} className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-risk-red px-4 font-bold text-white disabled:opacity-60"><Archive size={16} aria-hidden="true" />{saving ? "Archiving…" : "Archive location"}</button></div></Dialog>;
}

function Dialog({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  return <div role="presentation" className="fixed inset-0 z-50 grid place-items-center bg-ink/45 p-4"><section role="dialog" aria-modal="true" aria-labelledby="location-dialog-title" className="w-full max-w-2xl rounded-xl bg-white p-5 shadow-xl md:p-7"><div className="mb-5 flex items-start justify-between gap-4"><h3 id="location-dialog-title" className="font-display text-2xl font-semibold">{title}</h3><button type="button" onClick={onClose} className="rounded-lg p-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal" aria-label="Close dialog"><X size={19} /></button></div>{children}</section></div>;
}

function RegistryField({ label, name, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) { return <label className="block text-sm font-bold text-ink">{label}<input name={name} className="mt-2 min-h-11 w-full rounded-lg border border-line bg-white px-3 text-base" {...props} /></label>; }
function RegistrySelect({ label, name, defaultValue }: { label: string; name: string; defaultValue?: RegistryLocationType }) { return <label className="block text-sm font-bold text-ink">{label}<select name={name} defaultValue={defaultValue ?? "village"} className="mt-2 min-h-11 w-full rounded-lg border border-line bg-white px-3 text-base">{locationTypes.map(([value, text]) => <option value={value} key={value}>{text}</option>)}</select></label>; }
function Metric({ label, value }: { label: string; value: number }) { return <div className="rounded-lg border border-line bg-paper p-4"><p className="font-display text-3xl font-semibold">{value}</p><p className="mt-1 text-xs font-bold uppercase tracking-wide text-slate-600">{label}</p></div>; }
function SourceBadge({ source }: { source: LocationDataSource }) { return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${source === "pilot_entered" ? "bg-[#E8F5ED] text-[#12643D]" : "bg-[#EDF0F3] text-slate-700"}`}>{source === "pilot_entered" ? "Pilot entered" : "Demo seed"}</span>; }
function StatusBadge({ active }: { active: boolean }) { return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${active ? "bg-[#E8F5ED] text-[#12643D]" : "bg-[#EDF0F3] text-slate-700"}`}>{active ? "Active" : "Archived"}</span>; }
function typeLabel(type: RegistryLocationType) { return locationTypes.find(([value]) => value === type)?.[1] ?? type; }
