import pandas as pd


def load_data(uploaded_file):
    """
    Загружает CSV или Excel файл и возвращает pandas.DataFrame.
    """
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return pd.read_excel(uploaded_file)

    else:
        raise ValueError("Поддерживаются только CSV и Excel файлы.")