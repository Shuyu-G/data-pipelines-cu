# Lecture 6 Mid-Semester Assignment

This folder contains the submission files for the gold price and war news ML pipeline assignment.

The implementation uses a historical news API so the news dates line up with the gold price date range used for model training.

Expected deliverables in this folder:

- `gold_war_etl_dag.py`
- `test_model.py`
- `predict_next_day.py`
- `requirements.txt`
- `gold_model.pkl`
- `gold_prices_sample.csv`
- `war_news_sample.csv`
- `training_data_sample.csv`

Generated full-size pipeline outputs are written under `artifacts/`.

To view the model's next-trading-day prediction locally:

```bash
python predict_next_day.py
```

The script also writes the latest prediction to `artifacts/next_day_prediction.json`.
