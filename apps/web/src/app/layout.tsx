import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Radar Tech IA",
  description: "Briefing diario de IA, tecnologia e artigos academicos.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
