import streamlit as st

st.set_page_config(page_title="LLM Data Analyst", layout="wide")

st.title("LLM Data Analyst")
st.write("Анализируй данные")

uploaded_file = st.file_uploader("Загрузите CSV", type=["csv"])

user_instruction = st.text_area(
    "Инструкция для анализа",
    placeholder="Например: найди аномалии, покажи основные метрики, проверь выбросы"
)

if uploaded_file is not None:
    st.success(f"Файл загружен: {uploaded_file.name}")

if user_instruction:
    st.info("Инструкция получена.")