# DSAt

DSAt is a multi-agent AI study tutor for algorithms and data structures. Students can upload a photo of lecture notes, pseudocode, or a code screenshot, and DSAt turns it into an interactive learning session.

## Features

- Image/PDF upload or plain-text pseudocode input
- Reader agent extracts algorithm context into structured data
- Debate agents argue complexity and paradigm from different personas
- Judge agent synthesizes the strongest explanation
- Quiz agent checks understanding with targeted feedback
- Demo mode fallback when no Anthropic API key is configured

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

For live model calls, create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
DSAT_API_TIMEOUT=30
```

Without `ANTHROPIC_API_KEY`, the app runs in demo mode with deterministic Merge Sort responses.

## Project Structure

```text
dsa_study_agent/
  agents/          # reader, debate, judge, quiz
  config/          # editable prompts.yaml
  models/          # shared dataclasses
  utils/           # upload and JSON helpers
  orchestrator.py  # end-to-end agent sequence
  ui.py            # Streamlit UI
app.py             # Streamlit entrypoint
```
