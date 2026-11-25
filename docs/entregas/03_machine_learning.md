# Entrega 03 · Machine Learning

**Producto:** Reseñas AI, un agente que prioriza las reseñas de clientes, avisa de las que requieren atención humana y prepara borradores de respuesta que una persona revisa.
**Entrada:** `gold_reviews` de la [entrega 2](02_datos_y_preparacion.md) (`data/reviews.db`).
**Código:** [`notebooks/03_evaluacion.ipynb`](../../notebooks/03_evaluacion.ipynb) (evaluación) y [`src/score_reviews.py`](../../src/score_reviews.py) (salida para el producto).
**Documentos de apoyo:** [guía de etiquetado](../guia_etiquetado.md) y [protocolo de evaluación](../protocolo_evaluacion.md).

> **Pregunta que guía la entrega:** ¿leer el texto de la reseña aporta algo frente a usar solo la puntuación en estrellas?

## 1. Qué problema resuelve el modelo

- **Funcionalidad:** decidir, para cada reseña, si basta una respuesta tipo (plantillas 1 y 2) o si una persona debe leerla y contestar personalmente (plantilla 3).
- **Usuario y decisión:** el propietario o community manager. Revisa antes las reseñas alertadas y deja que el agente prepare el resto.
- **Tipo de problema:** clasificación binaria (*requiere atención* / *basta una plantilla*).
- **Qué significa "requiere atención":** se define con un criterio humano basado **solo en el texto** (guía de etiquetado), no con las estrellas. Con esto se evita medir las estrellas con las propias estrellas.

## 2. Datos de entrada y salida

- **Datos:** 438 reseñas con texto del Gold, divididas en dos conjuntos:
  - **Reservado:** 109 reseñas (separadas en la entrega 2) etiquetadas a mano, **a ciegas** (sin estrellas ni resultados de ningún modelo). Etiqueta definitiva: **11 SI, 96 NO y 2 excluidas** → **107 evaluables**.
  - **Desarrollo:** 329 reseñas, usadas solo para comprobar que el modelo se comporta, sin ajustar nada para ganar en el reservado.
- **Datos disponibles en el momento de uso:** cuando llega una reseña nueva se conocen sus **estrellas y su texto** (si lo tiene). Por tanto ambos pueden ser entrada. `has_reply` y `reply_text` no existen todavía y **no se usan** (leakage).
- **Salida esperada:** un aviso por reseña (y, para las que tienen texto, una puntuación del modelo).
- **Control de leakage y sesgos:**
  - Las etiquetas se pusieron antes de calcular ningún resultado del modelo, con una guía fijada de antemano.
  - Umbrales y reglas se fijaron **antes** de evaluar (protocolo) y no se ajustan con el reservado.
  - La evaluación final se ejecuta **una sola vez**.
  - Dos reseñas con duda se excluyeron del cálculo (ver limitaciones).
- **Las 417 reseñas sin texto** no se pueden puntuar con el texto: solo cuentan las estrellas.

## 3. Baseline y selección de modelos

| Sistema | Qué hace | Papel |
|---|---|---|
| **B1 · Estrellas ≤ 2** | Alerta con 1 o 2 estrellas | Baseline |
| **B2 · Estrellas ≤ 3** | Alerta con 1, 2 o 3 estrellas | Baseline |
| **M · Modelo sobre el texto** | Modelo preentrenado multilingüe (`nlptown/bert-base-multilingual-uncased-sentiment`), sin reentrenar. Alerta si la probabilidad de ≤ 3 estrellas es ≥ 0,5 | Alternativa de ML |
| **C · Combinación** | Alerta si B2 **o** M alertan | Alternativa de ML |

- **Por qué estos:** las estrellas son la referencia más sencilla y barata. El modelo sobre el texto es la forma de comprobar si aporta algo más. No se valora usar algoritmos complejos por sí mismos.
- **Por qué sin entrenar:** con solo 11 críticas en el reservado y pocas más en total, no hay datos para entrenar un clasificador propio de forma fiable. Un modelo que ya entiende el idioma evita ese problema.
- **Sobre el modelo preentrenado** ([ficha en Hugging Face](https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment)): licencia **MIT**. Es un BERT multilingüe afinado para predecir de 1 a 5 estrellas en **reseñas de productos** en seis idiomas (inglés, neerlandés, alemán, francés, italiano y español; 50.000 reseñas en español). Según su ficha, en reseñas de productos en español acierta la puntuación exacta en el 58% de los casos y con un máximo de una estrella de diferencia en el 95%. La ficha no indica el origen de las reseñas de entrenamiento.
- **Exploración previa descartada:** una primera versión etiquetaba con las estrellas y entrenaba un clasificador de texto para predecirlas (TF-IDF y modelo preentrenado). Se descartó porque medía las estrellas con las estrellas y no respondía a la pregunta.

