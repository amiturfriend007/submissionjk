import { render, screen } from "@testing-library/react";
import BookCard from "../BookCard";

test("renders title and author", () => {
  render(<BookCard title="Test Book" author="Jane Doe" />);
  expect(screen.getByText(/Test Book/)).toBeInTheDocument();
  expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
});

test("renders summary when provided", () => {
  render(<BookCard title="Another" summary="This is a summary." />);
  expect(screen.getByText(/This is a summary./)).toBeInTheDocument();
});