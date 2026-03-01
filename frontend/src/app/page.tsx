import BookCard from '../components/BookCard';
import PendingSummaryRefresher from '../components/PendingSummaryRefresher';
import { getBooks } from '../services/books';

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function Home() {
  const data = await getBooks();
  const items = data?.items || [];
  const hasPending = items.some((book: any) => book.summary_status === "pending");

  return (
    <main className="p-8">
      <PendingSummaryRefresher hasPending={hasPending} />
      <h1 className="text-3xl font-bold mb-4">LuminaLib</h1>
      <div className="grid gap-4">
        {items.length === 0 && (
          <p className="text-gray-600">No books found. Upload a book to get started.</p>
        )}
        {items.map((book: any) => (
          <BookCard
            key={book.id}
            id={book.id}
            title={book.title}
            author={book.author}
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