## 4. Validación y evaluación

**Estrategia:** evaluación única sobre el conjunto reservado, con etiquetas humanas. Sin validación cruzada, porque no hay entrenamiento: los sistemas comparados no aprenden de estos datos. Métricas: **precisión** (de lo que alerta, cuánto es crítica real) y **recall** (de las críticas reales, cuántas detecta), siempre con los **recuentos** y un intervalo de confianza del 95% (Wilson).

| Sistema | Críticas detectadas | Falsas alarmas | No detectadas | Precisión (IC 95%) | Recall (IC 95%) |
|---|---|---|---|---|---|
| B1 · estrellas ≤ 2 | 8 | 0 | 3 | 1,00 (0,68-1,00) | 0,73 (0,43-0,90) |
| B2 · estrellas ≤ 3 | 9 | 1 | 2 | 0,90 (0,60-0,98) | 0,82 (0,52-0,95) |
| M · modelo (texto) | 8 | 4 | 3 | 0,67 (0,39-0,86) | 0,73 (0,43-0,90) |
| C · B2 o M | 10 | 5 | 1 | 0,67 (0,42-0,85) | 0,91 (0,62-0,98) |

*107 reseñas evaluables, 11 críticas reales. Los intervalos se solapan en todos los casos: las diferencias no son estadísticamente concluyentes.*

### Respuesta a la pregunta clave

- **El modelo del texto por sí solo no mejora a las estrellas** en este restaurante: detecta lo mismo que B1 (8 de 11) y añade falsas alarmas.
- **La combinación C detecta 10 de 11 críticas frente a 9 de B2**, pero a cambio de 4 falsas alarmas más (5 frente a 1).
- **Críticas ocultas para las estrellas (4-5★):** hay 2 en el reservado. El modelo detecta 1.
- **Coste del texto:** el modelo marca 5 de las 97 reseñas de 4-5★, de las que solo 1 es crítica real.
- **Conclusión:** en este restaurante las estrellas ya hacen casi todo el trabajo. El texto aporta, como mucho, un pequeño margen que con tan pocos casos **no se puede confirmar**.

### Análisis de errores

Se leyeron a mano los 10 casos en que algún sistema discrepa del criterio humano.

| Tipo de caso | Casos | Qué ocurre |
|---|---|---|
| **El modelo no ve la queja** | 3 críticas | Una reseña larga y razonada sobre el servicio (puntuación 0,46, justo bajo el umbral), una queja ligada a un cobro expresada con ironía, y un reparo serio dentro de una reseña globalmente elogiosa. Son justo los casos en que el texto debería ayudar |
| **El modelo ve queja donde el criterio humano no** | 4 falsas alarmas | Reparos leves en reseñas de 4-5★ ("mejorable", "alto de precio", "no es espectacular") que la guía clasifica como NO. Una reseña de 5★ muy breve y con erratas también sale marcada |
| **Las estrellas se equivocan** | 1 falsa alarma de B2 | Una reseña de 3★ cuyo texto es un elogio |
| **Acierto del texto** | 1 | Una queja breve en una reseña de 4★ que solo el modelo detecta |

**Fragilidad del resultado.** La ventaja de C sobre B2 (10 frente a 9) depende de **una sola reseña**: una crítica breve de 4★ cuya etiqueta es discutible, porque está en la frontera entre "reparo pasajero" (NO) y "queja" (SI) de la guía. Si esa etiqueta fuera NO, el texto no aportaría ninguna crítica adicional y C solo añadiría falsas alarmas.

### Sensibilidad a las dos reseñas excluidas

Se repite el cálculo tratando las 2 reseñas excluidas (1-2 estrellas, que los cuatro sistemas marcan) como críticas (SI) o como no críticas (NO). Cada celda es *precisión / recall*.

| Sistema | Sin las excluidas (tabla principal) | Excluidas como SI | Excluidas como NO |
|---|---|---|---|
| B1 · estrellas ≤ 2 | 1,00 / 0,73 | 1,00 / 0,77 | 0,80 / 0,73 |
| B2 · estrellas ≤ 3 | 0,90 / 0,82 | 0,92 / 0,85 | 0,75 / 0,82 |
| M · modelo (texto) | 0,67 / 0,73 | 0,71 / 0,77 | 0,57 / 0,73 |
| C · B2 o M | 0,67 / 0,91 | 0,71 / 0,92 | 0,59 / 0,91 |

