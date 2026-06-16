import ast
import json
import sys
from collections import Counter
from pathlib import Path
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# -----------------------------------------------------------------------------
# GLC formal de la Etapa 4
# -----------------------------------------------------------------------------
# G = (V, T, P, S)
# V = {S, G, C, F}
# T = {caps, money, text, contact}
# P:
#   S -> G C F
#   G -> caps
#   G -> caps G
#   C -> money
#   C -> text
#   C -> money text
#   C -> text money
#   F -> contact
# -----------------------------------------------------------------------------

def reduce_tokens(tokens: list[str]) -> list[str]:
    reducidos = []
    habia_texto_anterior = False
    for token in tokens:
        if token == "CAPS":
            reducidos.append("caps")
            habia_texto_anterior = False
        elif token == "MONEY":
            reducidos.append("money")
            habia_texto_anterior = False
        elif token in {"PHONE", "URL"}:
            reducidos.append("contact")
            habia_texto_anterior = False
        elif token == "WORD":
            if not habia_texto_anterior:
                reducidos.append("text")
                habia_texto_anterior = True
        else:
            habia_texto_anterior = False
    return reducidos

class ParserGLC:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.posicion = 0

    def actual(self):
        return self.tokens[self.posicion] if self.posicion < len(self.tokens) else None

    def consumir(self, token_esperado: str) -> bool:
        if self.actual() == token_esperado:
            self.posicion += 1
            return True
        return False

    def parse_S(self) -> bool:
        pos_init = self.posicion
        if not self.parse_G():
            self.posicion = pos_init
            return False
        if not self.parse_C():
            self.posicion = pos_init
            return False
        if not self.parse_F():
            self.posicion = pos_init
            return False
        return True

    def parse_G(self) -> bool:
        if not self.consumir("caps"):
            return False
        while self.actual() == "caps":
            self.consumir("caps")
        return True

    def parse_C(self) -> bool:
        pos_init = self.posicion
        opciones = [["money", "text"], ["text", "money"], ["money"], ["text"]]
        for opt in opciones:
            self.posicion = pos_init
            if all(self.consumir(t) for t in opt):
                return True
        self.posicion = pos_init
        return False

    def parse_F(self) -> bool:
        return self.consumir("contact")

def validate_structure(tokens: list[str]) -> bool:
    if not tokens: return False
    parser = ParserGLC(tokens)
    return parser.parse_S() and parser.posicion == len(tokens)

def classify_final_spam(df_spam: pd.DataFrame) -> pd.DataFrame:
    df_result = df_spam.copy()
    reducidos = df_result["tokens"].apply(lambda x: reduce_tokens(x if isinstance(x, list) else ast.literal_eval(x)))
    acepta = reducidos.apply(validate_structure)
    
    df_result["tokens_reducidos"] = reducidos.apply(json.dumps)
    df_result["acepta_glc"] = acepta
    df_result["clasificacion"] = acepta.map({True: "Spam Canónico", False: "Spam Atípico"})
    return df_result

def generate_statistics(df_result: pd.DataFrame) -> None:
    total = len(df_result)
    canonicos = df_result[df_result["acepta_glc"] == True]
    atipicos = df_result[df_result["acepta_glc"] == False]
    
    print("=== ESTADÍSTICAS ETAPA 4 ===")
    print(f"Total spam procesado    : {total}")
    print(f"Spam Canónico (GLC ✓)  : {len(canonicos)}  ({len(canonicos)/total*100:.1f}%)")
    print(f"Spam Atípico  (GLC ✗)  : {len(atipicos)}  ({len(atipicos)/total*100:.1f}%)")
    
    def top_patrones(df):
        counts = Counter(df["tokens_reducidos"].apply(lambda x: " → ".join(json.loads(x))))
        for p, c in counts.most_common(5):
            print(f"  {p} : {c} mensajes")

    print("\nTop 5 patrones en Spam Canónico:")
    top_patrones(canonicos)
    print("\nTop 5 patrones en Spam Atípico:")
    top_patrones(atipicos)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    ruta_entrada = project_root / "resultados_etapa3.csv"

    if not ruta_entrada.exists():
        print(f"Error: No se encontró {ruta_entrada}")
        sys.exit(1)

    df = pd.read_csv(ruta_entrada)
    df_spam = df[df["prediccion"] == "spam"].copy()

    if df_spam.empty:
        print("No hay mensajes clasificados como spam para procesar.")
        sys.exit(0)

    df_result = classify_final_spam(df_spam)
    generate_statistics(df_result)

    output_path = project_root / "etapa4_glc" / "resultados_glc.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_result.to_csv(output_path, index=False)
    print(f"\nEtapa 4 completada. Archivo guardado: {output_path}")
