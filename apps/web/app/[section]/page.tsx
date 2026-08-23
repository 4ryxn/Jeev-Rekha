import { AppShell } from "@/components/app-shell";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";

const content: Record<string, { title: string; description: string; emptyTitle: string; emptyDescription: string }> = {
  trace: { title: "Trace Lab", description: "A workspace for transparent outbreak rewind and fast-forward review.", emptyTitle: "Start a persisted trace", emptyDescription: "Select Rewind contacts or Fast-forward exposure to create a persisted trace." },
  reports: { title: "Reports", description: "Field-usable movement and veterinary reports will be assembled once verified workflow data exists.", emptyTitle: "Reports unavailable", emptyDescription: "No report workflow is available in this local synthetic workspace." },
  "review-queue": { title: "Review Queue", description: "Veterinary review preserves source evidence and makes conflicts visible.", emptyTitle: "Review Queue unavailable", emptyDescription: "No review-queue workflow is available in this local synthetic workspace." },
  settings: { title: "Settings", description: "Workspace configuration and data-status controls.", emptyTitle: "Settings unavailable", emptyDescription: "No authenticated settings workflow is available in this local synthetic workspace." },
};

export default async function PlaceholderPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  const item = content[section] ?? { title: "Workspace", description: "This area has not been configured.", emptyTitle: "This area is unavailable", emptyDescription: "No workflow is available at this address." };
  return <AppShell><div className="space-y-8"><PageHeader title={item.title} description={item.description} eyebrow="Operations workspace" /><EmptyState title={item.emptyTitle} description={item.emptyDescription} /></div></AppShell>;
}
