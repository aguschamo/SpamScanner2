import csv
from pathlib import Path

# ------------------------------------------------------------------
# Los dos estados de la MT
# ------------------------------------------------------------------
Q0       = "q0"        # estado de trabajo
Q_ACCEPT = "q_accept"  # estado final
BLANCO   = None        # símbolo blanco B (fin de cinta)

# ------------------------------------------------------------------
# Función de transición δ  ← ESTO ES LO QUE PIDE EL ENUNCIADO
# Dado el estado actual y el símbolo leído,
# devuelve (qué escribir, siguiente estado)
# ------------------------------------------------------------------
def delta(estado, simbolo):
    if estado == Q0:
        if simbolo is BLANCO:
            return (BLANCO, Q_ACCEPT)                    # fin de cinta → terminar
        elif simbolo.isalnum() or simbolo in " $.:/":
            return (simbolo, Q0)                         # válido → conservar
        else:
            return (" ", Q0)                             # inválido → reemplazar
    return (simbolo, Q_ACCEPT)


# ------------------------------------------------------------------
# Máquina de Turing — simula la cinta paso a paso
# ------------------------------------------------------------------
def maquina_turing(mensaje, mostrar_traza=False):
    """
    Recorre el mensaje carácter por carácter usando la función delta.
    Devuelve el mensaje normalizado.
    """
    cinta  = list(mensaje)   # la cinta es una lista de caracteres
    cabeza = 0               # posición de la cabeza lectora
    estado = Q0              # empezamos en q0

    if mostrar_traza:
        print()
        print("=" * 55)
        print("  TRAZA DE EJECUCIÓN — Máquina de Turing")
        print(f"  Entrada: {repr(mensaje)}")
        print("=" * 55)
        print(f"  {'Paso':>4}  {'Estado':<10}  {'Lee':>6}  →  {'Escribe':>8}  Sig. estado")
        print("  " + "-" * 52)

    paso = 0
    while estado != Q_ACCEPT:

        # Leer símbolo bajo la cabeza (o blanco si llegamos al final)
        simbolo = cinta[cabeza] if cabeza < len(cinta) else BLANCO

        # Aplicar función de transición
        nuevo_simbolo, nuevo_estado = delta(estado, simbolo)

        if mostrar_traza:
            lee     = repr(simbolo)       if simbolo       is not BLANCO else "B"
            escribe = repr(nuevo_simbolo) if nuevo_simbolo is not BLANCO else "B"
            print(f"  {paso:>4}  {estado:<10}  {lee:>6}  →  {escribe:>8}  {nuevo_estado}")

        # Escribir en la cinta
        if nuevo_simbolo is not BLANCO and cabeza < len(cinta):
            cinta[cabeza] = nuevo_simbolo

        # Avanzar cabeza y actualizar estado
        cabeza += 1
        estado  = nuevo_estado
        paso   += 1

    # Resultado: unir la cinta y limpiar espacios dobles
    resultado = "".join(cinta)
    resultado = " ".join(resultado.split())   # <-- idea del código de ChatGPT, está buena

    if mostrar_traza:
        print("  " + "-" * 52)
        print(f"  Estado final : {estado}  ✓")
        print(f"  Salida       : {repr(resultado)}")
        print("=" * 55)
        print()

    return resultado


# ------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------------------------------------------
if __name__ == "__main__":

    print("\n  ╔══════════════════════════════════════╗")
    print("  ║   SpamScanner 2.0 — Etapa 1: MT     ║")
    print("  ╚══════════════════════════════════════╝")

    # 1. Traza del ejemplo del enunciado (para el informe)
    print("\n  📌 Traza del ejemplo del enunciado:")
    maquina_turing("WIN $1000 now!", mostrar_traza=True)

    # 2. Cargar el dataset con la biblioteca estándar de Python
    print("  Cargando dataset...")
    
    # Usar ruta absoluta desde la raíz del proyecto
    project_root = Path(__file__).parent.parent  # sube a SpamScanner2/
    dataset_path = project_root / "data" / "SpamCollectionSpanish.csv"
    fallback_path = project_root / "dataset_100.csv"
    
    if not dataset_path.exists() and fallback_path.exists():
        dataset_path = fallback_path

    if not dataset_path.exists():
        print(f"  ❌ Error: No se encontró {dataset_path}")
        exit(1)

    with open(dataset_path, newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        filas = list(lector)

    if filas and "v1" in filas[0] and "v2" in filas[0]:
        mensajes = [{"label": fila["v1"], "text": fila["v2"]} for fila in filas]
    elif filas and "label" in filas[0] and "text" in filas[0]:
        mensajes = [{"label": fila["label"], "text": fila["text"]} for fila in filas]
    elif filas and "label" in filas[0] and "message" in filas[0]:
        mensajes = [{"label": fila["label"], "text": fila["message"]} for fila in filas]
    else:
        print("  ❌ Error: El dataset debe tener columnas 'label' y 'text', 'label' y 'message', o 'v1' y 'v2'")
        columnas = list(filas[0].keys()) if filas else []
        print(f"  Columnas encontradas: {columnas}")
        exit(1)

    # Tomar 50 ham + 50 spam
    ham = [mensaje for mensaje in mensajes if str(mensaje["label"]).strip().lower() in {"0", "ham"}][:50]
    spam = [mensaje for mensaje in mensajes if str(mensaje["label"]).strip().lower() in {"1", "spam"}][:50]
    mensajes_100 = ham + spam

    print(f"  Dataset: {len(mensajes_100)} mensajes ({len(ham)} ham + {len(spam)} spam)\n")

    # 3. Aplicar la MT a todos los mensajes
    print("  Aplicando Máquina de Turing...")
    for mensaje in mensajes_100:
        mensaje["mensaje_limpio"] = maquina_turing(mensaje["text"])

    # 4. Mostrar ejemplos
    print("\n  === EJEMPLOS ANTES Y DESPUÉS ===\n")
    indices_ejemplo = list(range(min(5, len(mensajes_100)))) + list(range(50, min(55, len(mensajes_100))))
    for i in indices_ejemplo:
        etiqueta = "SPAM" if str(mensajes_100[i]["label"]).strip().lower() in {"1", "spam"} else "HAM"
        print(f"  [{etiqueta}] Original : {mensajes_100[i]['text'][:60]}")
        print(f"  [{etiqueta}] Limpio   : {mensajes_100[i]['mensaje_limpio'][:60]}")
        print("  " + "-" * 65)

    # 5. Guardar resultado para la Etapa 2
    output_path = project_root / "dataset_100.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as archivo_salida:
        columnas = ["text", "label", "mensaje_limpio"]
        escritor = csv.DictWriter(archivo_salida, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(mensajes_100)
    print("\n  ✅ Etapa 1 completada.")
    print(f"  Archivo guardado: {output_path}")
    print("  Listo para la Etapa 2.\n")
