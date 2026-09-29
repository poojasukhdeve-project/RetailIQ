import streamlit as st
import pandas as pd
import plotly.express as px


def render(executive, fact_sales, dim_store, dim_product, selected_store):
    # Executive Overview
    # --------------------------------------

    st.markdown(
        '<div class="executive-container">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-kicker">SECTION 1 OF 6</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Executive Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-question">How are we doing?</div>',
        unsafe_allow_html=True,
    )


    total_revenue = fact_sales["revenue"].sum()
    total_units = fact_sales["units_sold"].sum()
    active_products = executive["item_id"].nunique()
    active_stores = fact_sales["store_id"].nunique()
    high_risk_products = (
        executive["risk_category"] == "High Risk"
    ).sum()


    # --------------------------------------
    # KPI Cards
    # --------------------------------------

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-revenue">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">Total Revenue</div>
                <div class="kpi-value">${total_revenue:,.2f}</div>
                <div class="kpi-note">Analysis period revenue</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-units">
                <div class="kpi-icon">🛒</div>
                <div class="kpi-label">Units Sold</div>
                <div class="kpi-value">{total_units:,.0f}</div>
                <div class="kpi-note">Total recorded units</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-products">
                <div class="kpi-icon">📦</div>
                <div class="kpi-label">Active Products</div>
                <div class="kpi-value">{active_products:,}</div>
                <div class="kpi-note">Products in analysis</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-risk">
                <div class="kpi-icon">⚠️</div>
                <div class="kpi-label">Risk Level</div>
                <div class="kpi-value kpi-risk-value">High</div>
                <div class="kpi-note">
                    {high_risk_products:,} high-risk products identified
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------
    # Revenue Data
    # --------------------------------------

    monthly_revenue = (
        fact_sales
        .groupby(fact_sales["date"].dt.to_period("M"))
        .agg(revenue=("revenue", "sum"))
        .reset_index()
    )

    monthly_revenue["date"] = monthly_revenue["date"].dt.to_timestamp()


    store_revenue = (
        fact_sales
        .groupby("store_id")
        .agg(revenue=("revenue", "sum"))
        .reset_index()
    )

    state_revenue = (
        store_revenue
        .merge(dim_store[["store_id", "state_id"]], on="store_id", how="left")
        .groupby("state_id", as_index=False)["revenue"]
        .sum()
    )


    # --------------------------------------
    # Revenue Charts
    # --------------------------------------

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Revenue Trend</div>
                <div class="chart-subtitle">
                    Monthly revenue over the analysis period
                </div>
            """,
            unsafe_allow_html=True,
        )

        revenue_chart = px.area(
            monthly_revenue,
            x="date",
            y="revenue",
        )

        revenue_chart.update_traces(line=dict(width=3))

        revenue_chart.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
            showlegend=False,
        )

        revenue_chart.update_xaxes(
            showgrid=False,
            title=None,
        )

        revenue_chart.update_yaxes(
            showgrid=True,
            gridcolor="#edf2f7",
            title=None,
            tickprefix="$",
        )

        st.plotly_chart(
            revenue_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)


    with chart_right:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Revenue by State</div>
                <div class="chart-subtitle">
                    Total revenue contribution across states
                </div>
            """,
            unsafe_allow_html=True,
        )

        state_chart = px.pie(
            state_revenue,
            names="state_id",
            values="revenue",
            hole=0.60,
        )

        state_chart.update_traces(
            textposition="inside",
            textinfo="percent",
        )

        state_chart.add_annotation(
            text=(
                f"${total_revenue / 1_000_000:.2f}M"
                "<br><span style='font-size:11px'>Total Revenue</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="#102b4c"),
        )

        state_chart.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
        )

        st.plotly_chart(
            state_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------
    # Executive Insight
    # --------------------------------------

    st.markdown(
        """
        <div class="info-box">
            <div class="info-title">💡 Executive Insight</div>
            The overview connects overall revenue and sales activity with
            geographic contribution and product-level risk, giving decision-makers
            a clear starting point before deeper store, product, forecast,
            and inventory analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )




    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------
