"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { ApiError } from "@/lib/api";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // no point retrying 4xx (expired token, not found...)
            retry: (count, error) =>
              !(error instanceof ApiError && error.status < 500) && count < 2,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
