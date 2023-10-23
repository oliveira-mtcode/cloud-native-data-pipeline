from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import polars as pl
from sklearn.linear_model import LinearRegression

from .config import modeling
from .logging_utils import get_logger


logger = get_logger(__name__)


@dataclass
class ModelArtifacts:
    model: LinearRegression
    feature_cols: list[str]
    target_col: str


def prepare_supervised(df: pl.DataFrame) -> Tuple[np.ndarray, np.ndarray, list[str]]:
    # Simple baseline: forecast next-day revenue using lag features
    df = df.sort(["store_id", "date"]).with_columns([
        pl.col("rev_sum").shift(1).over("store_id").alias("rev_lag1"),
        pl.col("rev_sum").shift(7).over("store_id").alias("rev_lag7"),
        pl.col("qty_sum").shift(1).over("store_id").alias("qty_lag1"),
    ])

    df = df.drop_nulls(["rev_lag1", "rev_lag7", "qty_lag1"])  # drop cold starts
    feature_cols = ["rev_lag1", "rev_lag7", "qty_lag1", "num_txn"]
    target_col = "rev_sum"

    X = df.select(feature_cols).to_numpy()
    y = df.select(target_col).to_numpy().ravel()
    return X, y, feature_cols


def train_baseline(df_daily: pl.DataFrame) -> ModelArtifacts:
    X, y, feature_cols = prepare_supervised(df_daily)
    n = len(y)
    val_days = modeling.validation_days
    split = max(1, n - val_days)
    X_train, y_train = X[:split], y[:split]
    X_val, y_val = X[split:], y[split:]

    model = LinearRegression()
    model.fit(X_train, y_train)
    if len(y_val) > 0:
        val_mae = float(np.mean(np.abs(model.predict(X_val) - y_val)))
        logger.info("Validation MAE: %.4f", val_mae)
    return ModelArtifacts(model=model, feature_cols=feature_cols, target_col="rev_sum")


def forecast(artifacts: ModelArtifacts, recent_daily: pl.DataFrame, horizon_days: int) -> pl.DataFrame:
    # Roll forward using last available lags per store
    forecasts = []
    stores = recent_daily.select("store_id").unique().to_series().to_list()
    for store in stores:
        hist = recent_daily.filter(pl.col("store_id") == store).sort("date")
        hist_pd = hist.select(["date", "rev_sum", "qty_sum", "num_txn"]).to_pandas()
        rev = hist_pd["rev_sum"].values.tolist()
        qty = hist_pd["qty_sum"].values.tolist()
        num_txn = hist_pd["num_txn"].values.tolist()
        dates = hist_pd["date"].values.tolist()

        for i in range(horizon_days):
            rev_lag1 = rev[-1] if len(rev) >= 1 else 0.0
            rev_lag7 = rev[-7] if len(rev) >= 7 else rev_lag1
            qty_lag1 = qty[-1] if len(qty) >= 1 else 0.0
            x = np.array([[rev_lag1, rev_lag7, qty_lag1, num_txn[-1] if num_txn else 0.0]])
            yhat = float(artifacts.model.predict(x)[0])
            rev.append(yhat)
            qty.append(qty_lag1)
            num_txn.append(num_txn[-1] if num_txn else 0.0)
            dates.append(dates[-1] + np.timedelta64(1, 'D'))
            forecasts.append({"store_id": store, "date": dates[-1], "rev_fcst": yhat})

    return pl.DataFrame(forecasts)


