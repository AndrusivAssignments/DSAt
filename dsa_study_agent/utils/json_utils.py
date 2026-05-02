from __future__ import annotations

import json
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from a model response that may include prose fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise
        parsed = json.loads(cleaned[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object")
    return parsed


def extract_json_array(text: str) -> list[dict[str, Any]]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start == -1 or end == -1 or start >= end:
            raise
        parsed = json.loads(cleaned[start : end + 1])

    if not isinstance(parsed, list):
        raise ValueError("Expected a JSON array")
    return parsed
