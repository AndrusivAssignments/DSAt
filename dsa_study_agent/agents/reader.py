from __future__ import annotations

from dsa_study_agent.config import get_prompt
from dsa_study_agent.llm_client import LLMClient, demo_context
from dsa_study_agent.models import AlgorithmContext
from dsa_study_agent.utils.image_utils import UploadedPayload


def extract_algorithm(
    *,
    client: LLMClient,
    upload: UploadedPayload | None,
    text_input: str,
) -> AlgorithmContext:
    if client.is_demo:
        context = demo_context(text_input)
        if upload is not None:
            context.raw_image_b64 = upload.base64_data
            context.input_mime_type = upload.mime_type
        return context

    prompt = get_prompt("reader")
    user_text = (
        "Extract the algorithm from the provided material. "
        "Return only JSON with keys: name, pseudocode, paradigm_hint, variables, confidence, warning.\n\n"
        f"Optional plain-text input:\n{text_input or '[none]'}"
    )
    data = client.complete_json(system_prompt=prompt, text=user_text, image=upload, temperature=0.0)

    return AlgorithmContext(
        name=str(data.get("name") or "Unknown algorithm"),
        pseudocode=str(data.get("pseudocode") or ""),
        paradigm_hint=str(data.get("paradigm_hint") or "unknown"),
        variables=list(data.get("variables") or []),
        confidence=float(data.get("confidence") or 0.0),
        raw_image_b64=upload.base64_data if upload else None,
        input_mime_type=upload.mime_type if upload else None,
        warning=data.get("warning"),
    )
