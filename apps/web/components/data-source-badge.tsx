import { Tag } from "lucide-react";
import type { LocationDataSource } from "@/lib/api";

export function DataSourceBadge({ source }: { source: LocationDataSource }) { return <span className="inline-flex items-center gap-1 rounded-full border border-line bg-white px-2 py-1 text-[11px] font-bold text-slate-700"><Tag size={12} aria-hidden="true" />{source === "demo_seed" ? "Demo seed" : "Pilot entered"}</span>; }
