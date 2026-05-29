import pandas as pd

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
    resultado = " ".join(resultado.split())   # ← idea del código de ChatGPT, está buena

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

    # 2. Cargar el dataset con pandas (idea del código de ChatGPT)
    print("  Cargando dataset...")
    df = pd.read_csv('../SpamCollectionSpanish.csv')

    # Tomar 50 ham + 50 spam
    ham  = df[df['label'] == 0].head(50)
    spam = df[df['label'] == 1].head(50)
    df_100 = pd.concat([ham, spam]).reset_index(drop=True)

    print(f"  Dataset: {len(df_100)} mensajes ({len(ham)} ham + {len(spam)} spam)\n")

    # 3. Aplicar la MT a todos los mensajes
    print("  Aplicando Máquina de Turing...")
    df_100['mensaje_limpio'] = df_100['text'].apply(maquina_turing)

    # 4. Mostrar ejemplos
    print("\n  === EJEMPLOS ANTES Y DESPUÉS ===\n")
    for i in list(range(5)) + list(range(50, 55)):
        etiqueta = "SPAM" if df_100['label'].iloc[i] == 1 else "HAM"
        print(f"  [{etiqueta}] Original : {df_100['text'].iloc[i][:60]}")
        print(f"  [{etiqueta}] Limpio   : {df_100['mensaje_limpio'].iloc[i][:60]}")
        print("  " + "-" * 65)

    # 5. Guardar resultado para la Etapa 2
    df_100.to_csv('mensajes_normalizados.csv', index=False)
    print("\n  ✅ Etapa 1 completada.")
    print("  Archivo guardado: mensajes_normalizados.csv")
    print("  Listo para la Etapa 2.\n")
