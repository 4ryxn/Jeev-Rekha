import { AppShell } from "@/components/app-shell";
import { MapAdvisoriesContent } from "@/components/map-advisories-content";
import { PageHeader } from "@/components/ui/page-header";

export default function MapAdvisoriesPage() {
  return <AppShell><div className="space-y-8"><PageHeader eyebrow="Operations workspace" title="Map & Advisories" description="Review active fictional outbreak context, persisted movement advisories, and controlled route assessments." /><MapAdvisoriesContent /></div></AppShell>;
}
