"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createBook } from "../../../services/books";

export default function NewBookPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    if (!file) {
      setError("Please choose a .txt or .pdf file.");
      return;
    }

    const ext = file.name.toLowerCase().split(".").pop();
    if (ext !== "txt" && ext !== "pdf") {
      setError("Only .txt and .pdf files are supported.");
      return;
    }

    setSubmitting(true);
    try {
      await createBook({
        title: title.trim(),
        author: author.trim() || undefined,
        description: description.trim() || undefined,
        file,
      });
      router.push("/");
      router.refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to upload book.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Upload Book</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
          className="w-full p-2 border rounded"
        />
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="Author (optional)"
          className="w-full p-2 border rounded"
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          className="w-full p-2 border rounded"
          rows={3}
        />
        <input
          type="file"
          accept=".txt,.pdf,text/plain,application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="w-full p-2 border rounded"
        />

        {error && <p className="text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {submitting ? "Uploading..." : "Upload"}
        </button>
      </form>
    </main>
  );
}
