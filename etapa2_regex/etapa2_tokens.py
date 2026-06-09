#  SpamScanner 2.0 — Etapa 2: Tokenización con Expresiones Regulares
import re
import pandas as pd

PATRONES = [

    # MONEY: símbolo monetario + dígitos  O  dígitos + símbolo monetario
    # Ejemplos: $5000  |  100€  |  £50
    ("MONEY", re.compile(r'[\$£€]\d+|\d+[\$£€]')),

    # URL: empieza con http, https o www
    # Ejemplos: http://spam.com  |  www.premios.net
    ("URL", re.compile(r'https?://\S+|www\.\S+')),

    # PHONE: 7 o más dígitos seguidos (sin letras alrededor)
    # Ejemplos: 01144445555  |  5551234
    ("PHONE", re.compile(r'\b\d{7,}\b')),

    # CAPS: palabra de 3 o más letras TODAS en mayúsculas
    # Ejemplos: GANASTE  |  AHORA  |  WIN
    # \b = límite de palabra (no agarra letras pegadas)
    ("CAPS", re.compile(r'\b[A-ZÁÉÍÓÚÜÑ]{3,}\b')),

    # WORD: cualquier secuencia de letras o dígitos que no matcheó antes
    # Ejemplos: hola  |  Llamá  |  ok
    ("WORD", re.compile(r'\b\w+\b')),
]

# ------------------------------------------------------------------
# Función principal: tokenizar un mensaje
# ------------------------------------------------------------------
def tokenizar(texto):
    """
    Recibe un texto normalizado (salida de la Etapa 1)
    y devuelve una lista de tokens clasificados.

    Ejemplo:
      entrada: "GANASTE $5000 llamá al 01144445555"
      salida:  [("CAPS","GANASTE"), ("MONEY","$5000"),
                ("WORD","llamá"), ("WORD","al"), ("PHONE","01144445555")]
    """
    tokens = []
    texto_restante = texto  # vamos "consumiendo" el texto

    while texto_restante:

        # Saltar espacios
        if texto_restante[0] == " ":
            texto_restante = texto_restante[1:]
            continue

        matcheado = False

        # Probar cada patrón en orden
        for nombre_token, patron in PATRONES:
            match = patron.match(texto_restante)
            if match:
                tokens.append((nombre_token, match.group()))
                texto_restante = texto_restante[len(match.group()):]
                matcheado = True
                break

        # Si ningún patrón matcheó, avanzar un carácter
        if not matcheado:
            texto_restante = texto_restante[1:]

    return tokens


def solo_tipos(tokens):
    """
    De la lista de tokens, devuelve solo los tipos (sin el texto).
    Ejemplo: [("CAPS","GANASTE"), ("MONEY","$5000")] → ["CAPS", "MONEY"]
    """
    return [tipo for tipo, _ in tokens]


# ------------------------------------------------------------------
# Demo: mostrar cómo funciona con ejemplos concretos
# ------------------------------------------------------------------
def demo():
    ejemplos = [
        "GANASTE $5000 llamá al 01144445555 AHORA",   # spam típico
        "hola cómo estás todo bien por acá",           # ham típico
        "CLICK www.premios.com GRATIS",                # spam con URL
        "ok nos vemos mañana a las 18",                # ham simple
    ]

    print("\n" + "="*60)
    print("  DEMO — Tokenización con Expresiones Regulares")
    print("="*60)

    for msg in ejemplos:
        tokens = tokenizar(msg)
        tipos  = solo_tipos(tokens)
        print(f"\n  Texto  : {msg}")
        print(f"  Tokens : {tokens}")
        print(f"  Tipos  : {tipos}")
        print("  " + "-"*55)


# ------------------------------------------------------------------
# Procesar el dataset normalizado (salida de la Etapa 1)
# ------------------------------------------------------------------
def procesar_dataset(ruta_csv):
    """
    Lee el CSV generado por la Etapa 1 y tokeniza cada mensaje.
    Devuelve el DataFrame con una columna nueva: 'tokens'
    """
    df = pd.read_csv(ruta_csv)

    print(f"\n  Dataset cargado: {len(df)} mensajes")
    print("  Tokenizando...\n")

    # Aplicar tokenización a cada mensaje limpio
    df['tokens'] = df['text'].apply(lambda x: solo_tipos(tokenizar(str(x))))

    # Mostrar ejemplos
    print("  === EJEMPLOS DE TOKENIZACIÓN ===\n")
    print(f"  {'─'*60}")
    for i in range(5):
        etiqueta = "SPAM" if df['label'].iloc[i] == 1 else "HAM"
        print(f"  [{etiqueta}] Texto  : {str(df['text'].iloc[i])[:55]}")
        print(f"  [{etiqueta}] Tokens : {df['tokens'].iloc[i]}")
        print(f"  {'─'*60}")

    return df


# ------------------------------------------------------------------
# Punto de entrada
# ------------------------------------------------------------------
if __name__ == "__main__":

    print("\n  ╔══════════════════════════════════════╗")
    print("  ║  SpamScanner 2.0 — Etapa 2: Tokens  ║")
    print("  ╚══════════════════════════════════════╝")

    # 1. Demo con ejemplos inventados (para entender cómo funciona)
    demo()

    # 2. Procesar el dataset real de la Etapa 1
    #    El archivo lo generó tu compañera en etapa1_mt/
    ruta = "etapa1_mt/mensajes_normalizados.csv"
    df_tokens = procesar_dataset(ruta)

    # 3. Guardar resultado para la Etapa 3
    df_tokens.to_csv("mensajes_tokenizados.csv", index=False)

# Mostrar ejemplos de SPAM para verificar
print("\n  === EJEMPLOS SPAM (para verificar) ===\n")
spam_df = df_tokens[df_tokens['label'] == 1].head(5)
for i in range(len(spam_df)):
    print(f"  [SPAM] Texto  : {str(spam_df['text'].iloc[i])[:55]}")
    print(f"  [SPAM] Tokens : {spam_df['tokens'].iloc[i]}")
    print(f"  {'─'*60}")
  