import { useSyncExternalStore } from "react";
import { getToken, subscribeToken } from "./api";

export function useToken(): string | null | undefined {
  return useSyncExternalStore(subscribeToken, getToken, () => undefined);
}
