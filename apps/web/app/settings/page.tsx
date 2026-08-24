import type { Metadata } from "next";
import{AppShell}from"@/components/app-shell";import{WorkspaceSettings}from"@/components/workspace-settings";import{PageHeader}from"@/components/ui/page-header";
export const metadata: Metadata = { title: "Workspace Settings" };
export default function SettingsPage(){return <AppShell><div className="space-y-8"><PageHeader eyebrow="Local workspace" title="Workspace Settings" description="Inspect this local synthetic workspace and choose device-only display preferences."/><WorkspaceSettings/></div></AppShell>}
