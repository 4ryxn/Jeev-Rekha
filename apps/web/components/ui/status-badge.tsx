import { AlertTriangle, CheckCircle2, CircleHelp, type LucideIcon, ShieldAlert } from "lucide-react";

export type RiskStatus = "green" | "amber" | "red" | "grey";

const status: Record<RiskStatus, { label: string; classes: string; icon: LucideIcon }> = {
  green: { label: "Green · Lower risk", classes: "bg-[#E8F5ED] text-[#12643D]", icon: CheckCircle2 },
  amber: { label: "Amber · Precaution", classes: "bg-[#FFF3E0] text-[#8A4205]", icon: AlertTriangle },
  red: { label: "Red · High risk", classes: "bg-[#FDECEC] text-[#9F1D14]", icon: ShieldAlert },
  grey: { label: "Grey · Evidence insufficient", classes: "bg-[#EDF0F3] text-[#334155]", icon: CircleHelp },
};

export function StatusBadge({ state, label }: { state: RiskStatus; label?: string }) {
  const item = status[state];
  const Icon = item.icon;
  return <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold ${item.classes}`}><Icon aria-hidden="true" size={15} strokeWidth={2.5} />{label ?? item.label}</span>;
}
