"use client";
import { createContext, useState, useContext, ReactNode, useEffect } from "react";
import api from "../services/api";

interface AuthContextType {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) setToken(t);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencode d",
        },
        body:
          `username=${encodeURIComponent(email)}` +
          `&password=${encodeURIComponent(password)}`,
      }
    );

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  };
// const login = async (email: string, password: string) => {
//   const res = await fetch("http://localhost:8000/auth/login", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/x-www-form-urlencoded",
//     },
//     body: "username=user@example.com&password=1234",
//   });

//   console.log("STATUS", res.status);
//   console.log("TEXT", await res.text());
// };
  
  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    delete api.defaults.headers.common["Authorization"];
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}