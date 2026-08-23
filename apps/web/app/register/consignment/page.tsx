import { AppShell } from "@/components/app-shell";
import { RegisterConsignmentForm } from "@/components/register-consignment-form";
import { PageHeader } from "@/components/ui/page-header";

export default function RegisterConsignmentPage() { return <AppShell><div className="space-y-8"><PageHeader eyebrow="Core operations" title="Register consignment" description="Record a local synthetic livestock movement. The information is persisted locally; advisory evaluation uses the configured deterministic rules." /><RegisterConsignmentForm /></div></AppShell>; }
