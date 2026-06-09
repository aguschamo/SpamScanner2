import pandas as pd

df = pd.read_csv('SpamCollectionSpanish.csv')

print("Columnas:", df.columns.tolist())
print("\nCantidad de cada tipo:")
print(df['label'].value_counts())

df = df.rename(columns={'text': 'message'})
df['label'] = df['label'].map({0: 'ham', 1: 'spam'})

ham_sample = df[df['label'] == 'ham'].sample(n=50, random_state=42)
spam_sample = df[df['label'] == 'spam'].sample(n=50, random_state=42)

dataset_100 = pd.concat([ham_sample, spam_sample]).reset_index(drop=True)
dataset_100.to_csv('dataset_100.csv', index=False)

print("\n✅ ¡Listo! Se creó dataset_100.csv")
print(f"Total: {len(dataset_100)} mensajes (50 ham + 50 spam)")