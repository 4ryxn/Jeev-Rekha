"use client";

import { Card } from "@/components/ui/card";
import { type OutbreakTrendPoint } from "@/lib/api";
import { type DataContext } from "@/lib/data-context";

const colors = ["#0f766e", "#b45309", "#b42318", "#475569", "#7c3aed"];
const chartHeight = 220;
const chartTop = 24;
const chartBottom = 174;
const chartLeft = 48;
const chartRight = 24;

export function OutbreakTrendChart({ points, context }: { points: OutbreakTrendPoint[]; context: DataContext }) {
  if (context === "all") return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Historical outbreak trend</p><h2 className="mt-2 font-display text-2xl font-semibold">Choose a data context</h2><p className="mt-3 text-sm text-slate-600">Select Demo data or Pilot records to view a source-specific trend. Records are never combined in this chart.</p></Card>;
  if (!points.length) return <Card className="p-5 md:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Historical outbreak trend</p><h2 className="mt-2 font-display text-2xl font-semibold">No outbreak history yet</h2><p className="mt-3 text-sm text-slate-600">No outbreak records exist in the selected data context.</p></Card>;
  const months = [...new Set(points.map(point => point.month))].sort();
  const diseases = [...new Set(points.map(point => point.disease_name))];
  const maximum = Math.max(...points.map(point => point.outbreak_count), 1);
  const chartWidth = Math.max(320, chartLeft + chartRight + months.length * 116);
  const groupWidth = (chartWidth - chartLeft - chartRight) / months.length;
  const barWidth = Math.max(10, Math.min(30, groupWidth / Math.max(diseases.length + 1, 3)));
  const value = (disease: string, month: string) => points.find(point => point.disease_name === disease && point.month === month)?.outbreak_count ?? 0;
  const y = (count: number) => chartBottom - count * (chartBottom - chartTop) / maximum;
  const formatMonth = (month: string) => new Intl.DateTimeFormat("en-IN", { month: "short", year: "numeric" }).format(new Date(month));
  const ticks = Array.from({ length: maximum + 1 }, (_, index) => index);
  return <Card className="p-5 md:p-6"><div><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">Historical outbreak trend</p><h2 className="mt-2 font-display text-2xl font-semibold">Monthly outbreaks by disease</h2><p className="mt-2 text-sm text-slate-600">Counts reflect only the currently selected data context. Bars show exact records per month.</p></div><div className="mt-5 overflow-x-auto"><svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label="Monthly outbreak counts by disease" className="h-auto min-w-[320px] w-full"><title>Monthly outbreak counts by disease</title>{ticks.map((tick) => <g key={tick}><line x1={chartLeft} x2={chartWidth - chartRight} y1={y(tick)} y2={y(tick)} stroke={tick === 0 ? "#94a3b8" : "#e2e8f0"} /><text x={chartLeft - 10} y={y(tick) + 4} textAnchor="end" fontSize="11" fill="#475569">{tick}</text></g>)}{months.map((month, monthIndex) => <g key={month}><text x={chartLeft + groupWidth * monthIndex + groupWidth / 2} y={chartBottom + 24} textAnchor="middle" fontSize="11" fill="#475569">{formatMonth(month)}</text>{diseases.map((disease, diseaseIndex) => { const count = value(disease, month); const x = chartLeft + groupWidth * monthIndex + (groupWidth - diseases.length * barWidth) / 2 + diseaseIndex * barWidth; const barY = y(count); return <g key={disease}><title>{`${disease}, ${formatMonth(month)}: ${count}`}</title><rect x={x + 2} y={barY} width={Math.max(4, barWidth - 4)} height={chartBottom - barY} rx="2" fill={colors[diseaseIndex % colors.length]} />{count > 0 && <text x={x + barWidth / 2} y={barY - 6} textAnchor="middle" fontSize="11" fontWeight="700" fill="#334155">{count}</text>}</g>; })}</g>)}</svg></div><ul className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-xs font-semibold">{diseases.map((disease, index) => <li key={disease} className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: colors[index % colors.length] }} />{disease}</li>)}</ul><details className="mt-4 rounded-lg border border-line p-3"><summary className="cursor-pointer text-sm font-bold">View exact counts</summary><div className="mt-3 overflow-x-auto"><table className="w-full min-w-[360px] text-left text-sm"><caption className="sr-only">Monthly outbreak counts by disease</caption><thead><tr className="border-b border-line text-xs uppercase text-slate-500"><th className="py-2 pr-4">Month</th>{diseases.map((disease) => <th className="px-2 py-2" key={disease}>{disease}</th>)}</tr></thead><tbody>{months.map((month) => <tr className="border-b border-line last:border-0" key={month}><th className="py-2 pr-4 font-semibold">{formatMonth(month)}</th>{diseases.map((disease) => <td className="px-2 py-2" key={disease}>{value(disease, month)}</td>)}</tr>)}</tbody></table></div></details></Card>;
}