- **La conclusión no cambia:** en los tres escenarios el modelo solo queda por debajo o a la par de las estrellas, y C detecta **una crítica más que B2** (con 4 falsas alarmas más).
- **Lo que sí cambia es la precisión de las reglas de estrellas:** si las excluidas fueran NO, B2 bajaría de 0,90 a 0,75 y B1 de 1,00 a 0,80. Excluirlas las favorecía, pero no lo suficiente para alterar la comparación.

### Limitaciones

- **Solo 11 críticas reales:** una reseña de diferencia mueve el recall unos 9 puntos. Todas las comparaciones son orientativas.
- **Un solo etiquetador,** con casos frontera donde otro criterio podría decidir distinto. Una segunda persona etiquetando parte del conjunto lo cuantificaría.
- **Dos reseñas excluidas** (con 1-2 estrellas): son casos en los que las reglas de estrellas alertan, así que excluirlas favorece ligeramente a esas reglas. Su efecto se cuantifica en la tabla de sensibilidad anterior.
- **La resolución de las dudas** se hizo después de conocer los recuentos de las estrellas y antes de calcular ningún resultado del modelo (enmienda registrada en el protocolo).
- **Un solo negocio,** con perfil turístico y pocas críticas.
- **Dominio distinto y posible contaminación:** el modelo se entrenó con reseñas de productos, no de restaurantes, y su ficha no indica de dónde proceden; no se puede descartar que haya visto reseñas parecidas.

## 5. Decisión y uso en el producto

**Solución elegida (provisional): alerta en dos niveles.**

| Nivel | Condición | En el reservado |
|---|---|---|
| **Alta** | Valoración ≤ 3 estrellas (con o sin texto) | 10 alertas, 9 críticas reales |
| **Revisar** | Valoración ≥ 4 y el modelo detecta una queja en el texto | 5 alertas, 1 crítica real |
| **Ninguna** | El resto | |

- **Por qué:** es la combinación C presentada de forma que el coste del texto sea pequeño. El propietario atiende primero el nivel *alta*, que es fiable (9 de 10), y ojea el nivel *revisar* (5 reseñas de 97) como una lista secundaria. Así se recupera parte de lo que las estrellas no ven sin inundarle de avisos.
- **Qué mejora ofrece:** las estrellas solas ya detectan 9 de 11 críticas. La mejora del texto es pequeña y **no está demostrada**: se mantiene porque su coste es bajo y porque el texto es imprescindible para otra cosa, **rellenar las plantillas de respuesta** (qué se critica), algo que las estrellas no pueden hacer.
- **¿Es suficiente para el MVP?** Sí, como sistema de ayuda con una persona al mando. El MVP no depende de que el modelo supere a las estrellas.

**Salida que consume el frontal:** tabla `gold_predictions`, que se une a `gold_reviews` por `review_id`.

| Columna | Significado |
|---|---|
| `review_id` | Clave que une con `gold_reviews` |
| `stars_alert` | 1 si la valoración es ≤ 3 |
| `text_score` | Probabilidad (0-1) de que el modelo asigne ≤ 3 estrellas. Vacía si la reseña no tiene texto |
| `text_alert` | 1 si `text_score` ≥ 0,5 |
| `alert_level` | `alta`, `revisar` o `ninguna` |
| `model_version` | Modelo usado |

**Cautelas:**
- Es una **alerta, no una decisión**: ninguna respuesta se publica sin revisión humana.
- Una reseña sin alerta no garantiza que sea positiva. El modelo falla con ironía, quejas largas y razonadas y quejas dentro de elogios.
- `text_score` **no es una probabilidad calibrada**: sirve para ordenar, no para medir una probabilidad real.
- El nivel *revisar* tiene baja precisión (1 de 5): está pensado para ojearse, no para actuar sin leer.
- Las conclusiones salen de un solo restaurante y 11 críticas, y deben validarse con más datos.

## Reproducibilidad

1. Gold y conjunto reservado: `python src/pipeline.py` (entrega 2).
2. Etiquetas del reservado: `data/holdout_labels.csv` (solo identificadores y etiqueta, sin texto).
3. Evaluación: ejecutar `notebooks/03_evaluacion.ipynb` (en Colab). Genera `holdout_resultados.csv` y `resultados_comparacion.csv` (sin texto, guardados en `results/`) y un fichero privado con los casos a leer, que no se sube.
4. Salida para el producto: `python src/score_reviews.py` escribe `gold_predictions`.
