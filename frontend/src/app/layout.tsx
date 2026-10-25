import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "BriefBase",
  description: "Notes with AI summaries and tags",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
