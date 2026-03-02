"use client";

import "./globals.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { AuthProvider } from "../context/AuthContext";

export default function RootLayout({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <html lang="en">
      <body>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/85 backdrop-blur">
              <nav className="page-shell !py-3 flex flex-wrap items-center gap-2">
                <a href="/" className="mr-2 rounded-full bg-slate-900 px-3 py-1.5 text-sm font-semibold text-white">
                  LuminaLib
                </a>
                <a href="/" className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                  Home
                </a>
                <a href="/books/new" className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                  Upload
                </a>
                <a href="/llm" className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                  LLM Chat
                </a>
                <a href="/auth/profile" className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                  Profile
                </a>
                <a href="/auth/login" className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                  Login
                </a>
                <a href="/auth/signup" className="rounded-full bg-sky-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-sky-800">
                  Sign Up
                </a>
              </nav>
            </header>
            {children}
          </AuthProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
