"""
Pipeline Bronze -> Silver -> Gold de reseñas de Google Business Profile
(exportación Google Takeout del Cortijo Vistalegre).

Uso (desde la raíz del repo):
    python src/pipeline.py          # ejecución real: lee data/bronze/ y genera data/reviews.db
    python src/pipeline.py --demo   # demostración con reseñas INVENTADAS (data/sample/bronze_demo/)

Entrada : data/bronze/*.json        (inmutable, NO se sube al repo: contiene nombres)
Salida  : data/reviews.db            (SQLite con tablas silver_reviews, gold_reviews y holdout_reviews)
          data/sample/holdout_ids.csv      (solo ids hash del conjunto reservado; no contiene texto)
Demo    : entrada data/sample/bronze_demo/*.json -> salida data/sample/demo_silver.csv y demo_gold.csv
          (reseñas inventadas: así se enseña el proceso en GitHub sin publicar texto real)
"""
import argparse
import glob
import hashlib
import json
import sqlite3
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # resultados reproducibles

ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze"
SAMPLE = ROOT / "data" / "sample"
DEMO_BRONZE = SAMPLE / "bronze_demo"
DB = ROOT / "data" / "reviews.db"

# Conjunto reservado para la comprobación final (se fija aquí, antes de modelar)
HOLDOUT_FRAC = 0.25
HOLDOUT_SEED = 42
CRITICAL_MAX_RATING = 3  # solo para ESTRATIFICAR la reserva (no es una variable de entrada)

STARS = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
TRANSLATED = "(Translated by Google)"
ORIGINAL = "(Original)"


# --------------------------------------------------------------------------
# BRONZE: leer los JSON tal cual llegan (no se modifican)
# --------------------------------------------------------------------------
def read_bronze(directory: Path = BRONZE) -> list[dict]:
    reviews = []
    for path in sorted(glob.glob(str(directory / "*.json"))):
        with open(path, encoding="utf-8") as f:
            reviews.extend(json.load(f)["reviews"])
    return reviews


# --------------------------------------------------------------------------
# SILVER: tipos, duplicados, texto original vs traducción, sin datos personales
# --------------------------------------------------------------------------
def split_comment(comment: str | None) -> tuple[str | None, str | None]:
    """Separa el texto original de la traducción automática que añade Google.

    Formatos vistos en el export:
      A) "<original>\\n\\n(Translated by Google)\\n<traducción>"
      B) "(Translated by Google)\\n<traducción>\\n\\n(Original)\\n<original>"
      C) "<original>" (sin marcador)
    """
    if not comment or not comment.strip():
        return None, None
    c = comment.strip()
    if c.startswith(TRANSLATED) and ORIGINAL in c:  # formato B
        head, original = c.split(ORIGINAL, 1)
        return original.strip(), head.replace(TRANSLATED, "").strip()
    if TRANSLATED in c:  # formato A
        original, translation = c.split(TRANSLATED, 1)
        return original.strip(), translation.strip()
    return c, None  # formato C


def anon_id(name: str) -> str:
    """Id anónimo y estable derivado del id interno de Google."""
    return hashlib.sha256(name.encode()).hexdigest()[:16]


def build_silver(raw: list[dict]) -> pd.DataFrame:
    rows = []
    for r in raw:
        original, translation = split_comment(r.get("comment"))
        reply = r.get("reviewReply") or {}
        rows.append(
            {
                "review_id": anon_id(r["name"]),  # se descarta displayName a propósito
                "rating": STARS[r["starRating"]],
                "created_at": r["createTime"],
                "updated_at": r["updateTime"],
                "text_original": original,
                "text_translation": translation,
                "reply_text": (reply.get("comment") or "").strip() or None,
                "reply_time": reply.get("updateTime"),
            }
        )
    # Takeout mezcla fechas con y sin fracciones de segundo -> ISO8601 flexible
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset="review_id")  # por si el export repite reseñas
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, format="ISO8601")
    df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True, format="ISO8601")
    df["reply_time"] = pd.to_datetime(df["reply_time"], utc=True, format="ISO8601")
    df["was_edited"] = df["updated_at"] != df["created_at"]
    return df.sort_values("created_at").reset_index(drop=True)


