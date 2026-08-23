"use client";

import { ClipboardPlus, FlaskConical, LayoutDashboard, Map, ShieldCheck, ClipboardCheck, FileText } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/register", label: "Register", icon: ClipboardPlus },
  { href: "/map", label: "Map & Advisories", icon: Map },
  { href: "/trace-lab", label: "Trace Lab", icon: FlaskConical },
  { href: "/review-queue", label: "Review Queue", icon: ClipboardCheck },
  { href: "/reports", label: "Reports", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();
  return <aside className="flex shrink-0 flex-col border-b border-white/10 bg-ink text-white md:w-[236px] md:border-b-0 md:border-r">
    <div className="flex items-center gap-3 px-5 py-5 md:px-6 md:py-7">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-lime text-ink"><ShieldCheck size={22} aria-hidden="true" /></span>
      <div><p className="font-display text-lg font-semibold tracking-tight">Jeev Rekha</p><p className="text-[10px] font-bold uppercase tracking-[0.16em] text-white/55">Operations</p></div>
    </div>
    <nav aria-label="Primary navigation" className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:px-4">
      {items.map((item) => {
        const Icon = item.icon;
        const active = item.href === "/" ? pathname === item.href : pathname.startsWith(item.href);
        return <Link key={item.href} href={item.href} className={`inline-flex min-h-11 shrink-0 items-center gap-3 rounded-lg px-3 text-sm font-semibold ${active ? "bg-lime text-ink" : "text-white/75 hover:bg-white/10 hover:text-white"}`}><Icon size={18} aria-hidden="true" />{item.label}</Link>;
      })}
    </nav>
    <div className="m-4 mt-auto hidden rounded-xl border border-white/10 bg-white/5 p-4 md:block"><p className="text-xs font-bold uppercase tracking-wider text-lime">Synthetic data only</p><p className="mt-2 text-xs leading-5 text-white/70">No live government data is connected.</p></div>
  </aside>;
}
