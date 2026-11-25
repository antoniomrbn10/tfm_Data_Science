# Protocolo de evaluación (entrega 3)

**Fijado antes de evaluar ningún modelo sobre las etiquetas humanas.** No se modifica después de ver resultados.

## Datos

| Conjunto | Reseñas con texto | Uso |
|---|---|---|
| **Reservado (hold-out)** | 109 | Examen final. Etiquetado a mano **a ciegas** con la [guía](guia_etiquetado.md): **11 SI, 96 NO y 2 excluidas** (107 evaluables) |
| **Desarrollo** | 329 | Comprobar que el modelo funciona y leer errores. **No se ajusta nada con él para ganar en el hold-out** |

## Sistemas que se comparan (definidos de antemano, sin parámetros libres)

| Sistema | Regla |
|---|---|
| **B1 · Estrellas ≤ 2** | Alerta si la valoración es 1 o 2 estrellas |
| **B2 · Estrellas ≤ 3** | Alerta si la valoración es 1, 2 o 3 estrellas |
| **M · Modelo sobre el texto** | Modelo preentrenado multilingüe (`nlptown/bert-base-multilingual-uncased-sentiment`); alerta si la probabilidad de ≤ 3 estrellas es ≥ **0,5** (umbral por defecto, no ajustado) |
| **C · Combinación** | Alerta si estrellas ≤ 3 **o** M alerta |

Se informan **B1 y B2 las dos**, sin elegir la mejor después.

## Evaluación

- **Una sola vez** sobre el hold-out, con las etiquetas humanas SI/NO.
- **Las 2 reseñas excluidas** (marcadas DUDA y descartadas por no aportar contenido) quedan fuera de las métricas y se informa de ello. Se repite el cálculo tratándolas como SI y como NO para ver si cambia la conclusión (análisis de sensibilidad).
- **Métricas:** precision y recall de la clase "requiere atención", siempre junto a los **recuentos absolutos** (aciertos, falsas alarmas y críticas no detectadas) y un intervalo de confianza (Wilson).
- **Análisis de errores:** lectura a mano de todos los casos en que el sistema y el criterio humano discrepan.

## Limitaciones declaradas de antemano

- Solo hay **11 reseñas SI** en el hold-out: una sola reseña de diferencia mueve el recall unos 9 puntos. Las comparaciones serán **orientativas**, no concluyentes.
- **Las dos reglas de estrellas ya se habían cruzado con las etiquetas** en un recuento previo. No tienen parámetros libres, así que no hay ajuste, pero se declara.
- **Las 2 reseñas excluidas tienen 1-2 estrellas**, es decir, son casos en los que las reglas de estrellas alertan. Excluirlas favorece ligeramente a esas reglas (de haberse etiquetado NO, serían falsas alarmas); el análisis de sensibilidad lo cuantifica.
- Un solo negocio y un solo etiquetador (salvo que una segunda persona etiquete parte del conjunto).
- El modelo M puede haber visto reseñas parecidas durante su entrenamiento.

## Enmienda previa a la evaluación del modelo

Tras el etiquetado inicial (10 SI, 96 NO, 3 DUDA), las dudas se resolvieron así: una (4★, 2024) pasa a **SI** y las otras dos se **excluyen**.
La resolución se hizo **antes de calcular ningún resultado del modelo**, pero **después de conocer los recuentos de las reglas de estrellas**, y la reseña que pasa a SI tiene 4 estrellas (es un caso que las estrellas no detectan). Se declara por transparencia.
Las etiquetas definitivas están en `data/holdout_labels.csv` (`SI`, `NO` o `EXCLUIDA`; sin texto).
