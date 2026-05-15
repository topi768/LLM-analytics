import pandas as pd

file_path = "all_regions.csv"

chunks = []
chunk_size = 100_000  # читаем по кускам

for chunk in pd.read_csv(file_path, chunksize=chunk_size):
    sample = chunk.sample(frac=0.05, random_state=42)  # 5% из каждого куска
    chunks.append(sample)

df_sample = pd.concat(chunks, ignore_index=True)

# если нужно ровно 10k строк
df_sample = df_sample.sample(n=10_000, random_state=42)

df_sample.to_csv("sample_10k.csv", index=False)