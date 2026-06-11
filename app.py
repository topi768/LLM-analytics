import streamlit as st
import pandas as pd
from core.dataset_summary import build_dataset_summary
from core.agent import run_agent
from utils.file_loader import load_data

st.set_page_config(page_title="LLM Data Analyst", layout="wide")

st.title("LLM Data Analyst")
st.write("Анализа данных с LLM-агентом.")

uploaded_file = st.file_uploader("Загрузите CSV ", type=["csv", "xlsx", "xls"])

user_instruction = st.text_area(
    "Инструкция для анализа",
    placeholder="Например: найти корреляции, основные метрики, проверь выбросы"
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.success(f"Файл загружен: {uploaded_file.name}")

        st.subheader("Предпросмотр данных")
        st.dataframe(df.head(5), use_container_width=True)

        st.subheader("Основная информация")
        col1, col2, col3 = st.columns(3)
        col1.metric("Строки", df.shape[0])
        col2.metric("Столбцы", df.shape[1])

        missing_percent = (
                df.isna().sum().sum()
                / (df.shape[0] * df.shape[1])
                * 100
        )

        missing_percent = round(missing_percent, 2)

        col3.metric(
            "Пропущенные значения",
            f"{missing_percent}%"
        )
        #
        # with st.expander("Названия столбцов"):
        #     st.write(list(df.columns))

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")

# if user_instruction:
#     st.info("Инструкция получена.")
if st.button("Запустить AI-агента"):

    with st.spinner("Агент анализирует данные..."):
        output = run_agent(df, user_instruction)

    # Показать историю кода, если она есть
    if output.get("history"):
        st.subheader("История агента")
        for step in output["history"]:
            st.markdown(f"**Шаг {step['step']}**")
            st.code(step["code"], language="python")

    # Достаем внутренний результат выполнения
    result_block = output.get("result", {}).get("result", {})

    # Ошибка выполнения кода
    exec_error = output.get("result", {}).get("error")
    if exec_error:
        st.error("Ошибка выполнения кода")
        st.code(exec_error)
        st.stop()

    st.success("Код выполнен успешно")

    # Текстовый вывод
    text = result_block.get("text") or output.get("final_text")
    if text:
        st.subheader("Результат анализа")
        st.write(text)

    # Таблица
    table = result_block.get("table")
    if table is not None:
        st.subheader("Таблица результата")
        import pandas as pd
        table_df = pd.DataFrame(table)
        st.dataframe(table_df)

    # График
    chart = result_block.get("chart")
    if chart is not None:
        st.subheader("График")

        import plotly.express as px
        import pandas as pd

        df_chart = pd.DataFrame(chart["data"])
        chart_type = chart.get("type", "line")

        if chart_type == "line":
            fig = px.line(df_chart, x=chart["x"], y=chart["y"])
        elif chart_type == "bar":
            fig = px.bar(df_chart, x=chart["x"], y=chart["y"])
        elif chart_type == "scatter":
            fig = px.scatter(df_chart, x=chart["x"], y=chart["y"])
        else:
            st.warning("Неизвестный тип графика")
            fig = None

        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)