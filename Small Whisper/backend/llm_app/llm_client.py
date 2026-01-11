from openai import OpenAI
from openai import APIError, AuthenticationError
import os

# ============================================================
# 🔐 OpenRouter Configuration
# STATELESS: No user context, no Django auth, pure API call
# ============================================================

# Load API key from environment variable (preferred) or use hardcoded fallback
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3n-e4b-it:free")

# STATELESS CLIENT: No user information, no authentication headers
# This is a pure AI worker - only needs API key for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost",   # Required by OpenRouter
        "X-Title": "BI Voice Agent",           # Project identifier
        # NO Authorization header - OpenRouter uses api_key parameter
        # NO user_id or user_email - completely stateless
    }
)

# ============================================================
# 🔁 Same Interface, New Backend
# ============================================================

def call_llm(prompt: str) -> str:
    """
    Call LLM via OpenRouter.
    
    STATELESS: This function does NOT use any Django user context.
    It is a pure AI worker that only needs the prompt text.
    
    Args:
        prompt: The text prompt to send to the LLM
        
    Returns:
        Raw text response from the LLM
        
    Raises:
        ValueError: If OpenRouter API key is invalid or expired
        RuntimeError: For other API errors
    """
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=500,
        )

        return response.choices[0].message.content
    
    except AuthenticationError as e:
        # OpenRouter API key is invalid or expired
        # This is NOT a Django authentication issue
        error_msg = f"OpenRouter API authentication failed: {str(e)}. Please check OPENROUTER_API_KEY."
        raise ValueError(error_msg) from e
    
    except APIError as e:
        # Other OpenRouter API errors
        error_msg = f"OpenRouter API error: {str(e)}"
        raise RuntimeError(error_msg) from e
    
    except Exception as e:
        # Unexpected errors
        error_msg = f"LLM service error: {str(e)}"
        raise RuntimeError(error_msg) from e
