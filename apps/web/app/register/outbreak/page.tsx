import { AppShell } from "@/components/app-shell";
import { RegisterOutbreakForm } from "@/components/register-outbreak-form";
import { PageHeader } from "@/components/ui/page-header";

export default function RegisterOutbreakPage() { return <AppShell><div className="space-y-8"><PageHeader eyebrow="Core operations" title="Record outbreak evidence" description="Create an outbreak record in the selected Data Context. Verification and status remain visible; this is not a legal notification workflow." /><RegisterOutbreakForm /></div></AppShell>; }
