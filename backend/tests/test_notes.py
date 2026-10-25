from app import ai
from tests.conftest import register


def test_create_note_stores_summary_and_tags(client, fake_ai):
    headers = register(client)
    res = client.post("/notes", json={"title": "Standup", "content": "We talked about the release"}, headers=headers)
    assert res.status_code == 201
    note = res.json()
    assert note["title"] == "Standup"
    assert note["summary"].startswith("summary of")
    assert note["tags"] == ["python", "testing", "notes"]


def test_create_note_requires_content(client, fake_ai):
    headers = register(client)
    res = client.post("/notes", json={"title": "empty", "content": "   "}, headers=headers)
    assert res.status_code == 422


def test_note_saved_when_ai_fails(client, monkeypatch):
    monkeypatch.setattr(ai, "analyze_note", lambda title, content: None)
    headers = register(client)

    res = client.post("/notes", json={"content": "some text"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["summary"] is None
    assert res.json()["tags"] == []

    res = client.post(f"/notes/{res.json()['id']}/summarize", headers=headers)
    assert res.status_code == 502


def test_list_newest_first_and_filter_by_tag(client, monkeypatch):
    tags = iter([["work", "planning"], ["personal", "100%_done"], ["work"]])
    monkeypatch.setattr(ai, "analyze_note", lambda t, c: ai.NoteAnalysis(summary="s", tags=next(tags)))
    headers = register(client)
    for content in ["first", "second", "third"]:
        client.post("/notes", json={"content": content}, headers=headers)

    notes = client.get("/notes", headers=headers).json()
    assert [n["content"] for n in notes] == ["third", "second", "first"]

    work = client.get("/notes", params={"tag": "Work"}, headers=headers).json()
    assert [n["content"] for n in work] == ["third", "first"]

    wo = client.get("/notes", params={"tag": "wo"}, headers=headers).json()
    assert [n["content"] for n in wo] == ["third", "first"]
    ann = client.get("/notes", params={"tag": "ann"}, headers=headers).json()
    assert [n["content"] for n in ann] == ["first"]

    assert client.get("/notes", params={"tag": "w_rk"}, headers=headers).json() == []
    assert [n["content"] for n in client.get("/notes", params={"tag": "0%_d"}, headers=headers).json()] == ["second"]


def test_users_only_see_their_own_notes(client, fake_ai):
    test1 = register(client, "test1@example.com")
    test2 = register(client, "test2@example.com")

    note_id = client.post("/notes", json={"content": "test1's secret"}, headers=test1).json()["id"]

    assert client.get("/notes", headers=test2).json() == []
    assert client.delete(f"/notes/{note_id}", headers=test2).status_code == 404
    assert client.post(f"/notes/{note_id}/summarize", headers=test2).status_code == 404
    assert len(client.get("/notes", headers=test1).json()) == 1


def test_delete_note(client, fake_ai):
    headers = register(client)
    note_id = client.post("/notes", json={"content": "delete me"}, headers=headers).json()["id"]

    assert client.delete(f"/notes/{note_id}", headers=headers).status_code == 204
    assert client.get("/notes", headers=headers).json() == []
    assert client.delete(f"/notes/{note_id}", headers=headers).status_code == 404


def test_resummarize(client, monkeypatch):
    monkeypatch.setattr(ai, "analyze_note", lambda t, c: ai.NoteAnalysis(summary="old", tags=["a"]))
    headers = register(client)
    note_id = client.post("/notes", json={"content": "text"}, headers=headers).json()["id"]

    monkeypatch.setattr(ai, "analyze_note", lambda t, c: ai.NoteAnalysis(summary="new", tags=["b", "c"]))
    res = client.post(f"/notes/{note_id}/summarize", headers=headers)
    assert res.status_code == 200
    assert res.json()["summary"] == "new"
    assert res.json()["tags"] == ["b", "c"]


def test_clean_tags():
    assert ai.clean_tags(["#Python", "python", " Web Dev ", "", "a", "b", "c", "d"]) == [
        "python", "web dev", "a", "b", "c"
    ]
