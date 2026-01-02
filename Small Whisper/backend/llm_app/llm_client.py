from openai import OpenAI

# ============================================================
# 🔐 OpenRouter Configuration
# ============================================================

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "google/gemma-3n-e4b-it:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost",   # أي قيمة
        "X-Title": "BI Voice Agent",           # اسم مشروعك
    }
)

# ============================================================
# 🔁 Same Interface, New Backend
# ============================================================

def call_llm(prompt: str) -> str:
    """
    Call LLM via OpenRouter.
    Same interface as Ollama version.
    Returns raw text response.
    """
    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=500,
    )

    return response.choices[0].message.content
