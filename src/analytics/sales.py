"""RetailIQ retail sales analytics functions."""

import pandas as pd


# --------------------------------------
# Revenue Calculation
# --------------------------------------

def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate revenue from units sold and selling price."""

    df = df.copy()

    df["revenue"] = (
        df["units_sold"] * df["sell_price"]
    )

    return df


# --------------------------------------
# Top Products
# --------------------------------------

def top_products(
    df: pd.DataFrame,
    n: int = 10
) -> pd.DataFrame:
    """Return top products by units sold."""

    return (
        df.groupby("item_id", as_index=False)["units_sold"]
        .sum()
        .sort_values(
            "units_sold",
            ascending=False
        )
        .head(n)
        .reset_index(drop=True)
    )


# --------------------------------------
# Top Products by Revenue
# --------------------------------------

def top_products_by_revenue(
    df: pd.DataFrame,
    n: int = 10
) -> pd.DataFrame:
    """Return top products by revenue."""

    return (
        df.groupby("item_id", as_index=False)["revenue"]
        .sum()
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(n)
        .reset_index(drop=True)
    )


# --------------------------------------
# Store Performance
# --------------------------------------

def store_performance(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate sales performance by store."""

    return (
        df.groupby("store_id")
        .agg(
            units_sold=("units_sold", "sum"),
            revenue=("revenue", "sum"),
            avg_daily_revenue=("revenue", "mean")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
        .reset_index(drop=True)
    )


# --------------------------------------
# Category Performance
# --------------------------------------

def category_performance(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate sales performance by category."""

    return (
        df.groupby("cat_id")
        .agg(
            units_sold=("units_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
        .reset_index(drop=True)
    )


# --------------------------------------
# Daily Sales
# --------------------------------------

def daily_sales(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate sales by date."""

    return (
        df.groupby("date")
        .agg(
            units_sold=("units_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
        .sort_values("date")
        .reset_index(drop=True)
    )
