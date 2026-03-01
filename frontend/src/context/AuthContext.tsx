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
    const normalizedEmail = email.trim();
    if (!normalizedEmail || !password) {
      throw new Error("Email and password are required");
    }

    let data: { access_token?: string };
    try {
      const res = await api.post("/auth/login", {
        email: normalizedEmail,
        password,
      });
      data = res.data;
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "Login failed";
      throw new Error(typeof detail === "string" ? detail : "Login failed");
    }
    if (!data?.access_token) {
      throw new Error("Login failed: access token missing");
    }

    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  };
 
//  const login = async (email: string, password: string) => {
//   const params = new URLSearchParams();
//   params.append("username", email); // OAuth2 expects "username"
//   params.append("password", password);

//   const res = await api.post("/auth/login", params, {
//     headers: {
//       "Content-Type": "application/x-www-form-urlencoded",
//     },
//   });

//   const data = res.data;
//   if (!data?.access_token) {
//     throw new Error("Login failed: access token missing");
//   }

//   localStorage.setItem("token", data.access_token);
//   setToken(data.access_token);
// };

// const login = async (email: string, password: string) => {
//   const body = new URLSearchParams();
//   body.append("username", email);
//   body.append("password", password);

//   const res = await api.post(
//     "/auth/login",
//     body.toString(), // 👈 important
//     {
//       headers: {
//         "Content-Type": "application/x-www-form-urlencoded",
//       },
//     }
//   );

//   const data = res.data;
//   localStorage.setItem("token", data.access_token);
//   setToken(data.access_token);
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
