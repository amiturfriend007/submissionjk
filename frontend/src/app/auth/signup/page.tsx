"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "../../../services/api";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/auth/signup", {
        email: email.trim(),
        password,
        full_name: fullName.trim() || undefined,
      });
      router.push("/auth/login");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Signup failed");
    }
  };

  return (
    <main className="page-shell max-w-xl">
      <section className="panel p-6">
      <h1 className="text-2xl font-bold mb-1">Sign Up</h1>
      <p className="text-sm text-slate-600 mb-4">Create your account to start borrowing and reviewing books.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input-field"
        />
        <input
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="input-field"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="input-field"
        />
        {error && <p className="text-red-600">{error}</p>}
        <button type="submit" className="btn btn-primary">
          Sign Up
        </button>
      </form>
      </section>
    </main>
  );
}
