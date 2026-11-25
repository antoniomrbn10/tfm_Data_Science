"""
Calcula la alerta de cada reseña y escribe la tabla `gold_predictions` (entrega 3).

Lógica (ver docs/entregas/03_machine_learning.md, apartado 5):
  - stars_alert : 1 si la valoración es <= STARS_MAX (3).
  - text_score  : probabilidad de que un modelo preentrenado asigne <= 3 estrellas al TEXTO
                  (sin reentrenar). Vacía si la reseña no tiene texto.
  - text_alert  : 1 si text_score >= TEXT_THRESHOLD (0,5; umbral por defecto, no ajustado).
  - alert_level : 'alta'    si stars_alert
                  'revisar' si no hay stars_alert pero sí text_alert
                  'ninguna' en el resto

Uso (desde la raíz del repo, con data/reviews.db generado por src/pipeline.py):
    python src/score_reviews.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "reviews.db"

PRE_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
STARS_MAX = 3          # alerta por estrellas si rating <= 3
MODEL_MAX_STARS = 3    # el modelo puntúa P(<= 3 estrellas)
TEXT_THRESHOLD = 0.5   # umbral por defecto del modelo (fijado en docs/protocolo_evaluacion.md)


def hf_scorer():
    """Devuelve una función texts -> scores (probabilidad de <= MODEL_MAX_STARS estrellas)."""
    from transformers import pipeline  # import tardío: solo hace falta al puntuar

    clf = pipeline("text-classification", model=PRE_MODEL, top_k=None, truncation=True, max_length=256)

    def score(texts: list[str]) -> np.ndarray:
        out = clf(list(texts), batch_size=16)
        # etiquetas '1 star' ... '5 stars'
        return np.array([sum(o["score"] for o in r if int(o["label"][0]) <= MODEL_MAX_STARS) for r in out])

    return score


def build_predictions(gold: pd.DataFrame, scorer) -> pd.DataFrame:
    out = pd.DataFrame({"review_id": gold["review_id"]})
    out["stars_alert"] = (gold["rating"] <= STARS_MAX).astype(int)

    out["text_score"] = np.nan
    has_text = gold["has_text"] == 1
    if has_text.any():
        out.loc[has_text, "text_score"] = np.round(scorer(gold.loc[has_text, "text"].tolist()), 4)

    out["text_alert"] = (out["text_score"] >= TEXT_THRESHOLD).astype(int)  # NaN -> 0 (sin texto, sin aviso de texto)
    out["alert_level"] = np.where(out["stars_alert"] == 1, "alta",
                          np.where(out["text_alert"] == 1, "revisar", "ninguna"))
    out["model_version"] = PRE_MODEL
    return out


def main(scorer=None) -> pd.DataFrame:
    scorer = scorer or hf_scorer()
    with sqlite3.connect(DB) as con:
        gold = pd.read_sql("SELECT review_id, rating, has_text, text FROM gold_reviews", con)
        out = build_predictions(gold, scorer)
        out.to_sql("gold_predictions", con, if_exists="replace", index=False)

    print(f"{len(out)} reseñas | {int((out.text_score.notna()).sum())} con texto puntuado")
    print(out.alert_level.value_counts().to_dict())
    return out


if __name__ == "__main__":
    main()
