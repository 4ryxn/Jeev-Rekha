import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Jeev Rekha | Operations Workspace",
  description: "Livestock outbreak intelligence and movement advisory workspace.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
