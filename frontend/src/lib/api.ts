const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

const TOKEN_KEY = "briefbase_token";
const AUTH_EVENT = "briefbase-auth";

export type Note = {
  id: number;
  title: string | null;
  content: string;
  summary: string | null;
  tags: string[];
  created_at: string;
};

export type User = {
  id: number;
  email: string;
};

type TokenResponse = { access_token: string; token_type: string };

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

// token storage

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
  window.dispatchEvent(new Event(AUTH_EVENT));
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event(AUTH_EVENT));
}

export function subscribeToken(callback: () => void) {
  window.addEventListener(AUTH_EVENT, callback);
  window.addEventListener("storage", callback);
  return () => {
    window.removeEventListener(AUTH_EVENT, callback);
    window.removeEventListener("storage", callback);
  };
}

// requests

async function errorMessage(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return body.detail;

    if (Array.isArray(body.detail)) return body.detail.map((d: { msg: string }) => d.msg).join(", ");
  } catch {
    // not json
  }
  return `Request failed (${res.status})`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    throw new ApiError(res.status, await errorMessage(res));
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  register: (email: string, password: string) =>
    request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>("/auth/me"),

  listNotes: (tag: string | null) =>
    request<Note[]>(tag ? `/notes?tag=${encodeURIComponent(tag)}` : "/notes"),

  createNote: (data: { title?: string; content: string }) =>
    request<Note>("/notes", { method: "POST", body: JSON.stringify(data) }),

  resummarizeNote: (id: number) => request<Note>(`/notes/${id}/summarize`, { method: "POST" }),

  deleteNote: (id: number) => request<void>(`/notes/${id}`, { method: "DELETE" }),
};
