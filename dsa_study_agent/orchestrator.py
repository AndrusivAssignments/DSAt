from __future__ import annotations

from dsa_study_agent.agents import argue, decide, extract_algorithm, generate_quiz
from dsa_study_agent.llm_client import LLMClient
from dsa_study_agent.models import StudySession
from dsa_study_agent.utils.image_utils import UploadedPayload


def run_pipeline(upload: UploadedPayload | None, text_input: str) -> StudySession:
    client = LLMClient()
    context = extract_algorithm(client=client, upload=upload, text_input=text_input)
    argument_a = argue(client=client, context=context, agent_id="A")
    argument_b = argue(client=client, context=context, agent_id="B")
    verdict = decide(client=client, context=context, argument_a=argument_a, argument_b=argument_b)
    questions = generate_quiz(client=client, context=context, verdict=verdict)
    return StudySession(
        context=context,
        argument_a=argument_a,
        argument_b=argument_b,
        verdict=verdict,
        questions=questions,
    )
