from __future__ import annotations

import json

from dsa_study_agent.config import get_prompt
from dsa_study_agent.llm_client import LLMClient, demo_argument
from dsa_study_agent.models import AlgorithmContext, Argument


def argue(*, client: LLMClient, context: AlgorithmContext, agent_id: str) -> Argument:
    if client.is_demo:
        return demo_argument(agent_id)

    prompt_name = "debate_a" if agent_id == "A" else "debate_b"
    user_text = (
        "Analyze this extracted algorithm context and return only JSON with keys: "
        "agent_id, time_complexity, space_complexity, paradigm, reasoning.\n\n"
        f"{json.dumps(context.public_dict(), indent=2)}"
    )
    data = client.complete_json(
        system_prompt=get_prompt(prompt_name),
        text=user_text,
        temperature=0.45 if agent_id == "A" else 0.2,
    )
    return Argument(
        agent_id=str(data.get("agent_id") or agent_id),
        time_complexity=str(data.get("time_complexity") or "unknown"),
        space_complexity=str(data.get("space_complexity") or "unknown"),
        paradigm=str(data.get("paradigm") or "unknown"),
        reasoning=str(data.get("reasoning") or ""),
    )
