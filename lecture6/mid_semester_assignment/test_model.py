#!/usr/bin/env python3
"""
Lecture 6 mid-semester assignment model test script.
"""

import argparse
import pickle
from pathlib import Path

import pandas as pd


DEFAULT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = DEFAULT_DIR / "gold_model.pkl"
DEFAULT_DATA_DIR = DEFAULT_DIR / "artifacts"


def load_model(model_path: Path):
    with open(model_path, "rb") as handle:
        payload = pickle.load(handle)
    return payload["model"], payload["features"], payload.get("metadata", {})


def test_model(model_path: Path, data_dir: Path) -> dict:
    model, features, metadata = load_model(model_path)

    training_csv = data_dir / "training_data.csv"
    if not training_csv.exists():
        raise FileNotFoundError(
            f"Training data not found: {training_csv}. Run the pipeline first."
        )

    df = pd.read_csv(training_csv)
    X = df[features].fillna(0)
    y = df["target"]

    accuracy = model.score(X, y)
    predictions = model.predict(X)
    sample = df[["date", "close", "target"]].head(10).copy()
    sample["predicted"] = predictions[:10]

    return {
        "accuracy": accuracy,
        "n_samples": len(df),
        "sample_predictions": sample,
        "metadata": metadata,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Test gold price prediction model")
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
        help="Directory containing training_data.csv",
    )
    args = parser.parse_args()

    if not args.model.exists():
        print(f"ERROR: Model not found: {args.model}")
        print("Run the ETL pipeline first to train and save the model.")
        return 1

    result = test_model(args.model, args.data)
    print("\n=== Model Test Results ===")
    print(f"Accuracy: {result['accuracy']:.3f}")
    print(f"Samples:  {result['n_samples']}")

    metadata = result["metadata"]
    if metadata:
        print(f"Model type: {metadata.get('model_type', 'unknown')}")
        print(f"News source: {metadata.get('news_source', 'unknown')}")
        print(f"Train rows:  {metadata.get('train_rows', 'unknown')}")
        print(f"Test rows:   {metadata.get('test_rows', 'unknown')}")
        print(f"Rows with news: {metadata.get('rows_with_news', 'unknown')}")
        print(f"Holdout accuracy: {metadata.get('accuracy', 'unknown')}")
        print(f"Saved at:    {metadata.get('trained_at', 'unknown')}")

    print("\nSample predictions (first 10):")
    print(result["sample_predictions"].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
