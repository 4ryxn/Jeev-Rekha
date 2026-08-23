import type { ReactNode } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return <div className="min-h-screen bg-paper md:flex"><Sidebar /><div className="min-w-0 flex-1"><Topbar /><main className="mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-9">{children}</main></div></div>;
}
