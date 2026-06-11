import json

from core.dataset_summary import build_dataset_summary
from core.llm_client import ask_llm
from core.executor import execute_code
from core.code_parser import extract_python_code
from core.code_validator import validate_code


def safe_json_loads(text: str) -> dict:

    start = text.find("{")
    end = text.rfind("}")

    return json.loads(text[start: end + 1])


def format_history(history: list[dict]) -> str:
    if not history:
        return "История пустая."

    return "\n\n".join(
        f"""
        ШАГ {i}
        ИНСТРУКЦИЯ ШАГА:
        {item.get("instruction")}

        КОД:
        {item.get("code")}

        РЕЗУЛЬТАТ:
        text = {item.get("text")}
        table = {item.get("table")}
        chart = {item.get("chart")}
        """
        for i, item in enumerate(history, start=1)
    )


def build_code_prompt(dataset_summary: str, user_instruction: str, history: list[dict]) -> list[dict]:
    system_prompt = """
        Ты — генератор Python-кода для анализа pandas DataFrame (df).
        
        ТВОЯ ЗАДАЧА:
        Сгенерировать только Python-код, который анализирует df и формирует переменную result.
        
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
        table ОБЯЗАТЕЛЬНО должен быть list[dict].
        
        Каждая строка таблицы — отдельный словарь.
        
        Все словари должны иметь одинаковый набор ключей.
        
        Разрешённые типы значений в ячейках:
        
        - str
        - int
        - float
        - bool
        - None
        
        Запрещено использовать:
        
        - list
        - dict
        - tuple
        - set
        - DataFrame
        - Series
        - numpy.ndarray
        - любые вложенные структуры
        
        Таблица должна быть плоской.
        
        ПРАВИЛА:
        1. Выводи ТОЛЬКО Python-код
        2. Используй только pandas и df. Не используй другие подключаемые библиотеки
        3. НЕ пиши текст анализа
        4. Никаких выдуманных чисел
        5. Если строишь chart, то chart["x"] и chart["y"] должны совпадать с ключами внутри chart["data"]
        6. Не переименовывай поля внутри chart["data"] без необходимости
        7. Отвечай исключительно на русском языке
        """

    user_prompt = f"""
    Датасет:
    {dataset_summary}
    
    Текущая инструкция пользователя:
    {user_instruction}
    
    История предыдущих шагов:
    {format_history(history)}
    
    Сгенерируй следующий Python-код для анализа.
    """

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_decision_prompt(user_instruction: str, history: list[dict]) -> list[dict]:
    system_prompt = """
    Ты — аналитический агент.
    
    Твоя задача — посмотреть на уже выполненные шаги и решить:
    - закончить анализ,
    - или продолжить исследование ещё одним шагом.
    
    Верни ТОЛЬКО JSON без поясняющего текста.
    
    Формат:
    {
        "action": "finish" | "continue",
        "reason": "короткое объяснение",
        "next_instruction": "что именно нужно сделать дальше",
        "final_text": "итоговый текст, если action = finish"
    }
    
    Правила:
    1. Если информации достаточно — action = "finish"
    2. Если нужен дополнительный анализ — action = "continue"
    3. Если action = "continue", то next_instruction должен быть конкретным
    4. Если action = "finish", final_text обязателен
    """

    user_prompt = f"""
    Текущая задача пользователя:
    {user_instruction}
    
    История анализа:
    {format_history(history)}
    
    Прими решение: завершить или продолжить.
    """

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_summary_prompt(user_instruction: str, history: list[dict]) -> list[dict]:
    system_prompt = "Ты аналитик данных. Пиши кратко, точно и только на основе предоставленных результатов."

    user_prompt = f"""
    Инструкция пользователя:
    {user_instruction}
    
    История выполненных шагов:
    {format_history(history)}
    
    Напиши короткий итоговый аналитический вывод без выдуманных чисел.
    Отвечай искючительно на русском языке
    
    """

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def run_agent(df, user_instruction, max_steps=3):
    dataset_summary = build_dataset_summary(df)

    history = []
    current_instruction = user_instruction
    last_exec_result = None
    final_text = None

    for step in range(max_steps):
        code_messages = build_code_prompt(dataset_summary, current_instruction, history)
        raw_response = ask_llm(code_messages)

        code = extract_python_code(raw_response)
        validate_code(code)

        exec_result = execute_code(code, df)
        inner = exec_result.get("result", {}) or {}

        history.append(
            {
                "step": step + 1,
                "instruction": current_instruction,
                "code": code,
                "text": inner.get("text"),
                "table": inner.get("table"),
                "chart": inner.get("chart"),
                "raw_exec_result": exec_result,
            }
        )
        last_exec_result = exec_result

        decision_messages = build_decision_prompt(user_instruction, history)
        decision_raw = ask_llm(decision_messages)

        try:
            decision = safe_json_loads(decision_raw)
        except Exception:
            decision = {
                "action": "finish",
                "reason": "Не удалось разобрать решение модели",
                "final_text": None,
            }

        if decision.get("action") == "finish":
            final_text = decision.get("final_text")
            if not final_text:
                final_text = ask_llm(build_summary_prompt(user_instruction, history))
            break

        next_instruction = decision.get("next_instruction")
        if next_instruction:
            current_instruction = next_instruction

    if final_text is None:
        final_text = ask_llm(build_summary_prompt(user_instruction, history))

    if last_exec_result is None:
        last_exec_result = {"result": {}}

    last_exec_result["result"] = last_exec_result.get("result", {}) or {}
    last_exec_result["result"]["text"] = final_text

    return {
        "dataset_summary": dataset_summary,
        "history": history,
        "result": last_exec_result,
        "final_text": final_text,
        "code": history[-1]["code"] if history else None,
    }