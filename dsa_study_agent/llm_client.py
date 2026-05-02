from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from dsa_study_agent.models import AlgorithmContext, Argument, QuizFeedback, QuizQuestion, Verdict
from dsa_study_agent.utils.image_utils import UploadedPayload
from dsa_study_agent.utils.json_utils import extract_json_array, extract_json_object


DEFAULT_MODEL = "claude-sonnet-4-20250514"


class LLMClient:
    def __init__(self) -> None:
        load_dotenv()
        self.model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self.demo_mode = os.getenv("DSAT_DEMO_MODE", "").lower() in {"1", "true", "yes"}
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.timeout = float(os.getenv("DSAT_API_TIMEOUT", "30"))
        self._client = None

        if self.api_key and not self.demo_mode:
            from anthropic import Anthropic

            self._client = Anthropic(api_key=self.api_key, timeout=self.timeout)

    @property
    def is_demo(self) -> bool:
        return self._client is None

    def complete_json(
        self,
        *,
        system_prompt: str,
        text: str,
        image: UploadedPayload | None = None,
        temperature: float = 0.2,
        expects_array: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if self._client is None:
            raise RuntimeError("LLM client is in demo mode; use demo fixtures instead.")

        content: list[dict[str, Any]] = []
        if image is not None:
            media_block_type = "document" if image.is_pdf else "image"
            content.append(
                {
                    "type": media_block_type,
                    "source": {
                        "type": "base64",
                        "media_type": image.mime_type,
                        "data": image.base64_data,
                    },
                }
            )
        content.append({"type": "text", "text": text})

        response = self._client.messages.create(
            model=self.model,
            max_tokens=1800,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )
        response_text = "\n".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        return extract_json_array(response_text) if expects_array else extract_json_object(response_text)


def demo_context(text_input: str = "") -> AlgorithmContext:
    pseudocode = text_input.strip() or "\n".join(
        [
            "MERGE-SORT(A, l, r)",
            "if l >= r: return",
            "m = floor((l + r) / 2)",
            "MERGE-SORT(A, l, m)",
            "MERGE-SORT(A, m + 1, r)",
            "MERGE(A, l, m, r)",
        ]
    )
    return AlgorithmContext(
        name="Merge Sort",
        pseudocode=pseudocode,
        paradigm_hint="divide and conquer",
        variables=["A", "l", "r", "m"],
        confidence=0.82,
        warning="Demo response: set ANTHROPIC_API_KEY to use live extraction.",
    )


def demo_argument(agent_id: str) -> Argument:
    if agent_id == "A":
        return Argument(
            agent_id="A",
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            paradigm="divide and conquer",
            reasoning=(
                "The algorithm splits the input into two halves until single-element ranges, "
                "then merges each level in linear work. There are log n split levels and O(n) "
                "merge work per level."
            ),
        )
    return Argument(
        agent_id="B",
        time_complexity="O(n log n)",
        space_complexity="O(n)",
        paradigm="divide and conquer",
        reasoning=(
            "The recurrence is T(n) = 2T(n/2) + O(n), which gives O(n log n) by the Master "
            "Theorem. The merge helper needs temporary storage proportional to the subarray size."
        ),
    )


def demo_verdict() -> Verdict:
    return Verdict(
        time_complexity="O(n log n)",
        space_complexity="O(n)",
        paradigm="divide and conquer",
        explanation=(
            "Merge Sort is divide and conquer: divide the array into halves, solve each half, "
            "and combine them with a linear merge. The total work is O(n log n), while the "
            "typical implementation uses O(n) auxiliary space."
        ),
        key_insight="The merge step costs O(n) at every recursion level.",
        agent_a_correct=True,
        agent_b_correct=True,
        agent_a_feedback="Correct conclusion, but the recurrence makes the proof stronger.",
        agent_b_feedback="Correct and well justified with the Master Theorem.",
    )


def demo_questions() -> list[QuizQuestion]:
    return [
        QuizQuestion(
            question="What recurrence best describes Merge Sort?",
            type="mcq",
            options=["T(n)=T(n-1)+O(1)", "T(n)=2T(n/2)+O(n)", "T(n)=T(n/2)+O(log n)"],
            expected_answer="T(n)=2T(n/2)+O(n)",
            hint="Count the two recursive calls and the cost of merging.",
        ),
        QuizQuestion(
            question="Why is the merge step responsible for the O(n) term?",
            type="short_answer",
            expected_answer="It scans and writes the elements in the current range once.",
            hint="Think about how many elements are copied or compared while merging two sorted halves.",
        ),
        QuizQuestion(
            question="What happens to the time complexity if the input is already sorted?",
            type="edge_case",
            expected_answer="Standard Merge Sort is still O(n log n) because it still splits and merges.",
            hint="Does the algorithm skip the recursive structure when the array is sorted?",
        ),
    ]


def demo_feedback(question: QuizQuestion, answer: str) -> QuizFeedback:
    normalized_answer = answer.strip().lower()
    expected = question.expected_answer.lower()
    if not normalized_answer:
        is_correct = False
    elif question.type == "mcq":
        is_correct = normalized_answer == expected
    elif "merge step" in question.question.lower():
        is_correct = all(
            any(term in normalized_answer for term in group)
            for group in [
                ("scan", "copy", "compare", "touch", "write"),
                ("each", "every", "all"),
                ("linear", "o(n)", "once"),
            ]
        )
    elif "already sorted" in question.question.lower():
        is_correct = "o(n log n)" in normalized_answer and any(
            term in normalized_answer for term in ("still", "same", "does not change")
        )
    else:
        is_correct = normalized_answer in expected or expected in normalized_answer
    return QuizFeedback(
        question=question.question,
        user_answer=answer,
        is_correct=is_correct,
        feedback=(
            "Good. You connected the answer to the structure of the algorithm."
            if is_correct
            else f"Not quite. {question.hint}"
        ),
        follow_up=None if is_correct else "Try explaining it using the recurrence or the merge loop.",
    )
