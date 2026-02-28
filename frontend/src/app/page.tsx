import BookCard from '../components/BookCard';
import { getBooks } from '../services/books';

export default async function Home() {
  const data = await getBooks();

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold mb-4">LuminaLib</h1>
      <div className="grid gap-4">
        {data?.items.map((book: any) => (
          <BookCard
            key={book.id}
            title={book.title}
            author={book.author}
            summary={book.summary}
          />
        ))}
      </div>
    </main>
  );
}