"use client";

import { CheckCircle2, CloudSun, FlaskConical, LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { type Outbreak, type WeatherContext, apiFetch } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";

export function OutbreakDetail({ outbreakId }: { outbreakId: number }) {
  const [outbreak, setOutbreak] = useState<Outbreak | null>(null);
  const [weather, setWeather] = useState<WeatherContext | null>(null);
  const [referralId, setReferralId] = useState<number | null>(null);
  const [referralError, setReferralError] = useState("");
  useEffect(() => { apiFetch<Outbreak>(`/outbreaks/${outbreakId}`).then(setOutbreak); apiFetch<WeatherContext>(`/outbreaks/${outbreakId}/weather-context`).then(setWeather).catch(() => setWeather({ available: false, message: "Weather data unavailable.", observed_at: null, temperature_c: null, relative_humidity: null, wind_speed_kmh: null, weather_code: null, recent_days: [] })); }, [outbreakId]);
  async function referToLab() {
    setReferralError("");
    try {
      const referral = await apiFetch<{ id: number }>(`/outbreaks/${outbreakId}/lab-referrals`, { method: "POST" });
      setReferralId(referral.id);
    } catch (reason) {
      setReferralError(reason instanceof Error ? reason.message : "Could not create laboratory referral.");
    }
  }
  if (!outbreak) return <div className="grid min-h-48 place-items-center"><LoaderCircle className="animate-spin text-teal" /><span className="sr-only">Loading outbreak</span></div>;
  return <div className="grid gap-6 lg:grid-cols-[1fr_.9fr]"><Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Outbreak record</p><h2 className="mt-2 font-display text-3xl font-semibold">{outbreak.disease_name}</h2><p className="mt-2 text-slate-600">{outbreak.species} · {outbreak.location.name}, {outbreak.location.district}</p><dl className="mt-6 grid gap-4 text-sm sm:grid-cols-2"><Item label="Status" value={outbreak.status.replaceAll("_", " ")} /><Item label="Detected" value={new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(outbreak.detected_at))} /><Item label="Verification" value={outbreak.verification_level.replaceAll("_", " ")} /><Item label="Location" value={`${outbreak.location.latitude.toFixed(4)}, ${outbreak.location.longitude.toFixed(4)}`} /></dl>{outbreak.notes && <p className="mt-6 rounded-lg bg-paper p-4 text-sm leading-6">{outbreak.notes}</p>}<div className="mt-6 border-t border-line pt-5"><button type="button" onClick={referToLab} disabled={referralId !== null} className="inline-flex min-h-11 items-center gap-2 rounded-[10px] bg-teal px-4 text-sm font-bold text-white disabled:opacity-60">{referralId !== null ? <CheckCircle2 size={17} /> : <FlaskConical size={17} />} {referralId !== null ? "Referred to lab" : "Refer to lab"}</button>{referralId !== null && <p className="mt-2 text-sm text-slate-600">Referral created. Manage sample status in the Review Queue.</p>}{referralError && <p role="alert" className="mt-2 text-sm text-risk-red">{referralError}</p>}</div></Card><WeatherPanel weather={weather} /></div>;
}

function WeatherPanel({ weather }: { weather: WeatherContext | null }) { if (!weather) return <Card className="p-5 md:p-6"><LoaderCircle className="animate-spin text-teal" /><p className="mt-3 text-sm">Loading environmental context…</p></Card>; if (!weather.available) return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Environmental context</p><EmptyState title="Weather data unavailable" description="Current weather context could not be retrieved. This does not affect the outbreak record or any operational assessment." /></Card>; return <Card className="p-5 md:p-6"><div className="flex items-start gap-3"><CloudSun className="text-teal" aria-hidden="true" /><div><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Environmental context</p><h2 className="mt-2 font-display text-2xl font-semibold">Current and recent weather</h2></div></div><div className="mt-5 grid grid-cols-3 gap-3 text-center"><Metric label="Temperature" value={`${weather.temperature_c}°C`} /><Metric label="Humidity" value={`${weather.relative_humidity}%`} /><Metric label="Wind" value={`${weather.wind_speed_kmh} km/h`} /></div><div className="mt-5 overflow-x-auto"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-slate-500"><tr><th>Date</th><th>Rain</th><th>Temperature</th></tr></thead><tbody>{weather.recent_days.map(day => <tr key={day.date} className="border-t border-line"><td className="py-2">{day.date}</td><td>{day.precipitation_mm} mm</td><td>{day.temperature_min_c}–{day.temperature_max_c}°C</td></tr>)}</tbody></table></div><p className="mt-5 rounded-lg bg-paper p-3 text-xs leading-5 text-slate-600">Environmental context from Open-Meteo. It is informational only and is not a predictive or causal claim about this outbreak.</p></Card>; }
function Item({ label, value }: { label: string; value: string }) { return <div><dt className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</dt><dd className="mt-1 capitalize text-slate-800">{value}</dd></div>; }
function Metric({ label, value }: { label: string; value: string }) { return <div className="rounded-lg bg-paper p-3"><p className="text-lg font-bold">{value}</p><p className="mt-1 text-xs text-slate-600">{label}</p></div>; }
