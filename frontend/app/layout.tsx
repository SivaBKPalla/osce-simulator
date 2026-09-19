import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-serif",
});

const ibmPlexSans = IBM_Plex_Sans({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "OSCE Station — Clinical Reasoning Simulator",
  description: "Practice history taking and differentials with a virtual standardized patient.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${fraunces.variable} ${ibmPlexSans.variable}`}>
      <body>
        <div className="min-h-screen">
          <header className="border-b border-black/10 bg-ink text-paper">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <div>
                <p className="text-[11px] uppercase tracking-[0.28em] text-clinic-soft/80">
                  Clinical Skills Centre
                </p>
                <p className="font-serif text-xl tracking-tight">OSCE Station Simulator</p>
              </div>
              <p className="hidden text-sm text-paper/70 sm:block">History taking · 8 minutes</p>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
        </div>
      </body>
    </html>
  );
}
