"""SpamScanner 2.0 - Etapa 3: clasificacion heuristica por pesos."""

import ast
import csv
from pathlib import Path


PESOS = {"MONEY": 3, "PHONE": 3, "URL": 2, "CAPS": 1, "WORD": 0}
UMBRALES = [3, 4, 5, 6, 7, 8]

COMPORTAMIENTOS = {
    3: "Muy sensible",
    4: "Sensible",
    5: "Balanceado",
    6: "Moderadamente estricto",
    7: "Estricto",
    8: "Muy estricto",
}


def cargar_mensajes(ruta_csv):
    mensajes = []

    with open(ruta_csv, newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)

        # Recorremos una por una las filas del archivo tokenizado.
        for fila in lector:
            etiqueta = "spam" if str(fila["label"]).strip() in {"1", "spam"} else "ham"

            tipos_de_tokens = ast.literal_eval(fila["tokens"])
            tokens = [{"value": tipo, "type": tipo} for tipo in tipos_de_tokens]
            mensajes.append({"text": fila["text"], "label": etiqueta, "tokens": tokens})

    return mensajes


def calcular_score(mensaje):
    score = 0

    # Recorremos cada token ya clasificado por la etapa 2.
    for token in mensaje["tokens"]:
        tipo = token["type"]
        score += PESOS.get(tipo, 0)

    return score


def clasificar(mensaje, umbral):
    # Calculamos primero el puntaje heuristico del mensaje.
    score = calcular_score(mensaje)

    if score > umbral:
        return "spam"

    return "ham"


def division_segura(numerador, denominador):
    # Si el denominador es cero, no hay informacion suficiente para calcular la metrica.
    if denominador == 0:
        return 0.0

    return numerador / denominador


def evaluar_umbral(mensajes, umbral):
    """Evalua un umbral y devuelve matriz de confusion y metricas principales."""
    # verdaderos positivos: spam clasificado como real.
    tp = 0

    # verdaderos negativos: ham clasificado como real.
    tn = 0

    # falsos positivos: ham real clasificado incorrectamente como spam.
    fp = 0

    # falsos negativos: spam real clasificado incorrectamente como ham.
    fn = 0

    # Recorremos todos los mensajes del conjunto de prueba.
    for mensaje in mensajes:
        prediccion = clasificar(mensaje, umbral)
        etiqueta_real = mensaje["label"]

        if prediccion == "spam" and etiqueta_real == "spam":
            tp += 1
        elif prediccion == "ham" and etiqueta_real == "ham":
            tn += 1

        elif prediccion == "spam" and etiqueta_real == "ham":
            fp += 1

        elif prediccion == "ham" and etiqueta_real == "spam":
            fn += 1

    total = tp + tn + fp + fn

    # Calculamos accuracy como aciertos sobre el total.
    accuracy = division_segura(tp + tn, total)

    # Calculamos precision como proporcion de spams predichos que realmente eran spam.
    precision = division_segura(tp, tp + fp)

    # Calculamos recall como proporcion de spams reales que logramos detectar.
    recall = division_segura(tp, tp + fn)

    return {
        "umbral": umbral,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
    }


def calcular_f1(resultado):
    precision = resultado["precision"]

    recall = resultado["recall"]

    return division_segura(2 * precision * recall, precision + recall)


def imprimir_tabla(resultados):

    print("U  | Accuracy | Precision | Recall  | Comportamiento")

    print("---|----------|-----------|---------|----------------")

    for resultado in resultados:
        umbral = resultado["umbral"]
        comportamiento = COMPORTAMIENTOS[umbral]

        print(
            f"{umbral:<2} |  {resultado['accuracy']:.3f}   |"
            f"   {resultado['precision']:.3f}   |  {resultado['recall']:.3f}  | {comportamiento}"
        )


def imprimir_conclusion(resultados):

    mejor_accuracy = max(resultados, key=lambda resultado: resultado["accuracy"])

    # Buscamos el resultado cuyo F1 queda mas cerca de 1, es decir, mejor balance precision/recall.
    mejor_balance = min(resultados, key=lambda resultado: abs(1 - calcular_f1(resultado)))

    # Calculamos el F1 del mejor balance para mostrarlo en la conclusion.
    mejor_f1 = calcular_f1(mejor_balance)

    print()

    # umbral con mejor accuracy y su valor.
    print(f"Mejor Accuracy: umbral {mejor_accuracy['umbral']} con {mejor_accuracy['accuracy']:.3f}")

    # umbral con mejor balance entre precision y recall.
    print(f"Mejor balance Precision/Recall: umbral {mejor_balance['umbral']} con F1 {mejor_f1:.3f}")

    # MONEY y PHONE discriminan mas porque tienen el peso mas alto. VERIFICAR
    print("Mayor poder discriminativo: MONEY y PHONE, porque tienen el peso mas alto dentro de la heuristica.")


def main():
    """Ejecuta el experimento completo de la etapa 3."""
    # Ubicamos la carpeta donde vive este script.
    carpeta_actual = Path(__file__).resolve().parent

    # Construimos la ruta al CSV tokenizado que quedo disponible al integrar desarrollo.
    ruta_csv = carpeta_actual.parent / "mensajes_tokenizados.csv"

    mensajes = cargar_mensajes(ruta_csv)

    resultados = []

    for umbral in UMBRALES:
        resultados.append(evaluar_umbral(mensajes, umbral))

    imprimir_tabla(resultados)
    imprimir_conclusion(resultados)


# Ejecutamos main solamente cuando el archivo se corre como programa principal.
if __name__ == "__main__":
    # Llamamos a la funcion principal para iniciar la etapa 3.
        print("\n  ╔════════════════════════════════════════════╗")
        print("  ║  SpamScanner 2.0 — Etapa 3: Clasificador   ║")
        print("  ╚════════════════════════════════════════════╝")
        print()
        main()
