# Entrega 02 · Datos y preparación

**Producto:** Reseñas AI, un agente que clasifica reseñas de clientes, responde a las rutinarias y escala a una persona las críticas.
**Datos:** reseñas reales de Google Maps del restaurante Cortijo Vistalegre (Cazalla de la Sierra), propiedad de la familia del autor.

## 1. Qué datos necesita el producto

**Observación:** una reseña de un cliente en Google Maps.

| Tipo | Campos |
|---|---|
| Imprescindibles | texto de la reseña, valoración (1-5 estrellas), fecha |
| Deseables | respuesta del propietario (para aprender el tono de las respuestas), idioma |
| No necesarios | nombre o perfil del autor |

**Granularidad e histórico:** una fila por reseña, con histórico completo desde 2011. El volumen anual alcanzó su máximo en 2019-2021 (127-155 reseñas/año) y baja desde 2022 (29 en 2025). Hay que tenerlo en cuenta al decidir el split temporal.

## 2. Fuentes reales y viabilidad

- **Fuente principal:** exportación de Google Takeout (Google Business Profile) de la ficha del restaurante, con autorización de los propietarios. 43 ficheros JSON con 855 reseñas, que coinciden con las 855 valoraciones que muestra la ficha. Descarga del 10/11/2026.
- **Cómo se accede:** Takeout → Business Profile → reseñas, con la cuenta que administra la ficha. Es repetible siguiendo los mismos pasos.
- **API oficial:** se solicitó acceso a la Business Profile API y Google lo rechazó por no cumplir sus criterios para solicitantes. Sería el mecanismo de producción.
- **Cobertura y estabilidad:** la exportación es una foto fija sin actualización automática, suficiente para un MVP. Los ficheros son estables mientras Google mantenga Takeout.
- **Alternativa si la fuente fallara:** repetir el export cuando se necesite o, como apoyo de entrenamiento, un dataset público de reseñas con licencia clara (por ejemplo Yelp Open Dataset), siempre declarado como complementario. El test se haría siempre con reseñas del Cortijo.

## 3. Uso, privacidad y datos personales

- **Uso autorizado:** los datos pertenecen a la ficha de un negocio cuyos propietarios han dado su autorización. No se comparten ni se redistribuyen.
- **Dato personal:** el export incluye el nombre público de cada autor. No aporta valor al producto, así que **se elimina en la capa Silver** y nunca llega a Gold ni a la base de datos. El identificador interno de Google se sustituye por un hash (`review_id`).
- **Texto libre:** algunas reseñas mencionan nombres propios (clientes o personal). No se usan como variable y no se publican en el repositorio.
- **Repositorio:** `data/bronze/` está en `.gitignore`. Solo se sube una muestra de 20 reseñas con los nombres sustituidos (`data/sample/bronze_sample.json`) y una muestra de Gold.

## 4. Del dato bruto al dato utilizable

Código: [`src/pipeline.py`](../../src/pipeline.py). Se ejecuta con `python src/pipeline.py` y genera `data/reviews.db` (SQLite).

| Capa | Contenido | Transformaciones |
|---|---|---|
| **Bronze** | 43 JSON de Takeout tal cual, inmutables (`data/bronze/`). Muestra anonimizada en `data/sample/` | Ninguna |
| **Silver** (`silver_reviews`) | 855 filas | Estrellas de texto a entero (`FIVE` → 5). Fechas a `datetime` UTC (el export mezcla formatos con y sin fracciones de segundo). Deduplicación por id (0 duplicados). **Separación del texto original y la traducción automática** que Google añade al comentario (3 formatos distintos). Eliminación de `displayName`. Respuesta del propietario en columnas propias |
| **Gold** (`gold_reviews`) | 855 filas, una por reseña | Selección de columnas finales, año, longitud, idioma detectado y banderas `has_text` y `has_reply` |

**Columnas de Gold:** `review_id`, `created_at`, `year`, `rating`, `text`, `has_text`, `n_chars`, `lang`, `has_reply`, `reply_text`.

**Columnas que NO pueden ser variables de entrada del modelo:** `has_reply` y `reply_text` solo existen después de que el restaurante conteste, y no estarán disponibles cuando llegue una reseña nueva (leakage). Se conservan en Gold únicamente para estudiar el tono de las respuestas. `rating` tampoco puede usarse como entrada si la etiqueta se deriva de las estrellas.

**Uso:** es la entrada de la entrega 3 (clasificación de sentimiento y detección de reseñas que requieren atención humana). Gold no contiene etiquetas, splits ni transformaciones específicas de un modelo: eso se hace en la fase de ML.

**Resumen del dato (EDA):**

| | |
|---|---|
| Reseñas totales | 855 (2011-2026) |
| Con texto | 438 (51%) |
| Estrellas, todas | 5★ 570 · 4★ 189 · 3★ 38 · 1★ 36 · 2★ 22 |
| Estrellas, con texto | 5★ 311 · 4★ 78 · 3★ 14 · 2★ 15 · 1★ 20 |
| Con respuesta del propietario | 2 |
| Idioma (con texto) | ~91% español, con otros idiomas marginales y 25 textos demasiado cortos para detectar |
| Longitud (con texto) | mediana 93 caracteres; las negativas son más largas (mediana 290) que las positivas (86) |

## 5. Riesgos y limitaciones

- **Pocas críticas con texto:** solo hay **35 reseñas negativas (1-2★) con texto** y 14 neutras, frente a 389 positivas. Es el caso que más importa al producto (escalar a una persona) y el menos representado. Las métricas sobre esta clase serán inestables.
- **Pocas respuestas reales:** solo 2 reseñas tienen respuesta, así que no hay un corpus real de respuestas con el que evaluar o guiar la parte generativa.
- **Un solo negocio:** restaurante rural y turístico, con alguna reseña sobre eventos nocturnos. Los resultados no se generalizan sin más a otros negocios.
- **Estrellas no son sentimiento:** el 49% de las reseñas no tiene texto, y una valoración puede no coincidir con lo que dice el comentario.
- **Riesgos de data leakage a controlar en la entrega 3:** (1) usar las estrellas como entrada si la etiqueta se deriva de ellas; (2) usar variables posteriores a la reseña (`has_reply`, `reply_text`); (3) ajustar TF-IDF o escalado con todos los datos antes de separar train y test; (4) un split aleatorio que mezcle pasado y futuro, por la deriva temporal; (5) posible contaminación si se usa un modelo preentrenado que haya visto reseñas de Google durante su entrenamiento.
- **Deriva temporal:** el volumen baja desde 2022, y en 2024-2026 hay solo 57 reseñas con texto. Eso condiciona un split por fecha.
- **Idioma:** la detección falla con textos muy cortos, y la traducción de Google se elimina porque no es un dato del cliente.
- **Si la fuente dejara de estar disponible:** se repetiría la exportación o se solicitaría de nuevo la API. Como apoyo de entrenamiento se usaría un dataset público, siempre con test en reseñas del Cortijo.
