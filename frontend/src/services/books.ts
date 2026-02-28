import api from './api';

export async function getBooks(page = 1) {
  const { data } = await api.get(`/books?page=${page}`);
  return data;
}
