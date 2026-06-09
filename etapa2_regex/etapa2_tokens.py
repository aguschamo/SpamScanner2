#  SpamScanner 2.0 — Etapa 2: Tokenización con Expresiones Regulares
import re
import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
    Devuelve una lista de diccionarios con una columna nueva: 'tokens'
    """
    with open(ruta_csv, newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        mensajes = list(lector)

    print(f"\n  Dataset cargado: {len(mensajes)} mensajes")
    print("  Tokenizando...\n")

    # Aplicar tokenización a cada mensaje limpio
    for mensaje in mensajes:
        texto_para_tokenizar = mensaje.get("mensaje_limpio") or mensaje.get("text") or mensaje.get("message") or ""
        mensaje["text"] = mensaje.get("text") or mensaje.get("message") or texto_para_tokenizar
        mensaje["tokens"] = solo_tipos(tokenizar(str(texto_para_tokenizar)))

    # Mostrar ejemplos
    print("  === EJEMPLOS DE TOKENIZACIÓN ===\n")
    print(f"  {'─'*60}")
    for i in range(min(5, len(mensajes))):
        etiqueta = "SPAM" if str(mensajes[i]["label"]).strip().lower() in {"1", "spam"} else "HAM"
        print(f"  [{etiqueta}] Texto  : {str(mensajes[i]['text'])[:55]}")
        print(f"  [{etiqueta}] Tokens : {mensajes[i]['tokens']}")
        print(f"  {'─'*60}")

    return mensajes


def guardar_dataset_tokenizado(mensajes, ruta_salida):
    """Guarda los mensajes tokenizados en un CSV para la Etapa 3."""
    columnas = ["text", "label", "mensaje_limpio", "tokens"]

    with open(ruta_salida, "w", newline="", encoding="utf-8") as archivo_salida:
        escritor = csv.DictWriter(archivo_salida, fieldnames=columnas)
        escritor.writeheader()
        for mensaje in mensajes:
            escritor.writerow({columna: mensaje.get(columna, "") for columna in columnas})


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
    project_root = Path(__file__).resolve().parent.parent
    ruta = project_root / "dataset_100.csv"
    df_tokens = procesar_dataset(ruta)

    # 3. Guardar resultado para la Etapa 3
    guardar_dataset_tokenizado(df_tokens, project_root / "mensajes_tokenizados.csv")
    guardar_dataset_tokenizado(df_tokens, project_root / "etapa2_regex" / "mensajes_tokenizados.csv")

# Mostrar ejemplos de SPAM para verificar
    print("\n  === EJEMPLOS SPAM (para verificar) ===\n")
    spam_df = [mensaje for mensaje in df_tokens if str(mensaje["label"]).strip().lower() in {"1", "spam"}][:5]
    for mensaje in spam_df:
        print(f"  [SPAM] Texto  : {str(mensaje['text'])[:55]}")
        print(f"  [SPAM] Tokens : {mensaje['tokens']}")
        print(f"  {'─'*60}")
  
