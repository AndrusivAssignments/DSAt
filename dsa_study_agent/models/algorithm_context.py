from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


@dataclass
class AlgorithmContext:
    name: str
    pseudocode: str
    paradigm_hint: str
    variables: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_image_b64: str | None = None
    input_mime_type: str | None = None
    warning: str | None = None

    def public_dict(self) -> dict:
        data = asdict(self)
        data.pop("raw_image_b64", None)
        return data


@dataclass
class Argument:
    agent_id: str
    time_complexity: str
    space_complexity: str
    paradigm: str
    reasoning: str


@dataclass
class Verdict:
    time_complexity: str
    space_complexity: str
    paradigm: str
    explanation: str
    key_insight: str
    agent_a_correct: bool
    agent_b_correct: bool
    agent_a_feedback: str = ""
    agent_b_feedback: str = ""


@dataclass
class QuizQuestion:
    question: str
    type: Literal["mcq", "short_answer", "edge_case"]
    expected_answer: str
    hint: str
    options: list[str] | None = None


@dataclass
class QuizFeedback:
    question: str
    user_answer: str
    is_correct: bool
    feedback: str
    follow_up: str | None = None


@dataclass
class StudySession:
    context: AlgorithmContext
    argument_a: Argument
    argument_b: Argument
    verdict: Verdict
    questions: list[QuizQuestion]
    quiz_feedback: list[QuizFeedback] = field(default_factory=list)

    @property
    def score(self) -> int:
        return sum(1 for item in self.quiz_feedback if item.is_correct)
