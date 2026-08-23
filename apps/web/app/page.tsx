import { AppShell } from "@/components/app-shell";
import { DashboardContent } from "@/components/dashboard-content";
import { DashboardMapPreview } from "@/components/dashboard-map-preview";
import { TraceActivity } from "@/components/trace-activity";
import { ContainmentActivity } from "@/components/containment-activity";
import { PageHeader } from "@/components/ui/page-header";

export default function DashboardPage() {
  return <AppShell>
    <div className="space-y-8">
      <PageHeader eyebrow="Operations workspace" title="Situation brief" description="A live view of the local PostGIS-backed synthetic demonstration data. No live INAPH, NADRES, IDSP, or government data is connected." />
      <DashboardContent />
      <DashboardMapPreview />
      <TraceActivity />
      <ContainmentActivity />
    </div>
  </AppShell>;
}
