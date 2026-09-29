import streamlit as st
import pandas as pd
import plotly.express as px


def render(executive, fact_inventory, dim_product, selected_store):
    # --------------------------------------
    # Inventory & Risk
    # --------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="executive-container">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-kicker">SECTION 5 OF 6</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Inventory & Risk</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-question">Can we support the demand?</div>',
        unsafe_allow_html=True,
    )

    inventory = fact_inventory.copy()

    high_risk = inventory[inventory["risk_category"] == "High Risk"].copy()
    medium_risk = inventory[inventory["risk_category"] == "Medium Risk"].copy()

    high_risk_count = len(high_risk)
    medium_risk_count = len(medium_risk)
    avg_risk = inventory["inventory_risk_score"].mean()
    total_demand = inventory["avg_daily_demand"].sum()

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-risk">
                <div class="kpi-icon">⚠️</div>
                <div class="kpi-label">High-Risk Products</div>
                <div class="kpi-value kpi-risk-value">{high_risk_count:,}</div>
                <div class="kpi-note">Products requiring attention</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-products">
                <div class="kpi-icon">🟠</div>
                <div class="kpi-label">Medium-Risk Products</div>
                <div class="kpi-value">{medium_risk_count:,}</div>
                <div class="kpi-note">Products to monitor</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-units">
                <div class="kpi-icon">📊</div>
                <div class="kpi-label">Average Risk Score</div>
                <div class="kpi-value">{avg_risk:.2f}</div>
                <div class="kpi-note">Across all products</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-revenue">
                <div class="kpi-icon">📦</div>
                <div class="kpi-label">Daily Demand Base</div>
                <div class="kpi-value">{total_demand:,.0f}</div>
                <div class="kpi-note">Average daily units</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    risk_distribution = (
        inventory["risk_category"]
        .value_counts()
        .rename_axis("risk_category")
        .reset_index(name="products")
    )

    risk_left, risk_right = st.columns(2)

    with risk_left:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Risk Distribution</div>
                <div class="chart-subtitle">
                    Product count by inventory risk category
                </div>
            """,
            unsafe_allow_html=True,
        )

        risk_chart = px.pie(
            risk_distribution,
            names="risk_category",
            values="products",
            hole=0.58,
        )

        risk_chart.update_traces(
            textposition="inside",
            textinfo="percent",
        )

        risk_chart.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
        )

        st.plotly_chart(
            risk_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with risk_right:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Highest-Risk Products</div>
                <div class="chart-subtitle">
                    Products combining demand and inventory risk signals
                </div>
            """,
            unsafe_allow_html=True,
        )

        top_risk = (
            inventory
            .sort_values("inventory_risk_score", ascending=False)
            .head(10)
            .sort_values("inventory_risk_score")
        )

        risk_bar = px.bar(
            top_risk,
            x="inventory_risk_score",
            y="item_id",
            orientation="h",
        )

        risk_bar.update_traces(marker_line_width=0)

        risk_bar.update_layout(
            height=360,
            margin=dict(l=10, r=25, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
            showlegend=False,
        )

        risk_bar.update_xaxes(
            showgrid=True,
            gridcolor="#edf2f7",
            title=None,
        )

        risk_bar.update_yaxes(
            showgrid=False,
            title=None,
        )

        st.plotly_chart(
            risk_bar,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    risk_table = (
        inventory
        .sort_values(
            ["risk_category", "inventory_risk_score"],
            ascending=[True, False],
        )
        .head(15)
        .copy()
    )

    st.markdown(
        """
        <div class="chart-title">Inventory Risk Detail</div>
        <div class="chart-subtitle">
            Highest-priority products based on ABC class, demand, and variability
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        risk_table[
            [
                "item_id",
                "abc_class",
                "avg_daily_demand",
                "demand_std",
                "inventory_risk_score",
                "risk_category",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "item_id": "Product ID",
            "abc_class": "ABC Class",
            "avg_daily_demand": st.column_config.NumberColumn(
                "Avg Daily Demand",
                format="%.2f",
            ),
            "demand_std": st.column_config.NumberColumn(
                "Demand Std.",
                format="%.2f",
            ),
            "inventory_risk_score": st.column_config.NumberColumn(
                "Risk Score",
                format="%.4f",
            ),
            "risk_category": "Risk Category",
        },
    )

    st.markdown("<br>", unsafe_allow_html=True)

    top_item = top_risk.iloc[-1]["item_id"] if not top_risk.empty else "N/A"
    top_score = (
        top_risk.iloc[-1]["inventory_risk_score"]
        if not top_risk.empty else 0
    )

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">💡 Risk Insight</div>
            <b>{top_item}</b> currently has the highest inventory-risk score
            at <b>{top_score:.4f}</b>. These signals should be considered
            alongside forecast demand before making replenishment or allocation
            decisions. The risk model is a prioritization framework, not a
            direct observation of actual stockouts.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
