import api from './api';
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Book = {
  id: number;
  title: string;
  author?: string;
  description?: string;
  summary?: string;
  summary_status?: "pending" | "ready" | "failed";
  current_borrower?: string | null;
  recent_reviews?: {
    reviewer: string;
    rating: number;
    comment: string;
  }[];
};

export type BookListResponse = {
  items: Book[];
  page: number;
};

export type RecommendationResponse = {
  items: Book[];
};

export type BookAnalysis = {
  average_sentiment: number | null;
  review_count: number;
};

export async function getBooks(page = 1) {
  const { data } = await api.get<BookListResponse>(`/books/?page=${page}`);
  return data;
}

export async function getRecommendations() {
  const { data } = await api.get<RecommendationResponse>(`/books/recommendations`);
  return data;
}

export async function createBook(params: {
  title: string;
  author?: string;
  description?: string;
  file: File;
}) {
  const formData = new FormData();
  formData.append("title", params.title);
  if (params.author) formData.append("author", params.author);
  if (params.description) formData.append("description", params.description);
  formData.append("file", params.file);

  const { data } = await api.post<Book>("/books/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

export async function borrowBook(bookId: number) {
  const { data } = await api.post(`/books/${bookId}/borrow`);
  return data;
}

export async function returnBook(bookId: number) {
  const { data } = await api.post(`/books/${bookId}/return`);
  return data;
}

export async function createReview(params: {
  bookId: number;
  rating: number;
  comment?: string;
}) {
  const { data } = await api.post(`/books/${params.bookId}/reviews`, {
    rating: params.rating,
    comment: params.comment || null,
  });
  return data;
}

export async function getBookAnalysis(bookId: number) {
  const { data } = await api.get<BookAnalysis>(`/books/${bookId}/analysis`);
  return data;
}

export async function deleteBook(bookId: number) {
  await api.delete(`/books/${bookId}`);
}

export async function refreshBookSummary(bookId: number) {
  const { data } = await api.post(`/books/${bookId}/summary/refresh`);
  return data;
}

export function getBookDownloadUrl(bookId: number) {
  return `${API_BASE}/books/${bookId}/download`;
}

export function getBookViewUrl(bookId: number) {
  return `${API_BASE}/books/${bookId}/view`;
}
