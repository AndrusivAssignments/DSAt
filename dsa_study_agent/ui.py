from __future__ import annotations

import os

import streamlit as st

from dsa_study_agent.agents.quiz import evaluate_answer
from dsa_study_agent.llm_client import LLMClient
from dsa_study_agent.models import StudySession
from dsa_study_agent.orchestrator import run_pipeline
from dsa_study_agent.utils.image_utils import normalize_upload


def main() -> None:
    st.set_page_config(page_title="DSAt Study Tutor", layout="wide")

    st.title("DSAt Study Tutor")
    st.caption("Upload DSA notes or paste pseudocode, then walk through extraction, debate, verdict, and quiz.")

    with st.sidebar:
        st.header("Session")
        demo_active = not os.getenv("ANTHROPIC_API_KEY") or os.getenv("DSAT_DEMO_MODE", "").lower() in {
            "1",
            "true",
            "yes",
        }
        st.status("Demo mode" if demo_active else "Live Anthropic API", state="complete")
        if st.button("Start new session", use_container_width=True):
            for key in ["session", "answers", "feedback"]:
                st.session_state.pop(key, None)
            st.rerun()

    upload = st.file_uploader(
        "Image or PDF page scan",
        type=["png", "jpg", "jpeg", "webp", "pdf"],
        accept_multiple_files=False,
    )
    text_input = st.text_area("Plain-text pseudocode", height=180, placeholder="Paste pseudocode here...")

    if upload is not None:
        if upload.type.startswith("image/"):
            st.image(upload, caption=upload.name, use_container_width=True)
        else:
            st.info(f"PDF selected: {upload.name}")

    left, right = st.columns([1, 2])
    with left:
        run_disabled = upload is None and not text_input.strip()
        if st.button("Run study session", type="primary", disabled=run_disabled, use_container_width=True):
            try:
                payload = normalize_upload(upload) if upload else None
                with st.spinner("Running Reader, Debate, Judge, and Quiz agents..."):
                    st.session_state.session = run_pipeline(payload, text_input)
                    st.session_state.answers = {}
                    st.session_state.feedback = {}
            except Exception as exc:
                st.error(f"Could not run the session: {exc}")

    session: StudySession | None = st.session_state.get("session")
    if session is None:
        with right:
            st.info("Add an upload or pseudocode to start.")
        return

    render_session(session)


def render_session(session: StudySession) -> None:
    context = session.context
    if context.warning:
        st.warning(context.warning)

    st.subheader("Reader")
    metrics = st.columns(4)
    metrics[0].metric("Algorithm", context.name)
    metrics[1].metric("Paradigm", context.paradigm_hint)
    metrics[2].metric("Confidence", f"{context.confidence:.0%}")
    metrics[3].metric("Variables", ", ".join(context.variables) or "None")
    st.code(context.pseudocode or "No pseudocode extracted.", language="text")

    st.subheader("Debate")
    col_a, col_b = st.columns(2)
    with col_a:
        render_argument("Agent A", session.argument_a.reasoning, session.argument_a.time_complexity, session.argument_a.space_complexity, session.argument_a.paradigm)
    with col_b:
        render_argument("Agent B", session.argument_b.reasoning, session.argument_b.time_complexity, session.argument_b.space_complexity, session.argument_b.paradigm)

    st.subheader("Judge")
    verdict = session.verdict
    verdict_cols = st.columns(3)
    verdict_cols[0].metric("Time", verdict.time_complexity)
    verdict_cols[1].metric("Space", verdict.space_complexity)
    verdict_cols[2].metric("Paradigm", verdict.paradigm)
    st.write(verdict.explanation)
    st.info(verdict.key_insight)
    with st.expander("Agent feedback"):
        st.write(f"Agent A: {verdict.agent_a_feedback or verdict.agent_a_correct}")
        st.write(f"Agent B: {verdict.agent_b_feedback or verdict.agent_b_correct}")

    render_quiz(session)


def render_argument(title: str, reasoning: str, time_complexity: str, space_complexity: str, paradigm: str) -> None:
    st.markdown(f"**{title}**")
    st.write(f"Time: `{time_complexity}`")
    st.write(f"Space: `{space_complexity}`")
    st.write(f"Paradigm: `{paradigm}`")
    st.write(reasoning)


def render_quiz(session: StudySession) -> None:
    st.subheader("Quiz")
    client = LLMClient()
    answers = st.session_state.setdefault("answers", {})
    feedback = st.session_state.setdefault("feedback", {})

    for index, question in enumerate(session.questions):
        key = f"q{index}"
        st.markdown(f"**Question {index + 1}: {question.question}**")
        if question.type == "mcq" and question.options:
            answers[key] = st.radio("Choose one", question.options, key=f"answer_{key}", index=None)
        else:
            answers[key] = st.text_input("Your answer", key=f"answer_{key}")

        if st.button("Check answer", key=f"check_{key}"):
            if not answers.get(key):
                st.warning("Add an answer first.")
            else:
                with st.spinner("Checking your answer..."):
                    feedback[key] = evaluate_answer(
                        client=client,
                        context=session.context,
                        verdict=session.verdict,
                        question=question,
                        user_answer=str(answers[key]),
                    )

        if key in feedback:
            item = feedback[key]
            (st.success if item.is_correct else st.error)(item.feedback)
            if item.follow_up:
                st.caption(item.follow_up)

    if feedback:
        score = sum(1 for item in feedback.values() if item.is_correct)
        st.subheader("Summary")
        st.write(f"{session.context.name}: {session.verdict.time_complexity} time, {session.verdict.space_complexity} space.")
        st.write(f"Quiz score so far: {score}/{len(session.questions)}")
