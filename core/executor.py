import sys
import io
import traceback
import pandas as pd


def execute_code(code: str, df):
    """
    Выполняет LLM-сгенерированный код и извлекает result:
    {
        "text": str | None,
        "table": list[dict] | None,
        "chart": dict | None
    }
    """

    # 1. перехват stdout
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    # 2. execution environment
    exec_globals = {
        "df": df,
        "pd": pd,
        "__builtins__": {
            "len": len,
            "range": range,
            "min": min,
            "max": max,
            "sum": sum,
            "print": print,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
        }
    }

    error = None
    result = None

    try:
        # 3. execute LLM code
        exec(code, exec_globals)

        # 4. extract result (главный контракт)
        result = exec_globals.get("result", None)

        # 5. нормализация result (если LLM сломал формат)
        if result is not None:
            if not isinstance(result, dict):
                raise ValueError("result must be a dict with keys text/table/chart")

            result = {
                "text": result.get("text", None),
                "table": result.get("table", None),
                "chart": result.get("chart", None),
            }
        else:
            # если LLM вообще ничего не вернул
            result = {
                "text": None,
                "table": None,
                "chart": None
            }

        return {
            "result": result,
            "stdout": buffer.getvalue() or None,
            "error": None
        }

    except Exception:
        error = traceback.format_exc()

        return {
            "result": {
                "text": None,
                "table": None,
                "chart": None
            },
            "stdout": buffer.getvalue() or None,
            "error": error
        }

    finally:
        # restore stdout
        sys.stdout = old_stdout