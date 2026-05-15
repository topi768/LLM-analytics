import streamlit as st
import pandas as pd
from core.dataset_summary import build_dataset_summary
from core.agent import run_agent
from utils.file_loader import load_data

st.set_page_config(page_title="LLM Data Analyst", layout="wide")

st.title("LLM Data Analyst")
st.write("Приложение для анализа данных с LLM-агентом.")

uploaded_file = st.file_uploader("Загрузите CSV или Excel файл", type=["csv", "xlsx", "xls"])

user_instruction = st.text_area(
    "Инструкция для анализа",
    placeholder="Например: найди аномалии, покажи основные метрики, проверь выбросы"
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.success(f"Файл загружен: {uploaded_file.name}")

        st.subheader("Предпросмотр данных")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Основная информация")
        col1, col2, col3 = st.columns(3)
        col1.metric("Строки", df.shape[0])
        col2.metric("Столбцы", df.shape[1])
        col3.metric("Пропущенные значения", int(df.isna().sum().sum()))

        with st.expander("Названия столбцов"):
            st.write(list(df.columns))

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")

if user_instruction:
    st.info("Инструкция получена.")


if st.button("Запустить AI-агента"):

    with st.spinner("Агент анализирует данные..."):
        output = run_agent(df, user_instruction)

    st.subheader("Сгенерированный код")
    st.code(output["code"], language="python")

    result = output["result"]

    if result["ok"]:
        st.success("Код выполнен успешно")
    else:
        st.error("Ошибка выполнения")
        st.code(result["error"])

    if result["stdout"]:
        st.subheader("Вывод")
        st.text(result["stdout"])

    if result["result_text"]:
        st.subheader("Итог от кода")
        st.write(result["result_text"])

    if result["result_df"] is not None:
        st.subheader("Таблица результата")
        st.dataframe(result["result_df"])

    if result["matplotlib_figures"]:
        st.subheader("Графики")
        for fig in result["matplotlib_figures"]:
            st.pyplot(fig)
