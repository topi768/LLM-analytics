import io
import traceback
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# Белый список встроенных функций.
# Это значит: код, который запускает LLM, сможет использовать только эти функции,
# а не опасные вещи вроде open(), eval(), exec() и т.д.
SAFE_BUILTINS = {
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "range": range,
    "enumerate": enumerate,
    "sorted": sorted,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "float": float,
    "int": int,
    "str": str,
    "bool": bool,
    "print": print,
    "zip": zip,
    "any": any,
    "all": all,
    "round": round,
    "__import__": __import__,
}


def execute_code(code: str, df: pd.DataFrame) -> dict:
    """
    Выполняет Python-код, сгенерированный LLM.

    Параметры:
    code:
        Строка с Python-кодом.
        Этот код должен работать с переменной df.

    df:
        DataFrame, загруженный пользователем.

    Возвращает:
    dict:
        Словарь с результатом выполнения:
        - ok: успешно ли выполнился код
        - stdout: текст из print()
        - result_text: текстовый результат, если код сохранил его в переменную
        - result_df: таблица-результат, если код сохранил её в переменную
        - matplotlib_figures: список matplotlib-фигур
        - plotly_figures: список plotly-фигур
        - error: текст ошибки, если она была
    """

    # Эти переменные будут доступны коду, который исполняем.
    # Здесь мы специально ограничиваем окружение.
    global_vars = {
        "__builtins__": SAFE_BUILTINS,
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "plt": plt,
        "px": px,
        "go": go,
    }

    # Тут будут переменные, которые код создаст внутри себя.
    local_vars = {}

    # Сюда перехватываем всё, что код напечатает через print().
    stdout_buffer = io.StringIO()

    try:
        with redirect_stdout(stdout_buffer):
            exec(code, global_vars, local_vars)

        # Достаём все matplotlib-фигуры, которые были созданы.
        matplotlib_figures = []
        for fig_num in plt.get_fignums():
            matplotlib_figures.append(plt.figure(fig_num))

        # Достаём plotly-фигуры, если код сохранил их в заранее оговорённые имена.
        plotly_figures = []

        if "result_plotly_fig" in local_vars and local_vars["result_plotly_fig"] is not None:
            plotly_figures.append(local_vars["result_plotly_fig"])

        if "result_plotly_figures" in local_vars and local_vars["result_plotly_figures"] is not None:
            plotly_figures.extend(local_vars["result_plotly_figures"])

        # Формируем единый результат.
        result = {
            "ok": True,
            "stdout": stdout_buffer.getvalue(),
            "result_text": local_vars.get("result_text", ""),
            "result_df": local_vars.get("result_df", None),
            "matplotlib_figures": matplotlib_figures,
            "plotly_figures": plotly_figures,
            "error": "",
            "locals": local_vars,
        }

        return result

    except Exception as e:
        return {
            "ok": False,
            "stdout": stdout_buffer.getvalue(),
            "result_text": "",
            "result_df": None,
            "matplotlib_figures": [],
            "plotly_figures": [],
            "error": f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}",
            "locals": local_vars,
        }

    finally:
        # Закрываем все фигуры, чтобы они не копились между запусками.
        plt.close("all")