# --------------------------------------------------------------------------
# GOLD: una fila por reseña, lista para consumir (sin nada específico de modelo)
# --------------------------------------------------------------------------
def safe_detect(text: str | None) -> str | None:
    if not isinstance(text, str) or len(text) < 20:  # NaN o muy corto: poco fiable
        return None
    try:
        return detect(text)
    except Exception:
        return None


def build_gold(silver: pd.DataFrame) -> pd.DataFrame:
    g = pd.DataFrame(
        {
            "review_id": silver["review_id"],
            "created_at": silver["created_at"].dt.strftime("%Y-%m-%d"),
            "year": silver["created_at"].dt.year,
            "rating": silver["rating"],
            "text": silver["text_original"],
            "has_text": silver["text_original"].notna(),
            "n_chars": silver["text_original"].fillna("").str.len(),
            "lang": silver["text_original"].map(safe_detect),
            "has_reply": silver["reply_text"].notna(),
            "reply_text": silver["reply_text"],
        }
    )
    return g


# --------------------------------------------------------------------------
# HOLD-OUT: reserva fija de reseñas con texto, con críticas garantizadas.
# Es una tabla APARTE (no una columna de Gold): Gold no depende de decisiones de modelado
# y los splits de validación cruzada de cada experimento siguen siendo libres.
# --------------------------------------------------------------------------
def build_holdout(gold: pd.DataFrame) -> pd.DataFrame:
    t = gold[gold["has_text"]].sort_values("review_id").copy()
    t["stratum"] = (t["rating"] <= CRITICAL_MAX_RATING).map({True: "critica", False: "resto"})
    hold = t.groupby("stratum", group_keys=False).sample(frac=HOLDOUT_FRAC, random_state=HOLDOUT_SEED)
    return hold[["review_id", "stratum"]].sort_values("review_id").reset_index(drop=True)


def run_demo() -> None:
    """Mismo proceso con reseñas inventadas: sin base de datos y sin texto real."""
    raw = read_bronze(DEMO_BRONZE)
    silver = build_silver(raw)
    gold = build_gold(silver)
    silver.to_csv(SAMPLE / "demo_silver.csv", index=False)
    gold.to_csv(SAMPLE / "demo_gold.csv", index=False)
    print(f"DEMO | Bronze: {len(raw)} reseñas (inventadas) -> Silver: {len(silver)} -> Gold: {len(gold)}")
    print("Salida: data/sample/demo_silver.csv y data/sample/demo_gold.csv")


def main() -> None:
    raw = read_bronze()
    silver = build_silver(raw)
    gold = build_gold(silver)

    with sqlite3.connect(DB) as con:
        silver.assign(
            created_at=silver["created_at"].astype(str),
            updated_at=silver["updated_at"].astype(str),
            reply_time=silver["reply_time"].astype(str),
        ).to_sql("silver_reviews", con, if_exists="replace", index=False)
        gold.to_sql("gold_reviews", con, if_exists="replace", index=False)
        holdout = build_holdout(gold)
        holdout.to_sql("holdout_reviews", con, if_exists="replace", index=False)

    SAMPLE.mkdir(parents=True, exist_ok=True)
    holdout.to_csv(SAMPLE / "holdout_ids.csv", index=False)  # solo ids hash, sin texto

    print(f"Bronze: {len(raw)} reseñas en {len(glob.glob(str(BRONZE / '*.json')))} ficheros")
    print(f"Silver: {len(silver)} filas | Gold: {len(gold)} filas -> {DB.name}")
    print(f"Hold-out: {len(holdout)} reseñas reservadas ({(holdout.stratum == 'critica').sum()} críticas)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline Bronze -> Silver -> Gold")
    parser.add_argument("--demo", action="store_true", help="usar las reseñas inventadas de data/sample/bronze_demo/")
    args = parser.parse_args()
    run_demo() if args.demo else main()
