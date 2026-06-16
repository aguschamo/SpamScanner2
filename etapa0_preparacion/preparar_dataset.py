import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "data" / "raw"

df = pd.read_csv(raw_dir / "SpamCollectionSpanish.csv")

print("Columnas:", df.columns.tolist())
print("\nCantidad de cada tipo:")
print(df['label'].value_counts())

df = df.rename(columns={'text': 'message'})
df['label'] = df['label'].map({0: 'ham', 1: 'spam'})

ham_sample = df[df['label'] == 'ham'].sample(n=50, random_state=42)
spam_sample = df[df['label'] == 'spam'].sample(n=50, random_state=42)

dataset_100 = pd.concat([ham_sample, spam_sample]).reset_index(drop=True)
dataset_100.to_csv(raw_dir / "01_dataset_100.csv", index=False)

print("\nListo, Se creó dataset_100.csv")
print(f"Total: {len(dataset_100)} mensajes (50 ham + 50 spam)")