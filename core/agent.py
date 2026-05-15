from core.dataset_summary import build_dataset_summary
from core.llm_client import ask_llm
from core.executor import execute_code
from core.code_parser import extract_python_code
from core.code_validator import validate_code


def run_agent(df, user_instruction, max_retries=2):

    dataset_summary = build_dataset_summary(df)

    system_prompt = """
Ты — генератор Python-кода для анализа pandas DataFrame (df).

ТВОЯ ЗАДАЧА:
Сгенерировать код, который анализирует df и формирует result.

ФОРМАТ result:
{
    "text": str | None,
    "table": list[dict] | None,
    "chart": {
        "type": "line" | "bar" | "scatter",
        "x": str,
        "y": str,
        "data": list[dict]
    } | None
}

ПРАВИЛА:
1. Выводи ТОЛЬКО Python-код
2. Используй только pandas (pd) и df
3. НЕ пиши текст анализа — только вычисления
4. text можно оставить None (он будет сгенерирован позже)
5. ВСЕ метрики сохраняй в переменные или прямо в result
6. Никаких выдуманных чисел
"""

    user_prompt = f"""
Датасет:
{dataset_summary}

Инструкция:
{user_instruction}

Сгенерируй Python-код.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    raw_response = ask_llm(messages)
    code = extract_python_code(raw_response)

    validate_code(code)

    result = execute_code(code, df)

    summary_prompt = f"""
Ты аналитик данных.

Вот результат вычислений:

TEXT (если есть): {result.get("text")}

TABLE: {result.get("table")}

CHART: {result.get("chart")}

USER INSTRUCTION:
{user_instruction}

Напиши короткий, точный аналитический вывод на основе этих данных.
НЕ выдумывай числа — используй только предоставленные значения.
"""

    summary_messages = [
        {"role": "system", "content": "Ты аналитик данных. Пиши кратко и точно."},
        {"role": "user", "content": summary_prompt}
    ]

    final_text = ask_llm(summary_messages)

    result["text"] = final_text

    return {
        "code": code,
        "result": result
    }