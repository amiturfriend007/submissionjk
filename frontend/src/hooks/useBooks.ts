import { useQuery } from '@tanstack/react-query';
import { getBooks } from '../services/books';

export function useBooks(page = 1) {
  return useQuery({
    queryKey: ['books', page],
    queryFn: () => getBooks(page),
  });
}