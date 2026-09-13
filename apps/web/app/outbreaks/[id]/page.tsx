import { AppShell } from "@/components/app-shell";
import { OutbreakDetail } from "@/components/outbreak-detail";
import { PageHeader } from "@/components/ui/page-header";

export default async function OutbreakPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AppShell><div className="space-y-8"><PageHeader eyebrow="Core operations" title="Outbreak detail" description="Persisted outbreak evidence with read-only environmental context." /><OutbreakDetail outbreakId={Number(id)} /></div></AppShell>;
}
