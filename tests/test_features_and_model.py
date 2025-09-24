import polars as pl

from src.pipeline.features import daily_store_sales
from src.pipeline.model import train_baseline, forecast


def test_daily_and_model_forecast():
    # Build small synthetic dataset
    dates = pl.date_range(low=pl.date(2024, 1, 1), high=pl.date(2024, 1, 20), eager=True)
    df = pl.DataFrame({
        "date": dates,
        "store_id": ["s1"] * len(dates),
        "product_id": ["p1"] * len(dates),
        "quantity": [1.0 + (i % 3) for i in range(len(dates))],
        "price": [10.0] * len(dates),
    })
    daily = daily_store_sales(df)
    art = train_baseline(daily)
    fc = forecast(art, daily, 3)
    assert fc.height == 3  # for single store
    assert set(fc.columns) == {"store_id", "date", "rev_fcst"}


