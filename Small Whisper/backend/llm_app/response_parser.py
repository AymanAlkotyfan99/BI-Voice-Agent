import json
import re


def safe_json_parse(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in LLM output")

    return json.loads(match.group(0))