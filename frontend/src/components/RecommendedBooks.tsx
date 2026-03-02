"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Book, getRecommendations } from "../services/books";
import BookCard from "./BookCard";

export default function RecommendedBooks() {
  const { token } = useAuth();
  const [items, setItems] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      if (!token) {
        setItems([]);
        setError("");
        return;
      }
      setLoading(true);
      setError("");
      try {
        const data = await getRecommendations();
        setItems(data.items || []);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Unable to load recommendations.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [token]);

  if (!token) {
    return (
      <section className="panel mb-8 p-5">
        <h2 className="text-2xl font-semibold mb-1">Recommended for You</h2>
        <p className="text-sm text-slate-600">Login and review books to get personalized recommendations.</p>
      </section>
    );
  }

  return (
    <section className="panel mb-8 p-5">
      <h2 className="text-2xl font-semibold mb-2">Recommended for You</h2>
      {loading && <p className="text-sm text-slate-600">Loading recommendations...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!loading && !error && items.length === 0 && (
        <p className="text-sm text-slate-600">No recommendations yet. Add a few ratings first.</p>
      )}
      {!loading && !error && items.length > 0 && (
        <div className="grid gap-4">
          {items.map((book) => (
            <BookCard
              key={`recommended-${book.id}`}
              id={book.id}
              title={book.title}
              author={book.author}
              description={book.description}
              summary={book.summary}
              summaryStatus={book.summary_status}
              currentBorrower={book.current_borrower}
              previousReviews={book.recent_reviews}
            />
          ))}
        </div>
      )}
    </section>
  );
}
