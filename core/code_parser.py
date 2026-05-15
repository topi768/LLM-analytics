import re

def extract_python_code(text: str) -> str:
    """
    Достаёт чистый Python-код из ответа LLM.
    Убирает:
    - ```python блоки
    - лишний текст
    """

    # 1. пробуем найти ```python ... ```
    code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)

    if code_blocks:
        return code_blocks[0].strip()

    # 2. пробуем общий ``` ... ```
    code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)

    if code_blocks:
        return code_blocks[0].strip()

    # 3. если вообще нет блоков — считаем что это чистый код
    return text.strip()