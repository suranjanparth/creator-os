import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppNavigation } from "@/components/AppNavigation";

import "./globals.css";

export const metadata: Metadata = {
  title: "CREATOR OS",
  description: "Creator Intelligence, Strategy and Content Operating System",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <main className="shell">
          <AppNavigation />
          {children}
        </main>
      </body>
    </html>
  );
}
