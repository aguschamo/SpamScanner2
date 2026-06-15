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
        if self.posicion >= len(self.tokens):
            return None
        return self.tokens[self.posicion]

    def consumir(self, token_esperado: str) -> bool:
        if self.actual() == token_esperado:
            self.posicion += 1
            return True
        return False

    def parse_S(self) -> bool:
        posicion_inicial = self.posicion

        if not self.parse_G():
            self.posicion = posicion_inicial
            return False

        if not self.parse_C():
            self.posicion = posicion_inicial
            return False

        if not self.parse_F():
            self.posicion = posicion_inicial
            return False

        return True

    def parse_G(self) -> bool:
        if not self.consumir("caps"):
            return False

        while self.actual() == "caps":
            self.consumir("caps")

        return True

    def parse_C(self) -> bool:
        posicion_inicial = self.posicion

        producciones = [
            ["money", "text"],
            ["text", "money"],
            ["money"],
            ["text"],
        ]

        for produccion in producciones:
            self.posicion = posicion_inicial
            acepta = True

            for token_esperado in produccion:
                if not self.consumir(token_esperado):
                    acepta = False
                    break

            if acepta:
                return True

        self.posicion = posicion_inicial
        return False

    def parse_F(self) -> bool:
        return self.consumir("contact")


def validate_structure(tokens: list[str]) -> bool:
    if not isinstance(tokens, list):
        return False

    parser = ParserGLC(tokens)
    acepta = parser.parse_S()

    return acepta and parser.posicion == len(tokens)


def classify_final_spam(df_spam: pd.DataFrame) -> pd.DataFrame:
    df_result = df_spam.copy()

    tokens_reducidos_columna = []
    acepta_glc_columna = []
    clasificacion_columna = []

    for tokens in df_result["tokens"]:
        tokens_reducidos = reduce_tokens(tokens)
        acepta_glc = validate_structure(tokens_reducidos)
        clasificacion = "Spam Canónico" if acepta_glc else "Spam Atípico"

        tokens_reducidos_columna.append(json.dumps(tokens_reducidos, ensure_ascii=False))
        acepta_glc_columna.append(acepta_glc)
        clasificacion_columna.append(clasificacion)

    df_result["tokens_reducidos"] = tokens_reducidos_columna
    df_result["acepta_glc"] = acepta_glc_columna
    df_result["clasificacion"] = clasificacion_columna

    return df_result


def generate_statistics(df_result: pd.DataFrame) -> None:
    total_spam = len(df_result)
    total_canonico = int((df_result["clasificacion"] == "Spam Canónico").sum())
    total_atipico = int((df_result["clasificacion"] == "Spam Atípico").sum())

    porcentaje_canonico = (total_canonico / total_spam * 100) if total_spam else 0.0
    porcentaje_atipico = (total_atipico / total_spam * 100) if total_spam else 0.0

    patrones_canonicos = Counter()
    patrones_atipicos = Counter()

    for _, fila in df_result.iterrows():
        tokens_reducidos = json.loads(fila["tokens_reducidos"])
        patron = " → ".join(tokens_reducidos)

        if fila["clasificacion"] == "Spam Canónico":
            patrones_canonicos[patron] += 1
        else:
            patrones_atipicos[patron] += 1

    print("=== ESTADÍSTICAS ETAPA 4 ===")
    print(f"Total spam procesado    : {total_spam}")
    print(f"Spam Canónico (GLC ✓)  : {total_canonico}  ({porcentaje_canonico:.1f}%)")
    print(f"Spam Atípico  (GLC ✗)  : {total_atipico}  ({porcentaje_atipico:.1f}%)")
    print()
    print("Top 5 patrones en Spam Canónico:")
    for patron, cantidad in patrones_canonicos.most_common(5):
        print(f"  {patron} : {cantidad} mensajes")
    print()
    print("Top 5 patrones en Spam Atípico:")
    for patron, cantidad in patrones_atipicos.most_common(5):
        print(f"  {patron} : {cantidad} mensajes")


if __name__ == "__main__":
    raiz_proyecto = Path(__file__).resolve().parent.parent
    rutas_etapa3 = [
        raiz_proyecto / "etapa3_clasificacion" / "resultados_etapa3.csv",
        raiz_proyecto / "resultados_etapa3.csv",
    ]

    ruta_entrada = next((ruta for ruta in rutas_etapa3 if ruta.exists()), None)

    if ruta_entrada is None:
        print("No se encontró el CSV de salida de Etapa 3.")
        print("Rutas buscadas:")
        for ruta in rutas_etapa3:
            print(f"  - {ruta}")
        sys.exit(1)

    df = pd.read_csv(ruta_entrada)
    df["tokens"] = df["tokens"].apply(ast.literal_eval)
    df_spam = df[df["prediccion"] == "spam"]

    df_result = classify_final_spam(df_spam)
    generate_statistics(df_result)

    ruta_salida = raiz_proyecto / "etapa4_glc" / "resultados_glc.csv"
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df_result.to_csv(ruta_salida, index=False)

    print()
    print(f"Resultado guardado en: {ruta_salida}")
    print()

    ejemplos_canonicos = df_result[df_result["clasificacion"] == "Spam Canónico"].head(3)
    ejemplos_atipicos = df_result[df_result["clasificacion"] == "Spam Atípico"].head(3)

    print("=== EJEMPLOS SPAM CANÓNICO ===")
    for _, fila in ejemplos_canonicos.iterrows():
        reducido = " → ".join(json.loads(fila["tokens_reducidos"]))
        print(f"Texto    : {str(fila['text'])[:60]}")
        print(f"Reducido : {reducido}")
        print("GLC      : ✓ Canónico")
        print()

    print("=== EJEMPLOS SPAM ATÍPICO ===")
    for _, fila in ejemplos_atipicos.iterrows():
        reducido = " → ".join(json.loads(fila["tokens_reducidos"]))
        print(f"Texto    : {str(fila['text'])[:60]}")
        print(f"Reducido : {reducido}")
        print("GLC      : ✗ Atípico")
        print()
