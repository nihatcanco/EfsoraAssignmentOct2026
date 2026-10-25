import os

# must be set before the app (and its engine) is imported
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://briefbase:briefbase@localhost:5433/briefbase_test",
)
os.environ.setdefault("JWT_SECRET", "test-secret-that-is-at-least-32-bytes-long")
os.environ["ANTHROPIC_API_KEY"] = ""

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import ai
from app.db import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def migrate():
    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    command.upgrade(cfg, "head")


@pytest.fixture(autouse=True)
def clean_db():
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE notes, users RESTART IDENTITY CASCADE"))


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_ai(monkeypatch):
    def fake(title, content):
        return ai.NoteAnalysis(summary=f"summary of {content[:20]}", tags=["python", "testing", "notes"])

    monkeypatch.setattr(ai, "analyze_note", fake)


def register(client, email="test@example.com", password="password123"):
    res = client.post("/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
