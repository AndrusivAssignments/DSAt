from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROMPTS_PATH = Path(__file__).parent / "config" / "prompts.yaml"


@lru_cache(maxsize=1)
def load_prompts() -> dict[str, Any]:
    with PROMPTS_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Prompt config must be a YAML mapping: {PROMPTS_PATH}")
    return data


def get_prompt(name: str) -> str:
    prompts = load_prompts()
    prompt = prompts.get(name)
    if not isinstance(prompt, str) or not prompt.strip():
        raise KeyError(f"Missing prompt '{name}' in {PROMPTS_PATH}")
    return prompt.strip()
