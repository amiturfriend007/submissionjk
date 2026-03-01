"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

type PendingSummaryRefresherProps = {
  hasPending: boolean;
};

export default function PendingSummaryRefresher({ hasPending }: PendingSummaryRefresherProps) {
  const router = useRouter();

  useEffect(() => {
    if (!hasPending) return;
    const timer = setTimeout(() => {
      router.refresh();
    }, 5000);
    return () => clearTimeout(timer);
  }, [hasPending, router]);

  return null;
}
