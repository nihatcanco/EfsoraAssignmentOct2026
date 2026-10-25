"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type Note } from "@/lib/api";

type Props = {
  note: Note;
  activeTag: string | null;
  onTagClick: (tag: string) => void;
};

export function NoteItem({ note, activeTag, onTagClick }: Props) {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["notes"] });

  const deleteNote = useMutation({ mutationFn: api.deleteNote, onSuccess: invalidate });
  const resummarize = useMutation({ mutationFn: api.resummarizeNote, onSuccess: invalidate });

  const error = deleteNote.error ?? resummarize.error;

  const handleDelete = () => {
    if (window.confirm(`Delete "${note.title ?? "Untitled"}"? This can't be undone.`)) {
      deleteNote.mutate(note.id);
    }
  };

  const handleResummarize = () => {
    if (window.confirm("Re-summarize this note? The current summary and tags will be replaced.")) {
      resummarize.mutate(note.id);
    }
  };

  return (
    <article className="note">
      <h3>{note.title ?? "Untitled"}</h3>
      <p className="muted">{new Date(note.created_at).toLocaleString()}</p>

      <div>
        {note.tags.map((tag) => (
          <button
            key={tag}
            className={tag === activeTag ? "tag active" : "tag"}
            onClick={() => onTagClick(tag)}
          >
            #{tag}
          </button>
        ))}
      </div>

      {note.summary ? (
        <p>
          <strong>Summary</strong><br/>{note.summary}
        </p>
      ) : (
        <p className="muted">No summary yet (the AI call failed).</p>
      )}

      <p>
        <strong>Note</strong><br/>{note.content}
      </p>

      {error && <p className="error">{error.message}</p>}

      <div className="actions">
        <button onClick={handleResummarize} disabled={resummarize.isPending}>
          {resummarize.isPending ? "Summarizing..." : "Re-summarize"}
        </button>
        <button onClick={handleDelete} disabled={deleteNote.isPending}>
          {deleteNote.isPending ? "Deleting..." : "Delete"}
        </button>
      </div>
    </article>
  );
}
