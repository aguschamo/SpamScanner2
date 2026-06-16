import pandas as pd
import ast
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------
# CAPA DE LÓGICA FORMAL (Pure Python)
# ------------------------------------------------------------------
PESOS = {"MONEY": 3, "PHONE": 3, "URL": 2, "CAPS": 1, "WORD": 0}
UMBRAL = 5  # Umbral balanceado por defecto

def calcular_score(tokens):
    """Calcula la suma de pesos de una lista de tokens."""
    return sum(PESOS.get(token, 0) for token in tokens)

def clasificar(tokens, umbral=UMBRAL):
    """Clasifica como spam si el score supera el umbral."""
    return "spam" if calcular_score(tokens) > umbral else "ham"

# ------------------------------------------------------------------
# CAPA DE DATOS (Pandas)
# ------------------------------------------------------------------
def main():
    print("\n  ╔════════════════════════════════════════════╗")
    print("  ║  SpamScanner 2.0 — Etapa 3: Clasificador   ║")
    print("  ╚════════════════════════════════════════════╝")

    project_root = Path(__file__).resolve().parent.parent
    ruta_entrada = project_root / "mensajes_tokenizados.csv"

    if not ruta_entrada.exists():
        print(f"Error: No se encontró {ruta_entrada}. Ejecute la Etapa 2 primero.")
        sys.exit(1)

    print(f"  Cargando dataset desde: {ruta_entrada.name}...")
    df = pd.read_csv(ruta_entrada)

    # Parsear la columna tokens (está como string en el CSV)
    df['tokens'] = df['tokens'].apply(ast.literal_eval)

    print("  Clasificando mensajes...")
    df['score'] = df['tokens'].apply(calcular_score)
    df['prediccion'] = df['tokens'].apply(clasificar)

    # Exportar resultados para la Etapa 4
    output_path = project_root / "resultados_etapa3.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Etapa 3 completada. Archivo guardado: {output_path}")
    
    # Mostrar resumen rápido
    counts = df['prediccion'].value_counts()
    print(f"Resultados: Spam: {counts.get('spam', 0)}, Ham: {counts.get('ham', 0)}")

if __name__ == "__main__":
    main()
