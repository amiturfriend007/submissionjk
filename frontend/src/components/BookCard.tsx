"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  borrowBook,
  createReview,
  deleteBook,
  getBookAnalysis,
  getBookDownloadUrl,
  getBookViewUrl,
  refreshBookSummary,
  returnBook,
} from "../services/books";

type BookCardProps = {
  id: number;
  title: string;
  author?: string;
  description?: string;
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
  description,
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
  const [analysis, setAnalysis] = useState<{ average_sentiment: number | null; review_count: number }>({
    average_sentiment: null,
    review_count: 0,
  });

  const consensusText = useMemo(() => {
    const raw = description || "";
    const marker = "Consensus Summary:\n";
    const idx = raw.indexOf(marker);
    if (idx === -1) return "";
    return raw.slice(idx + marker.length).trim();
  }, [description]);

  const sentimentBadge = useMemo(() => {
    const score = analysis.average_sentiment;
    if (score === null || Number.isNaN(score)) {
      return {
        label: "Trend: Unknown",
        className: "bg-gray-200 text-gray-700",
      };
    }
    if (score >= 0.2) {
      return {
        label: "Trend: Positive",
        className: "bg-green-100 text-green-700",
      };
    }
    if (score <= -0.2) {
      return {
        label: "Trend: Negative",
        className: "bg-red-100 text-red-700",
      };
    }
    return {
      label: "Trend: Neutral",
      className: "bg-amber-100 text-amber-700",
    };
  }, [analysis.average_sentiment]);

  const loadAnalysis = async () => {
    try {
      const data = await getBookAnalysis(id);
      setAnalysis(data);
    } catch {
      // keep UI resilient when analysis is temporarily unavailable
    }
  };

  useEffect(() => {
    loadAnalysis();
  }, [id]);

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
      await loadAnalysis();
      router.refresh();
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
    <div className="panel p-5">
      <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
      {author && <p className="text-sm text-slate-600">by {author}</p>}
      {summaryStatus === "pending" && (
        <p className="mt-2 text-sm text-amber-700">Summary is being generated...</p>
      )}
      {summaryStatus === "failed" && (
        <p className="mt-2 text-sm text-red-600">Summary generation failed.</p>
      )}
      {summary && <p className="mt-2 text-slate-800 leading-relaxed">{summary}</p>}

      <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm">
        <p className="font-medium text-slate-800">Rolling Consensus</p>
        <span className={`inline-block mt-2 rounded px-2 py-1 text-xs font-medium ${sentimentBadge.className}`}>
          {sentimentBadge.label}
        </span>
        <p className="text-slate-700">
          Reviews analyzed: {analysis.review_count} | Average sentiment:{" "}
          {analysis.average_sentiment === null ? "N/A" : analysis.average_sentiment.toFixed(2)}
        </p>
        {consensusText ? (
          <p className="mt-1 whitespace-pre-wrap text-slate-700">{consensusText}</p>
        ) : (
          <p className="mt-1 text-slate-500">Consensus will appear as reviews come in.</p>
        )}
      </div>

      <p className="mt-2 text-sm text-slate-700">
        {currentBorrower ? `Currently borrowed by: ${currentBorrower}` : "Currently available"}
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <button onClick={handleBorrow} className="btn btn-primary">
          Borrow
        </button>
        <button onClick={handleReturn} className="btn btn-secondary">
          Return
        </button>
        <a
          href={getBookViewUrl(id)}
          target="_blank"
          rel="noreferrer"
          className="btn bg-indigo-700 text-white"
        >
          View
        </a>
        <a
          href={getBookDownloadUrl(id)}
          download
          className="btn bg-slate-800 text-white"
        >
          Download
        </a>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="btn btn-danger disabled:opacity-50"
        >
          {deleting ? "Deleting..." : "Delete"}
        </button>
        {(summaryStatus === "failed" || summaryStatus === "pending") && (
          <button
            onClick={handleRefreshSummary}
            disabled={refreshingSummary}
            className="btn btn-warning disabled:opacity-50"
          >
            {refreshingSummary ? "Retrying..." : "Retry Summary"}
          </button>
        )}
      </div>

      <div className="mt-4 space-y-2">
        <p className="text-sm font-medium">Previous comments</p>
        {previousReviews.length === 0 && (
          <p className="text-sm text-slate-500">No comments yet.</p>
        )}
        {previousReviews.map((review, idx) => (
          <div key={`${id}-review-${idx}`} className="rounded-lg border border-slate-200 bg-white p-2 text-sm">
            <p className="text-slate-800">{review.comment}</p>
            <p className="mt-1 text-slate-600">
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
          className="input-field"
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
          className="input-field"
          rows={2}
        />
        <button onClick={handleReview} className="btn bg-emerald-700 text-white">
          Submit Review
        </button>
      </div>

      {message && <p className="mt-3 text-sm text-emerald-700">{message}</p>}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}
