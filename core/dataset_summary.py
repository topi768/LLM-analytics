import pandas as pd


def build_dataset_summary(df: pd.DataFrame) -> str:


    summary = []

    summary.append(f"Размер датасета: {df.shape}")

    summary.append(f"Колонки: {list(df.columns)}")

    summary.append("\nТипы данных:")
    summary.append(str(df.dtypes))

    summary.append("\nКоличество пропусков:")
    summary.append(str(df.isna().sum()))

    summary.append("\nПервые 5 строк:")
    summary.append(df.head(5).to_string())

    return "\n".join(summary)