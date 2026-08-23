import { AppShell } from "@/components/app-shell";
import { AdvisoryResult } from "@/components/advisory-result";
import { SafeCorridorByAdvisory } from "@/components/safe-corridor";
import { PageHeader } from "@/components/ui/page-header";

export default async function AdvisoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AppShell><div className="space-y-8"><PageHeader eyebrow="Movement advisory · Phase 4" title="Movement advisory" description="A deterministic, explainable result from local synthetic evidence records." /><AdvisoryResult advisoryId={Number(id)} /><SafeCorridorByAdvisory id={Number(id)} /></div></AppShell>;
}
