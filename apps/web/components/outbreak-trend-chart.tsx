"use client";

import { Card } from "@/components/ui/card";
import { type OutbreakTrendPoint } from "@/lib/api";
import { type DataContext } from "@/lib/data-context";

const colors = ["#0f766e", "#b45309", "#b42318", "#475569", "#7c3aed"];

export function OutbreakTrendChart({ points, context }: { points: OutbreakTrendPoint[]; context: DataContext }) {
  if (context === "all") return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Historical outbreak trend</p><h2 className="mt-2 font-display text-2xl font-semibold">Choose a data context</h2><p className="mt-3 text-sm text-slate-600">Select Demo data or Pilot records to view a source-specific trend. Records are never combined in this chart.</p></Card>;
  if (!points.length) return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Historical outbreak trend</p><h2 className="mt-2 font-display text-2xl font-semibold">No outbreak history yet</h2><p className="mt-3 text-sm text-slate-600">No outbreak records exist in the selected data context.</p></Card>;
  const months = [...new Set(points.map(point => point.month))];
  const diseases = [...new Set(points.map(point => point.disease_name))];
  const maximum = Math.max(...points.map(point => point.outbreak_count), 1);
  const value = (disease: string, month: string) => points.find(point => point.disease_name === disease && point.month === month)?.outbreak_count ?? 0;
  const x = (index: number) => 44 + (months.length === 1 ? 140 : index * 252 / (months.length - 1));
  const y = (count: number) => 154 - count * 112 / maximum;
  return <Card className="p-5 md:p-6"><div><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Historical outbreak trend</p><h2 className="mt-2 font-display text-2xl font-semibold">Monthly outbreaks by disease</h2><p className="mt-2 text-sm text-slate-600">Counts reflect only the currently selected data context.</p></div><div className="mt-5 overflow-x-auto"><svg viewBox="0 0 320 190" role="img" aria-label="Monthly outbreak counts by disease" className="min-w-[320px] w-full max-w-2xl"><line x1="44" x2="296" y1="154" y2="154" stroke="#94a3b8" /><line x1="44" x2="44" y1="28" y2="154" stroke="#94a3b8" /><text x="30" y="35" textAnchor="end" fontSize="11" fill="#475569">{maximum}</text><text x="30" y="158" textAnchor="end" fontSize="11" fill="#475569">0</text>{diseases.map((disease, diseaseIndex) => <polyline key={disease} fill="none" stroke={colors[diseaseIndex % colors.length]} strokeWidth="3" points={months.map((month, index) => `${x(index)},${y(value(disease, month))}`).join(" ")} />)}{months.map((month, index) => <text key={month} x={x(index)} y="176" textAnchor="middle" fontSize="10" fill="#475569">{new Intl.DateTimeFormat("en-IN", { month: "short", year: "2-digit" }).format(new Date(month))}</text>)}</svg></div><ul className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs font-semibold">{diseases.map((disease, index) => <li key={disease} className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: colors[index % colors.length] }} />{disease}</li>)}</ul></Card>;
}
