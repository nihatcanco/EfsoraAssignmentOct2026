from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import ai
from app.db import get_db
from app.models import Note, User
from app.schemas import NoteCreate, NoteOut
from app.security import CurrentUser

router = APIRouter(prefix="/notes", tags=["notes"])

DB = Annotated[Session, Depends(get_db)]


def get_own_note(note_id: int, user: User, db: Session) -> Note:
    note = db.get(Note, note_id)
    if note is None or note.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note


@router.get("", response_model=list[NoteOut])
def list_notes(user: CurrentUser, db: DB, tag: str | None = None):
    query = select(Note).where(Note.user_id == user.id)
    tag = (tag or "").strip().lower()
    if tag:
        t = func.unnest(Note.tags).column_valued("t")
        query = query.where(select(t).where(t.contains(tag, autoescape=True)).exists())
    query = query.order_by(Note.created_at.desc(), Note.id.desc())
    return db.scalars(query).all()


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(body: NoteCreate, user: CurrentUser, db: DB):
    note = Note(user_id=user.id, title=body.title, content=body.content, tags=[])
    analysis = ai.analyze_note(body.title, body.content)
    
    if analysis:
        note.summary = analysis.summary
        note.tags = analysis.tags

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/summarize", response_model=NoteOut)
def resummarize_note(note_id: int, user: CurrentUser, db: DB):
    note = get_own_note(note_id, user, db)

    analysis = ai.analyze_note(note.title, note.content)
    if analysis is None:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "Couldn't summarize the note right now, try again later"
        )

    note.summary = analysis.summary
    note.tags = analysis.tags
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, user: CurrentUser, db: DB):
    note = get_own_note(note_id, user, db)
    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
