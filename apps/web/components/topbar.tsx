import { ChevronDown, MapPin, RefreshCw } from "lucide-react";

export function Topbar() {
  return <header className="flex min-h-[73px] items-center justify-between gap-3 border-b border-line bg-paper px-5 md:px-8">
    <button className="inline-flex min-h-11 items-center gap-2 rounded-lg px-2 text-left text-sm font-semibold text-ink hover:bg-ink/5" aria-label="Current placeholder location">
      <MapPin size={18} className="text-teal" aria-hidden="true" /><span className="hidden sm:inline">Karnataka · District workspace</span><span className="sm:hidden">District</span><ChevronDown size={15} aria-hidden="true" />
    </button>
    <div className="flex items-center gap-3">
      <span className="inline-flex items-center gap-2 rounded-full bg-[#E8F5ED] px-3 py-1.5 text-xs font-bold text-[#12643D]"><RefreshCw size={14} aria-hidden="true" />Demo shell synced</span>
      <button className="flex min-h-11 items-center gap-2 rounded-lg px-1 text-left hover:bg-ink/5" aria-label="Profile: District Vet Team"><span className="grid h-8 w-8 place-items-center rounded-full bg-teal text-xs font-bold text-white">DV</span><span className="hidden text-sm font-semibold md:inline">District Vet Team</span></button>
    </div>
  </header>;
}
