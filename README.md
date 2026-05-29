# SpamScanner 2.0
**TP Integrador · Autómatas y Gramáticas · 2026**

Sistema de clasificación de SMS spam/ham usando modelos formales.

## Integrantes
- Constanza Arancibia
- Mía Manchaca
- Agustina Chamorro

## Pipeline
```
Texto crudo SMS
  ↓ Etapa 1 — Máquina de Turing     → Normalización
  ↓ Etapa 2 — Expresiones Regulares → Tokenización
  ↓ Etapa 3 — Heurística de pesos   → Clasificación spam/ham
  ↓ Etapa 4 — Gramática LC          → Validación estructural
  ↓ Veredicto: HAM / SPAM / SPAM ATÍPICO
```

## Estructura
```
SpamScanner2/
├── main.py                        # Script principal (corre todo el pipeline)
├── data/
│   └── SMSSpamCollection.tsv      # Dataset (NO subir al repo, ver abajo)
├── etapa1_mt/
│   └── maquina_turing.py
├── etapa2_regex/
│   └── tokenizador.py
├── etapa3_clasificador/
│   └── clasificador.py
├── etapa4_glc/
│   └── gramatica.py
└── informe/
```

## Cómo correr el proyecto
1. Clonar el repo:
```bash
git clone https://github.com/aguschamo/SpamScanner2
cd SpamScanner2
```
2. Colocar el dataset en `data/SMSSpamCollection.tsv`
   (Descargar de: https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)

3. Correr el pipeline:
```bash
python main.py
```

## Dataset
El dataset **no está en el repo** por su tamaño. Descargarlo de Kaggle y colocarlo en `data/`.