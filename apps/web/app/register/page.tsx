import { ClipboardPlus, Stethoscope } from "lucide-react";
import Link from "next/link";
import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";

const actions = [
  { href: "/register/consignment", icon: ClipboardPlus, title: "Register a consignment", description: "Record a livestock movement with origin, destination, vehicle, timing, and vaccination evidence." },
  { href: "/register/outbreak", icon: Stethoscope, title: "Record outbreak evidence", description: "Capture a synthetic suspected, confirmed, or closed outbreak record for the operations workspace." },
];

export const metadata: Metadata = { title: "Register operational record" };

export default function RegisterPage() {
  return <AppShell><div className="space-y-8"><PageHeader eyebrow="Core operations" title="Register" description="Choose a real local workflow. All records entered in this environment are synthetic demonstration data only." /><div className="grid gap-6 md:grid-cols-2">{actions.map(({ href, icon: Icon, title, description }) => <Link className="lift rounded-xl border border-line bg-white p-6 hover:border-teal" href={href} key={href}><Icon className="text-teal" aria-hidden="true" /><h2 className="mt-5 font-display text-2xl font-semibold tracking-tight">{title}</h2><p className="mt-3 text-sm leading-6 text-slate-600">{description}</p><p className="mt-6 text-sm font-bold text-teal">Open workflow →</p></Link>)}</div></div></AppShell>;
}
