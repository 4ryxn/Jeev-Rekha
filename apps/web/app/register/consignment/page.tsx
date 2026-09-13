import { AppShell } from "@/components/app-shell";
import { RegisterOperationsForm } from "@/components/register-operations-form";
import { PageHeader } from "@/components/ui/page-header";

export default function RegisterConsignmentPage() { return <AppShell><div className="space-y-8"><PageHeader eyebrow="Core operations" title="Register" description="Record a livestock movement or a symptom and mortality report in the selected Data Context." /><RegisterOperationsForm /></div></AppShell>; }
