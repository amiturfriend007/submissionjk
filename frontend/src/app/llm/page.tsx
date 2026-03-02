"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import api from "../../services/api";

type StatusPayload = {
  connected: boolean;
  llm_url?: string;
  llm_provider?: string;
  configured_model?: string;
  configured_model_ready?: boolean;
  available_models?: string[];
  error?: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function LLMChatPage() {
  const [status, setStatus] = useState<StatusPayload>({ connected: false });
  const [statusLoading, setStatusLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const statusTone = useMemo(() => {
    if (status.connected && status.configured_model_ready) return "text-green-700 bg-green-100";
    if (status.connected) return "text-amber-700 bg-amber-100";
    return "text-red-700 bg-red-100";
  }, [status.connected, status.configured_model_ready]);

  const loadStatus = async () => {
    try {
      const res = await api.get<StatusPayload>("/llm/status");
      setStatus(res.data);
    } catch (err: any) {
      setStatus({
        connected: false,
        error: err?.response?.data?.detail || err?.message || "Status check failed",
      });
    } finally {
      setStatusLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    const timer = setInterval(loadStatus, 10000);
    return () => clearInterval(timer);
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setError("");
    const nextMessages: Message[] = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setSending(true);

    try {
      const payload = {
        messages: [
          { role: "system", content: "You are a concise helpful assistant." },
          ...nextMessages.map((m) => ({ role: m.role, content: m.content })),
        ],
      };
      const res = await api.post<{ answer: string }>("/llm/chat", payload);
      setMessages([...nextMessages, { role: "assistant", content: res.data.answer }]);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Chat failed");
      setMessages(nextMessages);
    } finally {
      setSending(false);
      loadStatus();
    }
  };

  return (
    <main className="page-shell max-w-4xl">
      <section className="panel p-6">
      <h1 className="text-2xl font-bold mb-4">LLM Chat</h1>

      <div className={`inline-block px-3 py-1 rounded text-sm font-medium ${statusTone}`}>
        {statusLoading ? "Checking LLM..." : status.connected ? "LLM Connected" : "LLM Disconnected"}
      </div>

      <div className="mt-3 text-sm text-slate-700">
        <p>Provider: {status.llm_provider || "unknown"}</p>
        <p>LLM URL: {status.llm_url || "unknown"}</p>
        <p>Configured model: {status.configured_model || "unknown"}</p>
        <p>Model ready: {status.configured_model_ready ? "yes" : "no"}</p>
        {status.available_models && status.available_models.length > 0 && (
          <p>Available: {status.available_models.join(", ")}</p>
        )}
        {status.error && <p className="text-red-600">Error: {status.error}</p>}
      </div>

      <div className="mt-6 rounded-xl border border-slate-200 p-4 h-[420px] overflow-y-auto bg-white">
        {messages.length === 0 && (
          <p className="text-slate-500 text-sm">Start a conversation with the LLM.</p>
        )}
        <div className="space-y-3">
          {messages.map((msg, idx) => (
            <div
              key={`${msg.role}-${idx}`}
              className={`p-3 rounded text-sm whitespace-pre-wrap ${
                msg.role === "user" ? "bg-blue-50" : "bg-slate-100"
              }`}
            >
              <p className="font-medium mb-1">{msg.role === "user" ? "You" : "LLM"}</p>
              <p>{msg.content}</p>
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          className="input-field"
        />
        <button
          type="submit"
          disabled={sending}
          className="btn btn-primary disabled:opacity-50"
        >
          {sending ? "Sending..." : "Send"}
        </button>
      </form>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </section>
    </main>
  );
}
