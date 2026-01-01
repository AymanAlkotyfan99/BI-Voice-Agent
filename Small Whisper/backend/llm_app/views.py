from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from llm_app.intent_service import extract_intent
from shared.sql_compiler import compile_sql
from shared.chart_recommender import recommend_chart


@csrf_exempt
def intent_test_view(request):
    """
    Test endpoint for intent extraction + SQL + Chart
    POST: {"question": "your analytical question"}
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            
            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)
            
            # Extract intent
            result = extract_intent(question)
            
            if result.get("error"):
                return JsonResponse(result, status=500)
            
            intent = result["intent"]
            
            # Generate SQL and Chart
            try:
                sql = compile_sql(intent)
                chart = recommend_chart(intent)
                
                return JsonResponse({
                    "question": question,
                    "intent": intent,
                    "sql": sql,
                    "chart": chart
                })
            except Exception as e:
                return JsonResponse({
                    "error": f"SQL/Chart generation failed: {str(e)}",
                    "intent": intent
                }, status=500)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST allowed"}, status=405)

