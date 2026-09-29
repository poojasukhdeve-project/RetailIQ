"""RetailIQ demand forecasting module.

Provides reusable feature engineering and forecasting functions.
"""


# --------------------------------------
# Feature Engineering
# --------------------------------------

def create_forecast_features(df):
    """Create time-series features for demand forecasting."""

    df = df.copy()

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["week_of_year"] = (
        df["date"].dt.isocalendar().week.astype(int)
    )

    df["lag_1"] = (
        df.groupby("item_id")["units_sold"]
        .shift(1)
    )

    df["lag_7"] = (
        df.groupby("item_id")["units_sold"]
        .shift(7)
    )

    df["lag_28"] = (
        df.groupby("item_id")["units_sold"]
        .shift(28)
    )

    df["rolling_7"] = (
        df.groupby("item_id")["units_sold"]
        .transform(
            lambda x: x.shift(1).rolling(7).mean()
        )
    )

    df["rolling_28"] = (
        df.groupby("item_id")["units_sold"]
        .transform(
            lambda x: x.shift(1).rolling(28).mean()
        )
    )

    return df


# --------------------------------------
# Forecast Features
# --------------------------------------

FORECAST_FEATURES = [
    "day_of_week",
    "month",
    "week_of_year",
    "lag_1",
    "lag_7",
    "lag_28",
    "rolling_7",
    "rolling_28",
]


# --------------------------------------
# Prepare Forecast Dataset
# --------------------------------------

def prepare_forecast_dataset(df):
    """Create the final dataset used by the forecasting model."""

    df = create_forecast_features(df)

    df = df.dropna(
        subset=FORECAST_FEATURES + ["units_sold"]
    ).reset_index(drop=True)

    return df
