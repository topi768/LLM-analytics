import os
import requests
from dotenv import load_dotenv

load_dotenv()

# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
def ask_llm(messages, model=None, temperature=0.2):

    api_key = os.getenv("OPENROUTER_API_CHAT_GPT")
    if not api_key:
        raise ValueError("Не найден OPENROUTER_API_KEY в .env")

    # model = model or os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free")
    model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b:free")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "LLM Data Analyst",
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"OpenRouter error {response.status_code}: {response.text}"
        )

    try:
        data = response.json()
    except Exception:
        raise Exception(f"Invalid JSON response: {response.text}")

    message = data["choices"][0]["message"]

    content = message.get("content")

    if content is None:
        content = message.get("reasoning")

    return content