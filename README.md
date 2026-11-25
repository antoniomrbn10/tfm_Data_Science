# Reseñas AI

Agente que clasifica las reseñas de clientes de un negocio, **avisa de las que requieren atención humana** y
prepara borradores de respuesta que una persona revisa antes de publicar. Caso de partida: el restaurante
Cortijo Vistalegre (Cazalla de la Sierra), con autorización de los propietarios.

## Estructura del repositorio

```
.
├── README.md
├── .gitignore                       # excluye los datos reales (en la raíz)
├── requirements.txt
├── docs/
│   └── entregas/
│       ├── 02_datos_y_preparacion.md
│       └── 03_machine_learning.md
├── src/
│   ├── pipeline.py                  # Bronze -> Silver -> Gold (entrega 2)
│   └── score_reviews.py             # escribe gold_predictions (entrega 3)
├── notebooks/
│   ├── 02_datos.ipynb               # exploración de los datos (sin texto de reseñas)
│   └── 03_evaluacion.ipynb          # comparación final de sistemas (sin texto de reseñas)
├── results/                         # resultados de la evaluación, sin texto
│   ├── holdout_resultados.csv
│   └── resultados_comparacion.csv
└── data/
    ├── plantillas_respuesta.md      # plantillas de respuesta validadas con los propietarios
    ├── holdout_labels.csv           # etiquetas humanas del conjunto reservado (id + etiqueta, sin texto)
    ├── bronze/                      # ⚠ datos reales (43 JSON de Google Takeout). NO está en el repo
    ├── reviews.db                   # ⚠ base de datos generada. NO está en el repo
    └── sample/                      # lo único de datos que sí está en el repo
        ├── bronze_demo/             #   reseñas INVENTADAS en formato Takeout (entrada de la demo)
        ├── demo_silver.csv          #   resultado de la demo: capa Silver
        ├── demo_gold.csv            #   resultado de la demo: capa Gold
        └── holdout_ids.csv          #   solo identificadores (hash) del conjunto reservado, sin texto
```

## Qué usa y genera cada script

| Script | Lee | Genera |
|---|---|---|
| `src/pipeline.py` (real) | `data/bronze/*.json` | `data/reviews.db` (`silver_reviews`, `gold_reviews`, `holdout_reviews`) y `data/sample/holdout_ids.csv` |
| `src/pipeline.py --demo` | `data/sample/bronze_demo/*.json` | `data/sample/demo_silver.csv` y `demo_gold.csv` |
| `src/score_reviews.py` | tabla `gold_reviews` de `data/reviews.db` | tabla `gold_predictions` en la misma base de datos |

Los scripts calculan las rutas respecto a su ubicación: **deben estar en `src/`** y ejecutarse desde la raíz del repo.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt

# Demostración (funciona con lo que hay en el repo; reseñas inventadas)
python src/pipeline.py --demo

# Ejecución real (necesita los datos reales en data/bronze/, que no se publican)
python src/pipeline.py
python src/score_reviews.py          # descarga el modelo la primera vez (~670 MB)
```

La evaluación final se ejecuta en `notebooks/03_evaluacion.ipynb` (pensado para Google Colab).

## Sobre los datos y la privacidad

- Los datos reales son reseñas de clientes. Aunque se elimina el nombre del autor (en la capa Silver), **el texto de
  una reseña todavía puede identificar a alguien**, así que ningún texto real se publica en este repositorio.
- Para enseñar el proceso se usan reseñas **inventadas** (`data/sample/bronze_demo/`) con la misma estructura que el
  export real.
- Los ficheros del repo con información del conjunto reservado (`holdout_ids.csv`, `holdout_labels.csv`,
  `results/`) contienen solo identificadores hash, etiquetas y cifras, **sin texto**.

## Documentación

- [Entrega 2 · Datos y preparación](docs/entregas/02_datos_y_preparacion.md)
- [Entrega 3 · Machine Learning](docs/entregas/03_machine_learning.md)
