"use client";

import { useState, useEffect } from "react";
import api from "../../../services/api";
import { useAuth } from "../../../context/AuthContext";

export default function ProfilePage() {
  const { token, logout } = useAuth();
  const [user, setUser] = useState<any>(null);
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      api.get("/auth/me").then((res) => setUser(res.data));
    }
  }, [token]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.put("/auth/me", { full_name: fullName });
      setUser(res.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Update failed");
    }
  };

  if (!token) return <main className="page-shell"><p className="panel p-5 text-slate-600">Please log in first.</p></main>;

  return (
    <main className="page-shell max-w-xl">
      <section className="panel p-6">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      {user && (
        <div className="mb-4 text-slate-700">
          <p>Email: {user.email}</p>
          <p>Name: {user.full_name || "(none)"}</p>
        </div>
      )}
      <form onSubmit={handleUpdate} className="space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="input-field"
        />
        {error && <p className="text-red-600">{error}</p>}
        <button type="submit" className="btn btn-primary">
          Update
        </button>
      </form>
      <button onClick={logout} className="mt-4 text-sm font-medium text-red-700">
        Sign out
      </button>
      </section>
    </main>
  );
}
