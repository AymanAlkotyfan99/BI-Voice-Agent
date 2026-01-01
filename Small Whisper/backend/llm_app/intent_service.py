from llm_app.schema_provider import get_schema, is_question_matching_schema
from llm_app.prompt_builder import build_prompt
from llm_app.response_parser import safe_json_parse
from llm_app.llm_client import call_llm


def extract_intent(question: str) -> dict:
    schema = get_schema()
    matches_schema = is_question_matching_schema(question, schema)

    prompt = build_prompt(question, schema)
    raw_output = call_llm(prompt)

    print("\n--- RAW INTENT OUTPUT ---")
    print(raw_output)

    return {
        "error": False,
        "intent": safe_json_parse(raw_output),
        "schema": schema,
        "matches_schema": matches_schema
    }
