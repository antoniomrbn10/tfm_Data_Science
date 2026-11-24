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
├── docs/entregas/
│   └── 02_datos_y_preparacion.md    # documento de la entrega 2
├── src/
│   └── pipeline.py                  # script Bronze -> Silver -> Gold
├── notebooks/
│   └── 02_datos.ipynb               # exploración de los datos (EDA), sin texto de reseñas
└── data/
    ├── plantillas_respuesta.md      # plantillas de respuesta validadas con los propietarios
    ├── bronze/                      # ⚠ datos reales (43 JSON de Google Takeout). NO está en el repo
    ├── reviews.db                   # ⚠ base de datos generada. NO está en el repo
    └── sample/                      # lo único de datos que sí está en el repo
        ├── bronze_demo/             #   reseñas INVENTADAS en formato Takeout (entrada de la demo)
        ├── demo_silver.csv          #   resultado de la demo: capa Silver
        ├── demo_gold.csv            #   resultado de la demo: capa Gold
        └── holdout_ids.csv          #   solo identificadores (hash) del conjunto reservado, sin texto
```

## Qué usa y genera `src/pipeline.py`

| | Ruta |
|---|---|
| **Lee** (ejecución real) | `data/bronze/*.json` |
| **Genera** (ejecución real) | `data/reviews.db` (tablas `silver_reviews`, `gold_reviews`, `holdout_reviews`) y `data/sample/holdout_ids.csv` |
| **Lee** (demo) | `data/sample/bronze_demo/*.json` |
| **Genera** (demo) | `data/sample/demo_silver.csv` y `data/sample/demo_gold.csv` |

El script calcula las rutas respecto a su propia ubicación, por lo que **debe estar en `src/`** y ejecutarse desde la raíz del repo.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt

# 1. Demostración (funciona con lo que hay en el repo; reseñas inventadas)
python src/pipeline.py --demo

# 2. Ejecución real (necesita los datos reales en data/bronze/, que no se publican)
python src/pipeline.py
```

## Sobre los datos y la privacidad

- Los datos reales son reseñas de clientes. Aunque se elimina el nombre del autor (en la capa Silver), **el texto de
  una reseña todavía puede identificar a alguien**, así que ningún texto real se publica en este repositorio.
- Para enseñar el proceso se usan reseñas **inventadas** (`data/sample/bronze_demo/`) con la misma estructura que el
  export real: distintos formatos de traducción, reseñas sin texto, una respuesta del propietario y una reseña
  repetida a propósito para mostrar la deduplicación.
- Los identificadores de `holdout_ids.csv` son hashes y no contienen texto.

## Documentación

- [Entrega 2 · Datos y preparación](docs/entregas/02_datos_y_preparacion.md)
