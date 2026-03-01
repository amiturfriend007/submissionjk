"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  borrowBook,
  createReview,
  deleteBook,
  getBookDownloadUrl,
  getBookViewUrl,
  refreshBookSummary,
  returnBook,
} from "../services/books";

type BookCardProps = {
  id: number;
  title: string;
  author?: string;
  summary?: string;
  summaryStatus?: "pending" | "ready" | "failed";
  currentBorrower?: string | null;
  previousReviews?: {
    reviewer: string;
    rating: number;
    comment: string;
  }[];
};

export default function BookCard({
  id,
  title,
  author,
  summary,
  summaryStatus,
  currentBorrower,
  previousReviews = [],
}: BookCardProps) {
  const router = useRouter();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [refreshingSummary, setRefreshingSummary] = useState(false);

  const handleBorrow = async () => {
    setError("");
    setMessage("");
    try {
      await borrowBook(id);
      setMessage("Book borrowed.");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Unable to borrow book.");
    }
  };

  const handleReturn = async () => {
    setError("");
    setMessage("");
    try {
      await returnBook(id);
      setMessage("Book returned.");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Unable to return book.");
    }
  };

  const handleReview = async () => {
    setError("");
    setMessage("");
    try {
      await createReview({ bookId: id, rating, comment });
      setMessage("Review submitted.");
      setComment("");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Unable to submit review.");
    }
  };

  const handleDelete = async () => {
    const confirmed = window.confirm(`Delete "${title}"? This cannot be undone.`);
    if (!confirmed) return;

    setError("");
    setMessage("");
    setDeleting(true);
    try {
      await deleteBook(id);
      router.refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Unable to delete book.");
    } finally {
      setDeleting(false);
    }
  };

  const handleRefreshSummary = async () => {
    setError("");
    setMessage("");
    setRefreshingSummary(true);
    try {
      await refreshBookSummary(id);
      setMessage("Summary refresh requested.");
      router.refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Unable to refresh summary.");
    } finally {
      setRefreshingSummary(false);
    }
  };

  return (
    <div className="p-4 border rounded shadow-sm">
      <h2 className="text-xl font-semibold">{title}</h2>
      {author && <p className="text-sm text-gray-600">by {author}</p>}
      {summaryStatus === "pending" && (
        <p className="mt-2 text-sm text-amber-700">Summary is being generated...</p>
      )}
      {summaryStatus === "failed" && (
        <p className="mt-2 text-sm text-red-600">Summary generation failed.</p>
      )}
      {summary && <p className="mt-2 text-gray-800">{summary}</p>}
      <p className="mt-2 text-sm text-gray-700">
        {currentBorrower ? `Currently borrowed by: ${currentBorrower}` : "Currently available"}
      </p>

      <div className="mt-4 flex gap-2">
        <button onClick={handleBorrow} className="px-3 py-1 bg-blue-600 text-white rounded">
          Borrow
        </button>
        <button onClick={handleReturn} className="px-3 py-1 bg-gray-700 text-white rounded">
          Return
        </button>
        <a
          href={getBookViewUrl(id)}
          target="_blank"
          rel="noreferrer"
          className="px-3 py-1 bg-indigo-600 text-white rounded"
        >
          View
        </a>
        <a
          href={getBookDownloadUrl(id)}
          download
          className="px-3 py-1 bg-slate-800 text-white rounded"
        >
          Download
        </a>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="px-3 py-1 bg-red-700 text-white rounded disabled:opacity-50"
        >
          {deleting ? "Deleting..." : "Delete"}
        </button>
        {(summaryStatus === "failed" || summaryStatus === "pending") && (
          <button
            onClick={handleRefreshSummary}
            disabled={refreshingSummary}
            className="px-3 py-1 bg-amber-600 text-white rounded disabled:opacity-50"
          >
            {refreshingSummary ? "Retrying..." : "Retry Summary"}
          </button>
        )}
      </div>

      <div className="mt-4 space-y-2">
        <p className="text-sm font-medium">Previous comments</p>
        {previousReviews.length === 0 && (
          <p className="text-sm text-gray-500">No comments yet.</p>
        )}
        {previousReviews.map((review, idx) => (
          <div key={`${id}-review-${idx}`} className="rounded border p-2 text-sm">
            <p className="text-gray-800">{review.comment}</p>
            <p className="mt-1 text-gray-600">
              {review.reviewer} - {review.rating}/5
            </p>
          </div>
        ))}
      </div>

      <div className="mt-4 space-y-2">
        <label className="block text-sm font-medium">Review</label>
        <select
          value={rating}
          onChange={(e) => setRating(Number(e.target.value))}
          className="p-2 border rounded"
        >
          <option value={1}>1</option>
          <option value={2}>2</option>
          <option value={3}>3</option>
          <option value={4}>4</option>
          <option value={5}>5</option>
        </select>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Optional comment"
          className="w-full p-2 border rounded"
          rows={2}
        />
        <button onClick={handleReview} className="px-3 py-1 bg-green-600 text-white rounded">
          Submit Review
        </button>
      </div>

      {message && <p className="mt-3 text-sm text-green-700">{message}</p>}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}
