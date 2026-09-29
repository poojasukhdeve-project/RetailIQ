"""Data cleaning and transformation functions for RetailIQ.""""

import pandas as pd


def clean_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    calendar = calendar.copy()
    calendar["date"] = pd.to_datetime(calendar["date"])
    return calendar


def reshape_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """Convert M5 daily sales from wide format to long format."""
    id_columns = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    day_columns = [c for c in sales.columns if c.startswith("d_")]

    long_df = sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )
    return long_df
