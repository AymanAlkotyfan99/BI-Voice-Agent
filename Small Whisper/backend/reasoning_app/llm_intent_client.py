import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"

ANALYTICAL_KEYWORDS = (
    "average", "avg", "sum", "count",
    "max", "min", "total",
    "by year", "by month", "by day",
    "per", "group", "breakdown", "compare",
    "trend", "top", "bottom", "rank"
)


def is_force_analytical(question: str) -> bool:
    """Rule-based check for analytical questions"""
    q = question.lower()
    return any(k in q for k in ANALYTICAL_KEYWORDS)


def safe_json_parse(text: str) -> dict:
    """Extract JSON from LLM response"""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(match.group(0))


def classify_question(question: str) -> dict:
    """
    Classify whether a question needs SQL and chart generation.
    Returns: {"needs_sql": bool, "needs_chart": bool, "question_type": str}
    """
    # Rule-based guard (higher priority than LLM)
    if is_force_analytical(question):
        return {
            "question_type": "analytical",
            "needs_sql": True,
            "needs_chart": True
        }

    # Fallback to LLM classifier
    prompt = f"""You are a classifier in a BI system.

Decide ONLY:
- Does the question require SQL data analysis?
- Does it require a chart visualization?

Return ONLY valid JSON with this exact format:
{{
  "needs_sql": true or false,
  "needs_chart": true or false,
  "question_type": "analytical" or "informational"
}}

Question: {question}

JSON response:"""

    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()

        raw_output = response.json().get("response", "")
        parsed = safe_json_parse(raw_output)

        return {
            "needs_sql": parsed.get("needs_sql", False),
            "needs_chart": parsed.get("needs_chart", False),
            "question_type": parsed.get("question_type", "informational")
        }

    except Exception as e:
        # Fallback: treat as informational if LLM fails
        return {
            "needs_sql": False,
            "needs_chart": False,
            "question_type": "informational",
            "llm_error": str(e)
        }
