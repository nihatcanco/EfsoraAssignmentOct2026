from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

Password = Annotated[str, Field(min_length=8, max_length=128)]


class RegisterIn(BaseModel):
    email: EmailStr
    password: Password


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class NoteCreate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50_000)]

    @field_validator("title")
    @classmethod
    def empty_title_is_none(cls, v: str | None) -> str | None:
        return v or None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    content: str
    summary: str | None
    tags: list[str]
    created_at: datetime
