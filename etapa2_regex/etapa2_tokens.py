import re
import pandas as pd
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------
# CAPA DE LÓGICA FORMAL (Pure Python)
# ------------------------------------------------------------------
PATRONES = [
    ("MONEY", re.compile(r'[\$£€]\d+|\d+[\$£€]')),
    ("URL", re.compile(r'https?://\S+|www\.\S+')),
    ("PHONE", re.compile(r'\b\d{7,}\b')),
    ("CAPS", re.compile(r'\b[A-ZÁÉÍÓÚÜÑ]{3,}\b')),
    ("WORD", re.compile(r'\b\w+\b')),
]

def tokenizar(texto):
    """Recibe un texto y devuelve una lista de tuplas (TIPO, VALOR)."""
    tokens = []
    texto_restante = str(texto)
    while texto_restante:
        if texto_restante[0] == " ":
            texto_restante = texto_restante[1:]
            continue
        matcheado = False
        for nombre_token, patron in PATRONES:
            match = patron.match(texto_restante)
            if match:
                tokens.append((nombre_token, match.group()))
                texto_restante = texto_restante[len(match.group()):]
                matcheado = True
                break
        if not matcheado:
            texto_restante = texto_restante[1:]
    return tokens

def solo_tipos(tokens):
    """Extrae solo los tipos de la lista de tokens."""
    return [tipo for tipo, _ in tokens]

# ------------------------------------------------------------------
# CAPA DE DATOS (Pandas)
# ------------------------------------------------------------------
def main():
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║  SpamScanner 2.0 — Etapa 2: Tokens  ║")
    print("  ╚══════════════════════════════════════╝")

    project_root = Path(__file__).resolve().parent.parent
    ruta_entrada = project_root / "dataset_100.csv"

    if not ruta_entrada.exists():
        print(f"Error: No se encontró {ruta_entrada}. Ejecute la Etapa 1 primero.")
        sys.exit(1)

    print(f"Cargando dataset desde: {ruta_entrada.name}...")
    df = pd.read_csv(ruta_entrada)

    # Tokenizamos la columna 'mensaje_limpio' (salida de Etapa 1)
    columna_texto = 'mensaje_limpio' if 'mensaje_limpio' in df.columns else 'text'
    df['tokens'] = df[columna_texto].apply(lambda x: solo_tipos(tokenizar(x)))

    output_path = project_root / "mensajes_tokenizados.csv"
    df.to_csv(output_path, index=False)
    print(f"Etapa 2 completada. Archivo guardado: {output_path}")

if __name__ == "__main__":
    main()
