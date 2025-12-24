import "../src/styles/globals.css";
import type { Metadata } from "next";

import { AuthProvider } from "@/src/context/AuthContext";

export const metadata: Metadata = {
  title: "Photo Platform",
  description: "Multi-tenant photo processing platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <AuthProvider>
          <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
