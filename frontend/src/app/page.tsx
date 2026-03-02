import BookCard from '../components/BookCard';
import PendingSummaryRefresher from '../components/PendingSummaryRefresher';
import RecommendedBooks from '../components/RecommendedBooks';
import { getBooks } from '../services/books';

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function Home() {
  const data = await getBooks();
  const items = data?.items || [];
  const hasPending = items.some((book: any) => book.summary_status === "pending");

  return (
    <main className="page-shell">
      <PendingSummaryRefresher hasPending={hasPending} />
      <div className="mb-5">
        <h1 className="text-3xl font-bold tracking-tight">LuminaLib</h1>
        <p className="mt-1 text-sm text-slate-600">Discover, review, and get AI-powered recommendations.</p>
      </div>
      <RecommendedBooks />
      <div className="grid gap-5">
        {items.length === 0 && (
          <p className="panel p-5 text-slate-600">No books found. Upload a book to get started.</p>
        )}
        {items.map((book: any) => (
          <BookCard
            key={book.id}
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
    </main>
  );
}
