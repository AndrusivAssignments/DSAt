from __future__ import annotations

import json
from dataclasses import asdict

from dsa_study_agent.config import get_prompt
from dsa_study_agent.llm_client import LLMClient, demo_feedback, demo_questions
from dsa_study_agent.models import AlgorithmContext, QuizFeedback, QuizQuestion, Verdict


def generate_quiz(
    *,
    client: LLMClient,
    context: AlgorithmContext,
    verdict: Verdict,
) -> list[QuizQuestion]:
    if client.is_demo:
        return demo_questions()

    payload = {
        "algorithm_context": context.public_dict(),
        "verdict": asdict(verdict),
    }
    user_text = (
        "Generate 3 quiz questions and return only a JSON array. Each object must include: "
        "question, type, options, expected_answer, hint. Types must be mcq, short_answer, "
        "or edge_case.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
    rows = client.complete_json(
        system_prompt=get_prompt("quiz_generate"),
        text=user_text,
        temperature=0.35,
        expects_array=True,
    )
    return [
        QuizQuestion(
            question=str(row.get("question") or ""),
            type=row.get("type") if row.get("type") in {"mcq", "short_answer", "edge_case"} else "short_answer",
            options=row.get("options") if isinstance(row.get("options"), list) else None,
            expected_answer=str(row.get("expected_answer") or ""),
            hint=str(row.get("hint") or ""),
        )
        for row in rows
    ]


def evaluate_answer(
    *,
    client: LLMClient,
    context: AlgorithmContext,
    verdict: Verdict,
    question: QuizQuestion,
    user_answer: str,
) -> QuizFeedback:
    if client.is_demo:
        return demo_feedback(question, user_answer)

    payload = {
        "algorithm_context": context.public_dict(),
        "verdict": asdict(verdict),
        "question": asdict(question),
        "user_answer": user_answer,
    }
    user_text = (
        "Evaluate the student's answer and return only JSON with keys: question, "
        "user_answer, is_correct, feedback, follow_up. Be concise and targeted.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
    data = client.complete_json(system_prompt=get_prompt("quiz_evaluate"), text=user_text, temperature=0.2)
    return QuizFeedback(
        question=question.question,
        user_answer=user_answer,
        is_correct=bool(data.get("is_correct")),
        feedback=str(data.get("feedback") or ""),
        follow_up=data.get("follow_up"),
    )
