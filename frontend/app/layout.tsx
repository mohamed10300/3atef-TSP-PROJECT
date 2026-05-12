import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "3atef — Event Intelligence",
  description: "AI-powered event & hotel profitability intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
