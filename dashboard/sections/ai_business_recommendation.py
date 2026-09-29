import streamlit as st
import pandas as pd


def render(executive, fact_sales, fact_forecast, fact_inventory, dim_product, selected_store):
    # --------------------------------------
    # AI Business Recommendation
    # --------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="executive-container">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-kicker">SECTION 6 OF 6</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">AI Business Recommendation 🤖</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-question">What should we consider doing?</div>',
        unsafe_allow_html=True,
    )

    store_data = fact_sales[
        fact_sales["store_id"] == selected_store
    ].copy()

    store_revenue = store_data["revenue"].sum()

    store_summary = (
        fact_sales
        .groupby("store_id")
        .agg(revenue=("revenue", "sum"))
        .reset_index()
    )

    average_store_revenue = store_summary["revenue"].mean()
    revenue_gap = store_revenue - average_store_revenue
    revenue_gap_pct = (
        revenue_gap / average_store_revenue * 100
        if average_store_revenue else 0
    )

    product_store = (
        store_data
        .groupby("item_id")
        .agg(
            revenue=("revenue", "sum"),
            units_sold=("units_sold", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    top_product = (
        product_store.iloc[0]["item_id"]
        if not product_store.empty else "N/A"
    )

    top_product_revenue = (
        product_store.iloc[0]["revenue"]
        if not product_store.empty else 0
    )

    risk_table = fact_inventory.sort_values(
        "inventory_risk_score",
        ascending=False,
    )

    top_risk = (
        risk_table.iloc[0]["item_id"]
        if not risk_table.empty else "N/A"
    )

    top_risk_score = (
        risk_table.iloc[0]["inventory_risk_score"]
        if not risk_table.empty else 0
    )

    top_risk_class = (
        risk_table.iloc[0]["abc_class"]
        if not risk_table.empty else "N/A"
    )

    forecast_product = (
        fact_forecast
        .groupby("item_id")
        .agg(
            actual_units=("actual_units", "sum"),
            predicted_units=("predicted_units", "sum"),
        )
        .reset_index()
    )

    forecast_product["predicted_units"] = (
        forecast_product["predicted_units"].clip(lower=0)
    )

    forecast_product = forecast_product.merge(
        executive[
            [
                "item_id",
                "risk_category",
                "inventory_risk_score",
                "abc_class",
            ]
        ],
        on="item_id",
        how="left",
    )

    priority_products = (
        forecast_product
        .sort_values(
            ["inventory_risk_score", "predicted_units"],
            ascending=[False, False],
        )
        .head(5)
    )

    priority_item = (
        priority_products.iloc[0]["item_id"]
        if not priority_products.empty else top_risk
    )

    priority_forecast = (
        priority_products.iloc[0]["predicted_units"]
        if not priority_products.empty else 0
    )

    if revenue_gap < 0:
        store_action = (
            f"Review {selected_store}'s product mix and inventory allocation. "
            f"The store is {abs(revenue_gap_pct):.1f}% below the average "
            "store revenue in the analysis period."
        )
        store_label = "Store Opportunity"
    else:
        store_action = (
            f"Use {selected_store}'s stronger performance as a benchmark and "
            "identify which products and demand patterns are contributing to it."
        )
        store_label = "Store Strength"

    recommendation = (
        f"Prioritize <b>{priority_item}</b> for inventory review at the "
        f"next planning cycle. It combines a high inventory-risk signal with "
        f"forecast demand of approximately <b>{priority_forecast:,.0f}</b> units "
        "over the evaluated 30-day period. Before increasing allocation, "
        "validate current stock levels, lead times, and actual replenishment "
        "constraints."
    )

    a1, a2, a3 = st.columns(3)

    with a1:
        st.markdown(
            f"""
            <div class="chart-card">
                <div class="chart-title">🎯 {store_label}</div>
                <div class="chart-subtitle">Selected store signal</div>
                <p style="color:#52677f;line-height:1.6;">
                    {store_action}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a2:
        st.markdown(
            f"""
            <div class="chart-card">
                <div class="chart-title">📦 Product Signal</div>
                <div class="chart-subtitle">Top revenue product</div>
                <p style="color:#52677f;line-height:1.6;">
                    <b>{top_product}</b> generated
                    <b>${top_product_revenue:,.2f}</b> at {selected_store}.
                    Use this product as a starting point when reviewing
                    demand and inventory decisions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a3:
        st.markdown(
            f"""
            <div class="chart-card">
                <div class="chart-title">⚠️ Risk Signal</div>
                <div class="chart-subtitle">Highest inventory priority</div>
                <p style="color:#52677f;line-height:1.6;">
                    <b>{top_risk}</b> has the highest inventory-risk score
                    of <b>{top_risk_score:.4f}</b> and belongs to
                    ABC class <b>{top_risk_class}</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">🤖 AI Decision Layer</div>
            {recommendation}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="chart-title">Decision Flow</div>
        <div class="chart-subtitle">
            How RetailIQ moves from raw data to an actionable business signal
        </div>
        """,
        unsafe_allow_html=True,
    )

    flow1, flow2, flow3, flow4, flow5 = st.columns(5)

    flow_items = [
        ("📊", "Data", "Sales & product history"),
        ("🔎", "Insight", "Store & product performance"),
        ("🔮", "Prediction", "Demand forecast"),
        ("⚠️", "Risk", "Inventory prioritization"),
        ("🤖", "Decision", "Business recommendation"),
    ]

    for col, (icon, title, description) in zip(
        [flow1, flow2, flow3, flow4, flow5],
        flow_items,
    ):
        with col:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:15px 8px;
                    border:1px solid #e0e8f2;
                    border-radius:14px;
                    background:#fbfdff;
                ">
                    <div style="font-size:25px;">{icon}</div>
                    <div style="
                        color:#102b4c;
                        font-weight:800;
                        margin-top:5px;
                    ">{title}</div>
                    <div style="
                        color:#8a99aa;
                        font-size:11px;
                        margin-top:4px;
                    ">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="info-box">
            <div class="info-title">ℹ️ Recommendation Note</div>
            This recommendation layer is generated from RetailIQ's structured
            analytics, forecast, and risk outputs. It is not a replacement for
            operational checks such as current stock, supplier lead time,
            pricing, or actual unit cost.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
