"use client";

import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { NoteForm } from "@/components/NoteForm";
import { NoteItem } from "@/components/NoteItem";
import { api, ApiError, clearToken } from "@/lib/api";
import { useToken } from "@/lib/useToken";

export default function NotesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const token = useToken();
  const [tag, setTag] = useState<string | null>(null);
  const [tagInput, setTagInput] = useState("");

  const me = useQuery({ queryKey: ["me"], queryFn: api.me, enabled: !!token });
  const notes = useQuery({
    queryKey: ["notes", tag],
    queryFn: () => api.listNotes(tag),
    enabled: !!token,
    placeholderData: keepPreviousData,
  });

  // filter as the user types, but wait for a pause before hitting the API
  useEffect(() => {
    const id = setTimeout(() => setTag(normalizeTag(tagInput)), 300);
    return () => clearTimeout(id);
  }, [tagInput]);

  const unauthorized = [me.error, notes.error].some((e) => e instanceof ApiError && e.status === 401);

  useEffect(() => {
    if (unauthorized) clearToken();
  }, [unauthorized]);

  useEffect(() => {
    if (token === null) {
      queryClient.clear();
      router.replace("/login");
    }
  }, [token, router, queryClient]);

  function applyTag(t: string | null) {
    setTag(t);
    setTagInput(t ?? "");
  }

  if (!token) return null;

  return (
    <>
      <header>
        <h1>BriefBase</h1>
        <div>
          <span className="muted">{me.data?.email} </span>
          <button onClick={clearToken}>Log out</button>
        </div>
      </header>

      <NoteForm />

      <h2>Your notes</h2>
      <form className="filter" onSubmit={(e) => e.preventDefault()}>
        <input
          placeholder="Filter by tag"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
        />
        {tagInput && (
          <button type="button" onClick={() => applyTag(null)}>
            Clear
          </button>
        )}
      </form>
      {tag && (
        <p>
          Showing notes with tags containing <strong>{tag}</strong>
        </p>
      )}

      {notes.isPending && <p>Loading...</p>}
      {notes.error && !unauthorized && <p className="error">{notes.error.message}</p>}
      {notes.data?.length === 0 && (
        <p className="muted">{tag ? `No tags contain "${tag}".` : "No notes yet."}</p>
      )}

      {notes.data?.map((note) => (
        <NoteItem
          key={note.id}
          note={note}
          activeTag={tag}
          onTagClick={(t) => applyTag(t === tag ? null : t)}
        />
      ))}
    </>
  );
}

function normalizeTag(input: string): string | null {
  return input.trim().replace(/^#/, "").toLowerCase() || null;
}
