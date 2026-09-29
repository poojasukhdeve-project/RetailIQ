import streamlit as st
import pandas as pd
import plotly.express as px


def render(executive, fact_forecast, selected_store):
    # Demand Forecast
    # --------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="executive-container">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-kicker">SECTION 4 OF 6</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Demand Forecast</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-question">What happens next?</div>',
        unsafe_allow_html=True,
    )

    forecast_start = fact_forecast["date"].min()
    forecast_end = fact_forecast["date"].max()

    total_actual_units = fact_forecast["actual_units"].sum()
    total_predicted_units = fact_forecast["predicted_units"].clip(lower=0).sum()

    forecast_gap = total_predicted_units - total_actual_units
    forecast_gap_pct = (
        forecast_gap / total_actual_units * 100
        if total_actual_units else 0
    )

    forecast_mae = 3.7572
    forecast_rmse = 7.0657

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-units">
                <div class="kpi-icon">📅</div>
                <div class="kpi-label">Forecast Period</div>
                <div class="kpi-value" style="font-size:20px;">
                    {forecast_start.strftime("%d %b")} –
                    {forecast_end.strftime("%d %b %Y")}
                </div>
                <div class="kpi-note">30-day model evaluation period</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-revenue">
                <div class="kpi-icon">🔮</div>
                <div class="kpi-label">Predicted Units</div>
                <div class="kpi-value">{total_predicted_units:,.0f}</div>
                <div class="kpi-note">Model-predicted demand</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-products">
                <div class="kpi-icon">🎯</div>
                <div class="kpi-label">Forecast MAE</div>
                <div class="kpi-value">{forecast_mae:.4f}</div>
                <div class="kpi-note">Lower is better</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-risk">
                <div class="kpi-icon">📐</div>
                <div class="kpi-label">Forecast RMSE</div>
                <div class="kpi-value">{forecast_rmse:.4f}</div>
                <div class="kpi-note">Lower is better</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    daily_forecast = (
        fact_forecast
        .groupby("date")
        .agg(
            actual_units=("actual_units", "sum"),
            predicted_units=("predicted_units", "sum"),
        )
        .reset_index()
    )

    daily_forecast["predicted_units"] = daily_forecast["predicted_units"].clip(lower=0)

    forecast_long = daily_forecast.melt(
        id_vars="date",
        value_vars=["actual_units", "predicted_units"],
        var_name="series",
        value_name="units",
    )

    forecast_long["series"] = forecast_long["series"].map({
        "actual_units": "Actual Demand",
        "predicted_units": "Predicted Demand",
    })

    forecast_left, forecast_right = st.columns(2)

    with forecast_left:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Actual vs Predicted Demand</div>
                <div class="chart-subtitle">
                    Daily demand during the model evaluation period
                </div>
            """,
            unsafe_allow_html=True,
        )

        forecast_chart = px.line(
            forecast_long,
            x="date",
            y="units",
            color="series",
            markers=True,
        )

        forecast_chart.update_layout(
            height=380,
            margin=dict(l=10, r=20, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
            legend_title=None,
        )

        forecast_chart.update_xaxes(showgrid=False, title=None)
        forecast_chart.update_yaxes(
            showgrid=True,
            gridcolor="#edf2f7",
            title=None,
        )

        st.plotly_chart(
            forecast_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with forecast_right:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Forecast Gap</div>
                <div class="chart-subtitle">
                    Predicted demand minus actual demand by day
                </div>
            """,
            unsafe_allow_html=True,
        )

        daily_forecast["gap"] = (
            daily_forecast["predicted_units"] -
            daily_forecast["actual_units"]
        )

        gap_chart = px.bar(
            daily_forecast,
            x="date",
            y="gap",
        )

        gap_chart.update_traces(marker_line_width=0)

        gap_chart.update_layout(
            height=380,
            margin=dict(l=10, r=20, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
            showlegend=False,
        )

        gap_chart.update_xaxes(showgrid=False, title=None)
        gap_chart.update_yaxes(
            showgrid=True,
            gridcolor="#edf2f7",
            title=None,
            zeroline=True,
            zerolinecolor="#b8c7d8",
        )

        st.plotly_chart(
            gap_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    product_forecast = (
        fact_forecast
        .groupby("item_id")
        .agg(
            actual_units=("actual_units", "sum"),
            predicted_units=("predicted_units", "sum"),
        )
        .reset_index()
    )

    product_forecast["predicted_units"] = (
        product_forecast["predicted_units"].clip(lower=0)
    )

    product_forecast["forecast_gap"] = (
        product_forecast["predicted_units"] -
        product_forecast["actual_units"]
    )

    product_forecast["forecast_gap_pct"] = (
        product_forecast["forecast_gap"] /
        product_forecast["actual_units"].replace(0, pd.NA) * 100
    )

    product_forecast = product_forecast.merge(
        executive[
            [
                "item_id",
                "abc_class",
                "avg_daily_demand",
                "inventory_risk_score",
                "risk_category",
            ]
        ],
        on="item_id",
        how="left",
    )

    forecast_table = (
        product_forecast
        .assign(abs_gap=lambda x: x["forecast_gap"].abs())
        .sort_values("abs_gap", ascending=False)
        .head(10)
        .drop(columns="abs_gap")
    )

    st.markdown(
        """
        <div class="chart-title">Product Forecast Signals</div>
        <div class="chart-subtitle">
            Products with the largest differences between predicted and actual demand
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        forecast_table[
            [
                "item_id",
                "abc_class",
                "actual_units",
                "predicted_units",
                "forecast_gap",
                "forecast_gap_pct",
                "risk_category",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "item_id": "Product ID",
            "abc_class": "ABC Class",
            "actual_units": "Actual Units",
            "predicted_units": "Predicted Units",
            "forecast_gap": "Forecast Gap",
            "forecast_gap_pct": st.column_config.NumberColumn(
                "Gap %",
                format="%.2f%%",
            ),
            "risk_category": "Risk",
        },
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if forecast_gap >= 0:
        gap_message = (
            f"The model predicted {abs(forecast_gap_pct):.2f}% more units "
            "than were actually observed across the evaluation period."
        )
    else:
        gap_message = (
            f"The model predicted {abs(forecast_gap_pct):.2f}% fewer units "
            "than were actually observed across the evaluation period."
        )

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">💡 Forecast Insight</div>
            {gap_message}
            The current model is evaluated on a historical 30-day holdout and
            operates at the <b>product level across stores</b>. It is therefore
            a validated demand signal rather than a true future 2026 forecast.
            The next section can use these demand signals together with inventory
            risk to support operational decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


    # --------------------------------------
