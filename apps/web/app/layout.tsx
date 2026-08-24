import type { Metadata, Viewport } from "next";

import "./globals.css";
import "leaflet/dist/leaflet.css";
import { PwaRegistration } from "@/components/pwa-registration";

export const metadata: Metadata = {
  title: { default: "Jeev Rekha | Operations Workspace", template: "%s | Jeev Rekha" },
  description: "Explainable livestock movement advisory and outbreak operations workspace using synthetic and clearly labelled pilot data.",
  manifest: "/manifest.webmanifest",
  applicationName: "Jeev Rekha",
  openGraph: {
    title: "Jeev Rekha",
    description: "Explainable livestock movement advisory and outbreak operations workspace.",
    type: "website",
  },
  twitter: { card: "summary", title: "Jeev Rekha", description: "Explainable livestock movement advisory workspace." },
};
export const viewport: Viewport = { themeColor: "#0f766e", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><PwaRegistration />{children}</body>
    </html>
  );
}
