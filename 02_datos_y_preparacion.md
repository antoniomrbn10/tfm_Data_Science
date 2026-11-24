# Entrega 02 · Datos y preparación

**Producto:** Reseñas AI, un agente que clasifica las reseñas de clientes, propone respuestas a las rutinarias y **escala a una persona las críticas**.
**Datos:** reseñas reales de Google Maps del restaurante Cortijo Vistalegre (Cazalla de la Sierra), propiedad de la familia del autor, con su autorización.

## 1. Qué datos necesita el producto

**Observación:** una reseña de un cliente en Google Maps.

| Tipo | Datos |
|---|---|
| Imprescindibles | texto de la reseña, valoración (1-5 estrellas), fecha |
| Deseables | idioma; ejemplos de respuestas del propietario (para el tono de los borradores) |
| No necesarios | nombre o perfil del autor |

**Granularidad e histórico:** una fila por reseña, con histórico completo desde 2011. El volumen alcanzó su máximo en 2019-2021 (127-155 reseñas al año) y baja desde 2022 (29 en 2025), algo que condiciona cómo se evalúa con el tiempo.

**Qué datos hacen falta para cada función del producto:**

| Función | Datos | Disponibilidad |
|---|---|---|
| Detectar reseñas que requieren atención | Texto y estrellas de las reseñas | Sí: 855 reseñas, 438 con texto |
| Proponer respuestas | Ejemplos de respuestas del propietario | **No hay corpus suficiente**: solo 2 respuestas reales. Se usarán unas pocas plantillas acordadas con la familia (ver apartado 2) |

## 2. Fuentes reales y viabilidad

- **Fuente principal:** exportación de Google Takeout (Google Business Profile) de la ficha del restaurante. 43 ficheros JSON con **855 reseñas**, que coinciden con las 855 valoraciones de la ficha. Descarga del 10/11/2026.
- **Cómo se accede:** Takeout → Business Profile → reseñas, con la cuenta que administra la ficha. Es repetible con los mismos pasos.
- **API oficial:** se solicitó acceso a la Business Profile API y Google no la aprobó por no cumplir sus criterios para solicitantes. Sería el mecanismo de producción para actualizar los datos de forma automática.
- **Cobertura y estabilidad:** la exportación es una foto fija, suficiente para un MVP. Los ficheros son estables mientras Google mantenga Takeout.
- **Si la fuente dejara de estar disponible:** se repetiría la exportación o se solicitaría de nuevo la API.

### Plan de trabajo acordado con el tutor

Tras plantear al tutor si convenía añadir un dataset público de reseñas, el plan acordado es **empezar solo con los datos del restaurante y añadir fuentes solo si hace falta**:

| Fase | Qué se hace | Decisión |
|---|---|---|
| **1. Solo el restaurante** | Un clasificador ya entrenado marca las reseñas que debe revisar una persona. Se revisan a mano los casos en que falla. Se reserva desde el principio un conjunto con ejemplos críticos para la comprobación final | Es el punto de partida: no se retrasa el proyecto buscando otro conjunto de datos |
| **2. Dataset público (condicional)** | Solo si la fase 1 se queda corta: se añaden reseñas públicas como apoyo (con su propio Bronze/Silver/Gold, licencia y limitaciones documentadas) y se compara si mejora **al probarlo en el restaurante** | Criterio orientativo para considerar suficiente la fase 1: detectar al menos ~3 de cada 4 críticas del conjunto reservado, con una carga de alertas asumible para el propietario |
| **3. Respuestas** | Con solo 2 respuestas reales del propietario, el agente preparará **borradores a partir de unas pocas plantillas acordadas con la familia**, que una persona revisa antes de publicar | Plantillas **validadas con los propietarios** (22/11/2026): trato de usted, firma del equipo y contacto acordados. En `data/plantillas_respuesta.md` |

Si se llegara a la fase 2, el test seguiría haciéndose siempre con reseñas del restaurante.

## 3. Uso, privacidad y datos personales

- **Uso autorizado:** los datos pertenecen a la ficha de un negocio cuyos propietarios han dado su autorización. No se comparten ni se redistribuyen.
- **Dato personal:** el export incluye el nombre público de cada autor. No aporta valor al producto, así que **se elimina en la capa Silver** y nunca llega a Gold ni a la base de datos. El identificador interno de Google se sustituye por un hash (`review_id`).
- **Texto libre:** algunas reseñas mencionan nombres propios (clientes o personal). No se usan como variable y no se publican en el repositorio.
- **Plantillas de respuesta:** no contienen datos de clientes; usan campos variables que rellena el agente a partir de la propia reseña y que revisa una persona.
- **Repositorio:** `data/bronze/` y `data/reviews.db` están en `.gitignore`. Solo se sube una muestra de 20 reseñas con los nombres sustituidos (`data/sample/bronze_sample.json`), una muestra de Gold y los identificadores del conjunto reservado.

## 4. Del dato bruto al dato utilizable

Código: [`src/pipeline.py`](../../src/pipeline.py). Se ejecuta con `python src/pipeline.py` y genera `data/reviews.db` (SQLite).

