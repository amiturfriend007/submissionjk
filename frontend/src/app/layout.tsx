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
          <header className="p-4 bg-gray-100 shadow">
            <nav className="max-w-4xl mx-auto flex space-x-4">
              <a href="/" className="font-semibold">
                Home
              </a>
              <a href="/auth/login" className="text-blue-600">
                Login
              </a>
              <a href="/auth/signup" className="text-blue-600">
                Sign Up
              </a>
              <a href="/auth/profile" className="text-blue-600">
                Profile
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
