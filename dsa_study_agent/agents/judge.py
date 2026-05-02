from __future__ import annotations

import json
from dataclasses import asdict

from dsa_study_agent.config import get_prompt
from dsa_study_agent.llm_client import LLMClient, demo_verdict
from dsa_study_agent.models import AlgorithmContext, Argument, Verdict


def decide(
    *,
    client: LLMClient,
    context: AlgorithmContext,
    argument_a: Argument,
    argument_b: Argument,
) -> Verdict:
    if client.is_demo:
        return demo_verdict()

    payload = {
        "algorithm_context": context.public_dict(),
        "argument_a": asdict(argument_a),
        "argument_b": asdict(argument_b),
    }
    user_text = (
        "Evaluate both arguments and return only JSON with keys: time_complexity, "
        "space_complexity, paradigm, explanation, key_insight, agent_a_correct, "
        "agent_b_correct, agent_a_feedback, agent_b_feedback.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
    data = client.complete_json(system_prompt=get_prompt("judge"), text=user_text, temperature=0.1)
    return Verdict(
        time_complexity=str(data.get("time_complexity") or "unknown"),
        space_complexity=str(data.get("space_complexity") or "unknown"),
        paradigm=str(data.get("paradigm") or "unknown"),
        explanation=str(data.get("explanation") or ""),
        key_insight=str(data.get("key_insight") or ""),
        agent_a_correct=bool(data.get("agent_a_correct")),
        agent_b_correct=bool(data.get("agent_b_correct")),
        agent_a_feedback=str(data.get("agent_a_feedback") or ""),
        agent_b_feedback=str(data.get("agent_b_feedback") or ""),
    )
