import os
import requests
from dotenv import load_dotenv
load_dotenv()

# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_llm(messages, model=None, temperature=0.2):
    """
    Отправляет сообщение в LLM через OpenRouter и возвращает текст ответа.

    messages:
        список сообщений в формате OpenAI:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]

    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Не найден OPENROUTER_API_KEY в .env")

    if model is None:
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash:free")

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

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()

    message = data["choices"][0]["message"]

    content = message.get("content")

    if content is None:
        content = message.get("reasoning")

    return content