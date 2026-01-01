from openai import OpenAI

OPENROUTER_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost",   # أي قيمة
        "X-Title": "BI Voice Agent",       # اسم مشروعك
    }
)

response = client.chat.completions.create(
    model="google/gemma-3n-e4b-it:free",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    temperature=0.0,
    max_tokens=50,
)

print("✅ Model reply:")
print(response.choices[0].message.content)
