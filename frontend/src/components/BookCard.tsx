type BookCardProps = {
  title: string;
  author?: string;
  summary?: string;
};

export default function BookCard({ title, author, summary }: BookCardProps) {
  return (
    <div className="p-4 border rounded shadow-sm">
      <h2 className="text-xl font-semibold">{title}</h2>
      {author && <p className="text-sm text-gray-600">by {author}</p>}
      {summary && <p className="mt-2 text-gray-800">{summary}</p>}
    </div>
  );
}