| Capa | Contenido | Transformaciones |
|---|---|---|
| **Bronze** | 43 JSON de Takeout tal cual, inmutables (`data/bronze/`). Muestra anonimizada en `data/sample/` | Ninguna |
| **Silver** (`silver_reviews`) | 855 filas | Estrellas de texto a entero (`FIVE` → 5). Fechas a `datetime` UTC (el export mezcla formatos con y sin fracciones de segundo). Deduplicación por id (0 duplicados). **Separación del texto original y la traducción automática** que Google añade al comentario (3 formatos distintos). Eliminación de `displayName`. Respuesta del propietario en columnas propias |
| **Gold** (`gold_reviews`) | 855 filas, una por reseña | Selección de columnas finales, año, longitud, idioma detectado y banderas `has_text` y `has_reply` |
| **Reserva** (`holdout_reviews`) | 109 reseñas con texto (12 críticas) | Muestra estratificada del 25% con semilla fija (ver abajo) |

**Columnas de Gold:** `review_id`, `created_at`, `year`, `rating`, `text`, `has_text`, `n_chars`, `lang`, `has_reply`, `reply_text`.

**Uso del Gold:** entrada de la entrega 3 (clasificación de las reseñas que requieren atención humana). Gold no contiene etiquetas, splits ni transformaciones específicas de un modelo: eso se hace en la fase de ML.

**Columnas que NO pueden ser variables de entrada del modelo:** `has_reply` y `reply_text` solo existen después de que el restaurante conteste, y no estarán disponibles cuando llegue una reseña nueva (leakage). Se conservan únicamente para estudiar el tono de las respuestas. `rating` tampoco puede usarse como entrada si la etiqueta se deriva de las estrellas.

### Conjunto reservado para la comprobación final

El tutor recomendó guardar desde el principio una parte de las reseñas, con ejemplos críticos, para comprobar el resultado al final.

- **Qué es:** 109 reseñas con texto, el **25% de cada grupo** (críticas ≤ 3★ y resto), elegidas con semilla fija (42). Contiene **12 críticas** y 97 reseñas restantes, repartidas por todos los años.
- **Por qué es una tabla aparte y no una columna de Gold:** Gold no debe depender de decisiones de modelado, y los splits de validación de cada experimento deben poder variar. La reserva, en cambio, es un conjunto de comprobación final deliberadamente fijo.
- **Es reproducible:** `holdout_reviews` se regenera idéntica al ejecutar el pipeline, y sus identificadores están en `data/sample/holdout_ids.csv`.
- **Para qué sirve:** la comprobación final se hará **etiquetando a mano estas reseñas, a ciegas** (sin ver estrellas ni puntuación del modelo), para comparar el modelo con las estrellas con un criterio independiente.
- **Limitación:** con solo 12 críticas, las métricas sobre este conjunto serán orientativas.

### Resumen de los datos (EDA)

| | |
|---|---|
| Reseñas totales | 855 (2011-2026) |
| Con texto | 438 (51%) |
| Estrellas, todas | 5★ 570 · 4★ 189 · 3★ 38 · 1★ 36 · 2★ 22 |
| Estrellas, con texto | 5★ 311 · 4★ 78 · 3★ 14 · 2★ 15 · 1★ 20 |
| Con respuesta del propietario | 2 |
| Idioma (con texto) | ~91% español, con otros idiomas marginales y 25 textos demasiado cortos para detectar |
| Longitud (con texto) | mediana 93 caracteres; las críticas son más largas (mediana 290) que las positivas (86) |

## 5. Riesgos y limitaciones

- **Pocas críticas con texto:** solo **35 reseñas negativas (1-2★) con texto** y 14 neutras, frente a 389 positivas. Es el caso que más importa al producto (escalar a una persona) y el menos representado. Las métricas sobre esta clase serán inestables, y por eso la validación usará repeticiones y se acompaña de revisión manual de errores.
- **Pocas respuestas reales:** solo 2 reseñas tienen respuesta, así que no hay un corpus con el que entrenar o evaluar respuestas automáticas. Se mitiga con plantillas acordadas con la familia y revisión humana antes de publicar.
- **Un solo negocio:** restaurante rural y turístico, con alguna reseña sobre eventos nocturnos. Los resultados no se generalizan sin más a otros negocios.
- **Estrellas no son sentimiento:** el 49% de las reseñas no tiene texto, y una valoración puede no coincidir con lo que dice el comentario. De ahí la revisión manual del conjunto reservado.
- **Riesgos de data leakage a controlar en la entrega 3:** (1) usar las estrellas como entrada si la etiqueta se deriva de ellas; (2) usar variables posteriores a la reseña (`has_reply`, `reply_text`); (3) ajustar TF-IDF o escalado con todos los datos antes de separar train y test; (4) un split aleatorio que mezcle pasado y futuro, por la deriva temporal; (5) posible contaminación si se usa un modelo preentrenado que haya visto reseñas de Google durante su entrenamiento.
- **Deriva temporal:** el volumen baja desde 2022, y en 2024-2026 hay solo 57 reseñas con texto.
- **Idioma:** la detección falla con textos muy cortos, y la traducción de Google se elimina porque no es un dato del cliente.
- **Si la fuente dejara de estar disponible:** se repetiría la exportación o se solicitaría de nuevo la API. Si los datos propios se quedaran cortos, se aplicaría la fase 2 del plan (dataset público como apoyo), siempre con prueba en el restaurante.
