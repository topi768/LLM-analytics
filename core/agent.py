from core.dataset_summary import build_dataset_summary
from core.llm_client import ask_llm
from core.executor import execute_code
from core.code_parser import extract_python_code

def run_agent(df, user_instruction):
    """
    Один полный цикл агента:
    LLM → код → выполнение → результат
    """

    # 1. готовим описание датасета
    dataset_summary = build_dataset_summary(df)

    # 2. просим LLM написать код
    messages = [
        {
            "role": "system",
            "content": (
                "Ты — узкоспециализированный генератор Python-кода для pandas. "
                "Твоя задача: прочитать описание df и выдать код, решающий задачу. "
                "\n\nПРАВИЛА:\n"
                "1. Выдавай ТОЛЬКО чистый Python-код.\n"
                "2. Никаких пояснений, вступлений и комментариев 'Сгенерированный код'.\n"
                "3. Весь код должен быть обернут в один блок ```python ... ```.\n"
                "4. Результат обязательно сохрани в переменную result_text (строка) или result_df (DataFrame)."
                "5. Если нужен график, используй matplotlib.pyplot (импортирован как plt). "
                "6. ОБЯЗАТЕЛЬНО сохраняй график через plt.savefig('temp_plot.png'). "
                "7. Всегда делай plt.close() после сохранения, чтобы не забивать память."
            )
        },
        {
            "role": "user",
            "content": f"""
    Датасет (df.head()):
    {dataset_summary}

    Инструкция: {user_instruction}

    Напиши код. Используй только библиотеку pandas (уже импортирована как pd) и переменную df.
    """
        }
    ]

    raw_response = ask_llm(messages)
    code = extract_python_code(raw_response)
    # 3. выполняем код
    result = execute_code(code, df)

    return {
        "code": code,
        "result": result
    }