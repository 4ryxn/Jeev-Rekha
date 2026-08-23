import type { Metadata, Viewport } from "next";

import "./globals.css";
import { PwaRegistration } from "@/components/pwa-registration";

export const metadata: Metadata = {
  title: "Jeev Rekha | Operations Workspace",
  description: "Livestock outbreak intelligence and movement advisory workspace.",
  manifest: "/manifest.webmanifest",
};
export const viewport: Viewport = { themeColor: "#0f766e" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><PwaRegistration />{children}</body>
    </html>
  );
}
