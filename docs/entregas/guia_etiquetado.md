# Guía de etiquetado: ¿esta reseña requiere atención?

**Versión 1.** Se fija **antes** de etiquetar el conjunto reservado y no se modifica después.
Todos los ejemplos de esta guía son **inventados**.

## Para qué sirve

El producto debe decidir, para cada reseña, si basta una respuesta tipo (plantillas 1 y 2) o si una persona
debe leerla y contestar personalmente (plantilla 3). Esta guía define qué significa "requiere atención" con un
criterio basado **solo en el texto**, para poder comprobar si leer el texto aporta algo frente a usar solo las
estrellas.

## La pregunta

> Si yo fuera el dueño, ¿querría leer esta reseña personalmente antes de contestar?

## Las tres etiquetas

| Etiqueta | Cuándo |
|---|---|
| **SI** (requiere atención) | El cliente describe un **problema o una mala experiencia concreta**; expresa decepción o dice que no volverá o no lo recomienda; acusa de algo grave (higiene, trato, alergias, cobro); se queja con ironía; o es una reseña **mixta** donde el reparo pesa de verdad. |
| **NO** (basta una plantilla) | Elogio; comentario neutro o sin contenido; o un **reparo pasajero** dentro de una reseña claramente satisfecha. |
| **DUDA** | No se decide tras leerla dos veces. Se resuelve después; no se le dan vueltas. |

## Ejemplos (inventados)

| Texto | Etiqueta | Por qué |
|---|---|---|
| "Comida casera y trato excelente. Repetiremos." | NO | Elogio |
| "Todo muy rico, aunque los postres un poco caros." | NO | Reparo pasajero en una reseña satisfecha |
| "Buena comida pero algo de ruido." | NO | Reparo leve, sin decepción |
| "Bien." | NO | Sin contenido de queja |
| "Esperamos 50 minutos para el primer plato y nadie nos dio explicaciones." | SI | Problema concreto |
| "El sitio es bonito, pero la carne llegó fría y la camarera fue seca con nosotros. No sé si volveremos." | SI | Reseña mixta con reparo importante y duda de volver |
| "Qué maravilla de servicio… otra hora esperando, por supuesto." | SI | Queja con ironía |
| "Mi hijo es alérgico y los platos no estaban bien indicados; pasamos un mal rato." | SI | Tema de salud |
| "Un robo." | SI | Corta, pero es una queja clara: la longitud no importa |
| "Ha cambiado mucho desde la última vez." | DUDA | Puede ser nostalgia o queja; el texto no lo aclara |

## Reglas del procedimiento

1. **Mira solo el texto.** Las estrellas están ocultas y no se buscan.
2. **No mires resultados de ningún modelo** ni comparaciones antes de terminar.
3. **No busques la reseña en Google** ni el contexto del cliente.
4. **No cambies etiquetas ya puestas** al ver otras reseñas. Si dudas, usa DUDA.
5. **La longitud, el tono educado o el número de signos de exclamación no deciden:** decide el contenido.
6. **Se etiqueta en una o dos sesiones**, sin prisas pero sin releer en exceso.

## Después de etiquetar

- Se cuentan SI, NO y DUDA. Las **DUDA** se resuelven con una segunda persona; si siguen sin resolverse, se
  excluyen de las métricas y se indica cuántas fueron.
- Opcionalmente, una segunda persona etiqueta una parte del conjunto para medir **cuánto coinciden**.
- Las etiquetas (solo `review_id` y SI/NO/DUDA, sin texto) pueden publicarse en el repositorio.
