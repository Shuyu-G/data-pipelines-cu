"""
Lecture 6 mid-semester assignment DAG.

Builds a weekly ETL + ML pipeline that:
1. Downloads gold prices from 2024-01-01 to today
2. Fetches date-aligned war-related historical news
3. Computes sentiment and training features
4. Trains a classifier to predict next-day gold price direction
5. Saves submission-ready sample files
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from airflow import DAG

try:
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    try:
        from airflow.operators.python import PythonOperator
    except ImportError:
        from airflow.operators.python_operator import PythonOperator


ASSIGNMENT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.getenv("GOLD_WAR_OUTPUT_DIR", ASSIGNMENT_DIR / "artifacts"))
MODEL_PATH = ASSIGNMENT_DIR / "gold_model.pkl"
GOLD_CSV = OUTPUT_DIR / "gold_prices.csv"
NEWS_CSV = OUTPUT_DIR / "war_news.csv"
TRAINING_CSV = OUTPUT_DIR / "training_data.csv"
GOLD_SAMPLE_CSV = ASSIGNMENT_DIR / "gold_prices_sample.csv"
NEWS_SAMPLE_CSV = ASSIGNMENT_DIR / "war_news_sample.csv"
TRAINING_SAMPLE_CSV = ASSIGNMENT_DIR / "training_data_sample.csv"

NEWS_START_DATE = "2024-01-01"
GUARDIAN_API_URL = "https://content.guardianapis.com/search"
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY", "test")
GUARDIAN_SECTION = "world"
GUARDIAN_PAGE_SIZE = 200
WAR_KEYWORDS = [
    "war",
    "conflict",
    "attack",
    "military",
    "invasion",
    "strike",
    "battle",
    "missile",
    "troops",
    "ceasefire",
]


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _write_sample(dataframe, path: Path, rows: int = 20) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.head(rows).to_csv(path, index=False)


def _fetch_gold_prices(**_context):
    import pandas as pd

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("pip install yfinance") from exc

    end_date = datetime.now().strftime("%Y-%m-%d")
    gold = yf.download(
        "GC=F",
        start=NEWS_START_DATE,
        end=end_date,
        progress=False,
        auto_adjust=True,
    )

    if gold.empty:
        raise ValueError("No gold price data returned for GC=F.")

    gold = gold.reset_index()
    if hasattr(gold.columns, "levels"):
        gold.columns = [str(col).lower() for col in gold.columns.get_level_values(0)]
    else:
        gold.columns = [str(col).lower() for col in gold.columns]

    if "date" not in gold.columns and "datetime" in gold.columns:
        gold = gold.rename(columns={"datetime": "date"})

    gold["date"] = pd.to_datetime(gold["date"]).dt.strftime("%Y-%m-%d")
    numeric_columns = [column for column in ["open", "high", "low", "close", "volume"] if column in gold.columns]
    gold[numeric_columns] = gold[numeric_columns].apply(pd.to_numeric, errors="coerce")
    gold = gold.dropna(subset=["date", "close"]).sort_values("date").reset_index(drop=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    gold.to_csv(GOLD_CSV, index=False)
    _write_sample(gold[["date", "open", "high", "low", "close"]], GOLD_SAMPLE_CSV)
    print(f"Saved {len(gold)} gold price rows to {GOLD_CSV}")
    return str(GOLD_CSV)


def _fetch_war_news(**_context):
    import pandas as pd

    try:
        import requests
    except ImportError as exc:
        raise ImportError("pip install requests") from exc

    rows = []
    seen = set()
    end_date = datetime.now().strftime("%Y-%m-%d")
    keyword_query = " OR ".join(WAR_KEYWORDS)
    base_params = {
        "api-key": GUARDIAN_API_KEY,
        "q": f"({keyword_query})",
        "from-date": NEWS_START_DATE,
        "to-date": end_date,
        "section": GUARDIAN_SECTION,
        "page-size": GUARDIAN_PAGE_SIZE,
        "show-fields": "trailText,headline",
        "order-by": "oldest",
    }

    page = 1
    total_pages = 1
    while page <= total_pages:
        params = dict(base_params)
        params["page"] = page
        response = requests.get(GUARDIAN_API_URL, params=params, timeout=60)
        response.raise_for_status()
        payload = response.json()["response"]
        total_pages = payload["pages"]

        for entry in payload["results"]:
            title = _strip_html(entry.get("webTitle", ""))
            summary = _strip_html(entry.get("fields", {}).get("trailText", ""))
            date_value = entry["webPublicationDate"][:10]

            dedupe_key = entry.get("id") or (date_value, title)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            rows.append(
                {
                    "date": date_value,
                    "title": title[:250],
                    "summary": summary[:800],
                }
            )

        page += 1

    if not rows:
        raise ValueError("No historical war-related news items matched the keyword filter.")

    news = pd.DataFrame(rows).sort_values(["date", "title"]).reset_index(drop=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    news.to_csv(NEWS_CSV, index=False)
    _write_sample(news[["date", "title", "summary"]], NEWS_SAMPLE_CSV)
    print(f"Saved {len(news)} historical war-related news rows to {NEWS_CSV}")
    return str(NEWS_CSV)


def _compute_sentiment_and_merge(**_context):
    import pandas as pd

    try:
        from textblob import TextBlob
    except ImportError as exc:
        raise ImportError("pip install textblob") from exc

    gold = pd.read_csv(GOLD_CSV)
    news = pd.read_csv(NEWS_CSV)

    gold["date"] = pd.to_datetime(gold["date"])
    news["date"] = pd.to_datetime(news["date"])

    def sentiment(text: str) -> float:
        if pd.isna(text) or not str(text).strip():
            return 0.0
        return TextBlob(str(text)).sentiment.polarity

    news["sentiment"] = (news["title"].fillna("") + " " + news["summary"].fillna("")).apply(sentiment)
    daily_news = news.groupby("date")["sentiment"].agg(["mean", "count"]).reset_index()
    daily_news.columns = ["date", "sentiment_mean", "news_count"]

    gold = gold.sort_values("date").reset_index(drop=True)
    gold["daily_return"] = gold["close"].pct_change().fillna(0)
    gold["target"] = (gold["close"].shift(-1) > gold["close"]).astype(int)
    training = gold.merge(daily_news, on="date", how="left")
    training["sentiment_mean"] = training["sentiment_mean"].fillna(0.0)
    training["news_count"] = training["news_count"].fillna(0).astype(int)
    training = training.iloc[:-1].copy()
    training["date"] = training["date"].dt.strftime("%Y-%m-%d")

    training.to_csv(TRAINING_CSV, index=False)
    sample_columns = ["date", "close", "sentiment_mean", "news_count", "target"]
    _write_sample(training[sample_columns], TRAINING_SAMPLE_CSV)
    print(f"Saved {len(training)} training rows to {TRAINING_CSV}")
    return str(TRAINING_CSV)


def _train_model(**_context):
    import pickle

    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier

    training = pd.read_csv(TRAINING_CSV)
    if len(training) < 30:
        raise ValueError("Not enough rows to train a meaningful model.")

    features = ["open", "high", "low", "close", "daily_return", "sentiment_mean", "news_count"]
    X = training[features].fillna(0)
    y = training["target"]

    split_index = max(int(len(training) * 0.8), 1)
    if split_index >= len(training):
        split_index = len(training) - 1

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)

    payload = {
        "model": model,
        "features": features,
        "metadata": {
            "model_type": "RandomForestClassifier",
            "news_source": "Guardian Content API",
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "rows_with_news": int((training["news_count"] > 0).sum()),
            "accuracy": float(accuracy),
            "trained_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    }

    with open(MODEL_PATH, "wb") as handle:
        pickle.dump(payload, handle)

    print(f"Saved model to {MODEL_PATH}")
    print(f"Holdout accuracy: {accuracy:.3f}")
    return str(MODEL_PATH)


dag = DAG(
    dag_id="lecture6_mid_semester_gold_war_pipeline",
    start_date=datetime(2024, 1, 7),
    schedule="@weekly",
    catchup=False,
    tags=["lecture6", "mid-semester", "gold", "news", "ml"],
)

fetch_gold_prices = PythonOperator(
    task_id="fetch_gold_prices",
    python_callable=_fetch_gold_prices,
    dag=dag,
)

fetch_war_news = PythonOperator(
    task_id="fetch_war_news",
    python_callable=_fetch_war_news,
    dag=dag,
)

compute_sentiment_and_merge = PythonOperator(
    task_id="compute_sentiment_and_merge",
    python_callable=_compute_sentiment_and_merge,
    dag=dag,
)

train_model = PythonOperator(
    task_id="train_model",
    python_callable=_train_model,
    dag=dag,
)

[fetch_gold_prices, fetch_war_news] >> compute_sentiment_and_merge >> train_model
