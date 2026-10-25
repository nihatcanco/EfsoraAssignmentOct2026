import logging

import anthropic
from pydantic import BaseModel, ValidationError

from app.config import settings

log = logging.getLogger(__name__)

PROMPT = """Summarize the note below in at most 2 short sentences and pick 3 to 5 short tags for it (lowercase, max 2 words each) that would help find it later.

<note>
{note}
</note>"""


class NoteAnalysis(BaseModel):
    summary: str
    tags: list[str]


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=60)
    return _client


def clean_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    for tag in tags:
        tag = tag.strip().lstrip("#").lower()
        if tag and tag not in out:
            out.append(tag[:40])
    return out[:5]


def analyze_note(title: str | None, content: str) -> NoteAnalysis | None:
    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY is not set, skipping summary")
        return None

    note = f"Title: {title}\n\n{content}" if title else content

    try:
        response = _get_client().messages.parse(
            model=settings.anthropic_model,
            max_tokens=4000,
            output_config={"effort": "low"},
            output_format=NoteAnalysis,
            messages=[{"role": "user", "content": PROMPT.format(note=note)}],
        )
    except ValidationError:
        log.warning("AI returned malformed output")
    except anthropic.APIError:
        log.exception("AI request failed")
        return None

    if response.stop_reason == "refusal":
        log.warning("AI refused to summarize note")
        return None

    result = response.parsed_output
    if result is None or not result.summary.strip():
        log.warning("AI returned an empty result")

    return NoteAnalysis(summary=result.summary.strip(), tags=clean_tags(result.tags))

    return None
