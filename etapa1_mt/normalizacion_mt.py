import pandas as pd
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------
# CAPA DE LÓGICA FORMAL (Pure Python)
# ------------------------------------------------------------------
Q0       = "q0"
Q_ACCEPT = "q_accept"
BLANCO   = None

def delta(estado, simbolo):
    if estado == Q0:
        if simbolo is BLANCO:
            return (BLANCO, Q_ACCEPT)
        elif simbolo.isalnum() or simbolo in " $.:/":
            return (simbolo, Q0)
        else:
            return (" ", Q0)
    return (simbolo, Q_ACCEPT)

def maquina_turing(mensaje):
    """Recorre el mensaje carácter por carácter y devuelve el normalizado."""
    cinta  = list(str(mensaje))
    cabeza = 0
    estado = Q0

    while estado != Q_ACCEPT:
        simbolo = cinta[cabeza] if cabeza < len(cinta) else BLANCO
        nuevo_simbolo, nuevo_estado = delta(estado, simbolo)
        if nuevo_simbolo is not BLANCO and cabeza < len(cinta):
            cinta[cabeza] = nuevo_simbolo
        cabeza += 1
        estado  = nuevo_estado

    resultado = "".join(cinta)
    return " ".join(resultado.split())

# ------------------------------------------------------------------
# CAPA DE DATOS (Pandas)
# ------------------------------------------------------------------
def main():
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║   SpamScanner 2.0 — Etapa 1: MT     ║")
    print("  ╚══════════════════════════════════════╝")

    project_root = Path(__file__).resolve().parent.parent
    dataset_path = project_root / "data" / "raw" / "SpamCollectionSpanish.csv"
    fallback_path = project_root / "data" / "raw" / "01_dataset_100.csv"

    ruta_entrada = dataset_path if dataset_path.exists() else fallback_path if fallback_path.exists() else None

    if ruta_entrada is None:
        print(f"Error: No se encontró el dataset en {dataset_path} ni en {fallback_path}")
        sys.exit(1)

    print(f"  Cargando dataset desde: {ruta_entrada.name}...")
    df = pd.read_csv(ruta_entrada)

    # Normalización de columnas
    if 'v1' in df.columns and 'v2' in df.columns:
        df = df.rename(columns={'v1': 'label', 'v2': 'text'})
        df['label'] = df['label'].map({'ham': 0, 'spam': 1})
    
    if 'label' not in df.columns or 'text' not in df.columns:
        print("Error: El CSV debe tener columnas 'label' y 'text'")
        sys.exit(1)

    # Muestreo de 100 mensajes
    ham  = df[df['label'].astype(str).str.lower().isin(['0', 'ham'])].head(50)
    spam = df[df['label'].astype(str).str.lower().isin(['1', 'spam'])].head(50)
    df_100 = pd.concat([ham, spam]).reset_index(drop=True)

    print(f"Procesando {len(df_100)} mensajes...")
    df_100['mensaje_limpio'] = df_100['text'].apply(maquina_turing)

    output_path = project_root / "data" / "raw" / "01_dataset_100.csv"
    df_100.to_csv(output_path, index=False)
    print(f"Etapa 1 completada. Archivo guardado: {output_path}")

if __name__ == "__main__":
    main()
