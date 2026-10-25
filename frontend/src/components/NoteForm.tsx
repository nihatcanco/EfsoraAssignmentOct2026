"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";

export function NoteForm() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const createNote = useMutation({
    mutationFn: api.createNote,
    onSuccess: () => {
      setTitle("");
      setContent("");
      return queryClient.invalidateQueries({ queryKey: ["notes"] });
    },
  });

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    createNote.mutate({ title: title || undefined, content });
  }

  return (
    <form onSubmit={onSubmit}>
      <h2>New note</h2>
      <input placeholder="Title (optional)" value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea
        placeholder="Note"
        rows={6}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        required
      />
      {createNote.error && <p className="error">{createNote.error.message}</p>}
      <button type="submit" disabled={createNote.isPending || !content.trim()}>
        {createNote.isPending ? "Saving & summarizing..." : "Save note"}
      </button>
    </form>
  );
}
