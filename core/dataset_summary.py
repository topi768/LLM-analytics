import pandas as pd


def build_dataset_summary(df: pd.DataFrame) -> str:
    """
    Создаёт краткое текстовое описание датасета для LLM.
    """

    summary = []

    # Размер таблицы
    summary.append(f"Размер датасета: {df.shape}")

    # Названия колонок
    summary.append(f"Колонки: {list(df.columns)}")

    # Типы данных
    summary.append("\nТипы данных:")
    summary.append(str(df.dtypes))

    # Пропуски
    summary.append("\nКоличество пропусков:")
    summary.append(str(df.isna().sum()))

    # Первые строки
    summary.append("\nПервые 5 строк:")
    summary.append(df.head(5).to_string())

    return "\n".join(summary)