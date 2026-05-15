import sys
import io
import traceback
import pandas as pd


def execute_code(code: str, df):


    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

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
            '__import__ ': __import__
        }
    }

    error = None
    result = None

    try:
        exec(code, exec_globals)

        result = exec_globals.get("result", None)

        if result is not None:
            if not isinstance(result, dict):
                raise ValueError("result must be a dict with keys text/table/chart")

            result = {
                "text": result.get("text", None),
                "table": result.get("table", None),
                "chart": result.get("chart", None),
            }
        else:
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
        sys.stdout = old_stdout