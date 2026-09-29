"""Load RetailIQ datasets."""

from pathlib import Path
import pandas as pd

RAW_DATA = Path(__file__).resolve().parents[2] / "data" / "raw"


def load_sales():
    return pd.read_csv(RAW_DATA / "sales_train_validation.csv")


def load_calendar():
    return pd.read_csv(RAW_DATA / "calendar.csv")


def load_prices():
    return pd.read_csv(RAW_DATA / "sell_prices.csv")
