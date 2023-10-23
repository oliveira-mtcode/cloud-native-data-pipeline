import polars as pl

from src.pipeline.transform import clean_sales, clean_customers


def test_clean_sales_basic():
    df = pl.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "store_id": ["s1", "s1"],
        "product_id": ["p1", "p2"],
        "quantity": [1, 2],
        "price": [10.0, 12.0],
    })
    out = clean_sales(df)
    assert out.height == 2
    assert "revenue" in out.columns
    assert out.select(pl.sum("revenue")).item() == 34.0


def test_clean_customers_basic():
    df = pl.DataFrame({
        "customer_id": ["c1", "c2"],
        "signup_date": ["2024-01-01", "2024-01-02"],
    })
    out = clean_customers(df)
    assert out.height == 2
    assert out.select(pl.col("customer_id").is_not_null().all()).item() is True


