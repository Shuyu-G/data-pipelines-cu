#!/usr/bin/env python3
"""
Predict the next trading day's gold price direction using the latest
available gold-price row plus same-day news features.
"""

import argparse
import json
import pickle
from pathlib import Path

import pandas as pd
from pandas.tseries.offsets import BDay
from textblob import TextBlob


DEFAULT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = DEFAULT_DIR / "gold_model.pkl"
DEFAULT_DATA_DIR = DEFAULT_DIR / "artifacts"
DEFAULT_OUTPUT = DEFAULT_DATA_DIR / "next_day_prediction.json"


def load_model(model_path: Path):
    with open(model_path, "rb") as handle:
        payload = pickle.load(handle)
    return payload["model"], payload["features"], payload.get("metadata", {})


def _sentiment(text: str) -> float:
    if pd.isna(text) or not str(text).strip():
        return 0.0
    return TextBlob(str(text)).sentiment.polarity


def _build_latest_feature_row(data_dir: Path, features: list[str]) -> dict:
    gold_csv = data_dir / "gold_prices.csv"
    news_csv = data_dir / "war_news.csv"

    if not gold_csv.exists():
        raise FileNotFoundError(f"Gold prices not found: {gold_csv}. Run the pipeline first.")
    if not news_csv.exists():
        raise FileNotFoundError(f"War news not found: {news_csv}. Run the pipeline first.")

    gold = pd.read_csv(gold_csv)
    news = pd.read_csv(news_csv)

    gold["date"] = pd.to_datetime(gold["date"])
    news["date"] = pd.to_datetime(news["date"])

    gold = gold.sort_values("date").reset_index(drop=True)
    gold["daily_return"] = gold["close"].pct_change().fillna(0)

    news["sentiment"] = (
        news["title"].fillna("") + " " + news["summary"].fillna("")
    ).apply(_sentiment)
    daily_news = news.groupby("date")["sentiment"].agg(["mean", "count"]).reset_index()
    daily_news.columns = ["date", "sentiment_mean", "news_count"]

    latest_gold = gold.iloc[-1].copy()
    latest_news = daily_news[daily_news["date"] == latest_gold["date"]]
    if latest_news.empty:
        sentiment_mean = 0.0
        news_count = 0
    else:
        sentiment_mean = float(latest_news.iloc[0]["sentiment_mean"])
        news_count = int(latest_news.iloc[0]["news_count"])

    feature_values = latest_gold.to_dict()
    feature_values["sentiment_mean"] = sentiment_mean
    feature_values["news_count"] = news_count

    x_latest = pd.DataFrame(
        [{feature: feature_values[feature] for feature in features}]
    ).fillna(0)

    latest_date = latest_gold["date"]
    prediction_date = (latest_date + BDay(1)).strftime("%Y-%m-%d")

    return {
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "prediction_for_date": prediction_date,
        "latest_close": float(latest_gold["close"]),
        "x_latest": x_latest,
        "features": {feature: feature_values[feature] for feature in features},
    }


def predict_next_day(model_path: Path, data_dir: Path, output_path: Path | None = None) -> dict:
    model, features, metadata = load_model(model_path)
    latest_row = _build_latest_feature_row(data_dir, features)

    prediction = int(model.predict(latest_row["x_latest"])[0])
    probabilities = None
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(latest_row["x_latest"])[0]

    result = {
        "latest_feature_date": latest_row["latest_date"],
        "prediction_for_date": latest_row["prediction_for_date"],
        "latest_close": latest_row["latest_close"],
        "prediction": prediction,
        "prediction_label": "UP" if prediction == 1 else "DOWN",
        "prob_down": float(probabilities[0]) if probabilities is not None else None,
        "prob_up": float(probabilities[1]) if probabilities is not None else None,
        "features": latest_row["features"],
        "metadata": metadata,
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, default=str)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Predict the next trading day gold direction"
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
        help="Path to saved model .pkl",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing gold_prices.csv and war_news.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Where to save the JSON prediction output",
    )
    args = parser.parse_args()

    if not args.model.exists():
        print(f"ERROR: Model not found: {args.model}")
        print("Run the ETL pipeline first to train and save the model.")
        return 1

    result = predict_next_day(args.model, args.data, args.output)
    print("=== Next Trading Day Prediction ===")
    print(f"Latest feature date: {result['latest_feature_date']}")
    print(f"Prediction for date:  {result['prediction_for_date']}")
    print(f"Latest close price:  {result['latest_close']:.2f}")
    print(f"Prediction:          {result['prediction_label']}")
    if result["prob_up"] is not None and result["prob_down"] is not None:
        print(f"Probability UP:      {result['prob_up']:.3f}")
        print(f"Probability DOWN:    {result['prob_down']:.3f}")

    metadata = result["metadata"]
    if metadata:
        print(f"Model source:        {metadata.get('news_source', 'unknown')}")
        print(f"Model trained at:    {metadata.get('trained_at', 'unknown')}")

    print("\nLatest features used:")
    for key, value in result["features"].items():
        print(f"- {key}: {value}")
    print(f"\nSaved prediction JSON: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
