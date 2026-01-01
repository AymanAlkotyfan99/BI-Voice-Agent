# This module is deprecated and replaced by shared.pipeline
# Kept for backwards compatibility but not actively used

from llm_app.intent_service import extract_intent
from shared.sql_compiler import compile_sql
from shared.chart_recommender import recommend_chart


def generate_sql_and_chart(question: str) -> dict:
    """
    Legacy function - use shared.pipeline.process_question instead
    """
    intent_result = extract_intent(question)

    if intent_result.get("error"):
        return {
            "type": "error",
            "message": intent_result.get("message", "Unknown error")
        }

    intent = intent_result["intent"]
    
    try:
        sql = compile_sql(intent)
        chart = recommend_chart(intent)
        
        return {
            "sql": sql,
            "chart": chart,
            "intent": intent
        }
    except Exception as e:
        return {
            "type": "error",
            "message": str(e)
        }