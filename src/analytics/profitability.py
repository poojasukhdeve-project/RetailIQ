"""Profitability analytics for RetailIQ.

Provides reusable profitability calculations.
"""

import pandas as pd


# --------------------------------------
# Estimated Profit Calculation
# --------------------------------------

def add_estimated_profit(
    df: pd.DataFrame,
    estimated_cost_ratio: float = 0.70
) -> pd.DataFrame:
    """Add estimated cost, profit, and profit margin."""

    df = df.copy()

    df["estimated_cost"] = (
        df["revenue"] * estimated_cost_ratio
    )

    df["estimated_profit"] = (
        df["revenue"] - df["estimated_cost"]
    )

    df["profit_margin"] = (
        df["estimated_profit"]
        / df["revenue"].replace(0, pd.NA)
    )

    return df


# --------------------------------------
# Profitability Summary
# --------------------------------------

def create_profitability_summary(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Create an overall profitability summary."""

    summary = pd.DataFrame({
        "total_revenue": [df["revenue"].sum()],
        "estimated_cost": [df["estimated_cost"].sum()],
        "estimated_profit": [df["estimated_profit"].sum()],
        "profit_margin": [df["estimated_profit"].sum()
                          / df["revenue"].sum()]
    })

    return summary


# --------------------------------------
# Product Profitability
# --------------------------------------

def calculate_product_profitability(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate profitability by product."""

    product_profitability = (
        df.groupby("item_id")
        .agg(
            revenue=("revenue", "sum"),
            estimated_cost=("estimated_cost", "sum"),
            estimated_profit=("estimated_profit", "sum"),
            units_sold=("units_sold", "sum")
        )
        .reset_index()
    )

    product_profitability["profit_margin"] = (
        product_profitability["estimated_profit"]
        / product_profitability["revenue"].replace(0, pd.NA)
    )

    return product_profitability.sort_values(
        "estimated_profit",
        ascending=False
    ).reset_index(drop=True)