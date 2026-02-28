import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import axios from 'axios';
import { useBooks } from '../useBooks';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('useBooks', () => {
  it('fetches books', async () => {
    const booksData = { items: [{ id: 1, title: 'A' }], page: 1 };
    mockedAxios.get.mockResolvedValue({ data: booksData });

    const queryClient = new QueryClient();
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result, waitFor } = renderHook(() => useBooks(1), { wrapper });
    await waitFor(() => result.current.isSuccess);
    expect(result.current.data).toEqual(booksData);
  });
});