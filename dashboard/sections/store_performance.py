import streamlit as st
import pandas as pd
import plotly.express as px


def render(executive, fact_sales, dim_store, dim_product, selected_store):
    # Store Performance
    # --------------------------------------

    st.markdown(
        '<div class="executive-container">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-kicker">SECTION 2 OF 6</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Store Performance</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-question">Where is the opportunity?</div>',
        unsafe_allow_html=True,
    )

    store_data = fact_sales[
        fact_sales["store_id"] == selected_store
    ].copy()

    selected_revenue = store_data["revenue"].sum()
    selected_units = store_data["units_sold"].sum()

    store_summary = (
        fact_sales
        .groupby("store_id")
        .agg(
            revenue=("revenue", "sum"),
            units_sold=("units_sold", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    store_summary["rank"] = (
        store_summary["revenue"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    selected_rank = int(
        store_summary.loc[
            store_summary["store_id"] == selected_store,
            "rank",
        ].iloc[0]
    )

    average_store_revenue = store_summary["revenue"].mean()

    revenue_gap = selected_revenue - average_store_revenue

    revenue_gap_pct = (
        revenue_gap / average_store_revenue * 100
        if average_store_revenue
        else 0
    )

    state = dim_store.loc[
        dim_store["store_id"] == selected_store,
        "state_id",
    ].iloc[0]


    # Store KPIs
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-revenue">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">Store Revenue</div>
                <div class="kpi-value">${selected_revenue:,.2f}</div>
                <div class="kpi-note">{selected_store} • {state}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-units">
                <div class="kpi-icon">🛒</div>
                <div class="kpi-label">Units Sold</div>
                <div class="kpi-value">{selected_units:,.0f}</div>
                <div class="kpi-note">Total units at this store</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-products">
                <div class="kpi-icon">🏆</div>
                <div class="kpi-label">Revenue Rank</div>
                <div class="kpi-value">#{selected_rank}</div>
                <div class="kpi-note">Out of {len(store_summary)} stores</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    gap_class = "kpi-revenue" if revenue_gap >= 0 else "kpi-risk"
    gap_color = "#16834d" if revenue_gap >= 0 else "#d33147"
    gap_sign = "+" if revenue_gap >= 0 else ""

    with k4:
        st.markdown(
            f"""
            <div class="kpi-card {gap_class}">
                <div class="kpi-icon">📊</div>
                <div class="kpi-label">Vs Store Average</div>
                <div class="kpi-value" style="color:{gap_color};">
                    {gap_sign}{revenue_gap_pct:.1f}%
                </div>
                <div class="kpi-note">Revenue difference</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)


    # Store comparison
    chart_left, chart_right = st.columns(2)

    with chart_left:

        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Store Comparison</div>
                <div class="chart-subtitle">
                    Revenue performance across all stores
                </div>
            """,
            unsafe_allow_html=True,
        )

        comparison_chart = px.bar(
            store_summary.sort_values("revenue"),
            x="revenue",
            y="store_id",
            orientation="h",
        )

        comparison_chart.update_traces(marker_line_width=0)

        comparison_chart.update_layout(
            height=380,
            margin=dict(l=10, r=25, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
            showlegend=False,
        )

        comparison_chart.update_xaxes(
            showgrid=True,
            gridcolor="#edf2f7",
            title=None,
            tickprefix="$",
            tickformat=",.0f",
        )

        comparison_chart.update_yaxes(
            title=None,
            showgrid=False,
        )

        st.plotly_chart(
            comparison_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)


    with chart_right:

        category_summary = (
            store_data
            .merge(
                dim_product[["item_id", "cat_id"]],
                on="item_id",
                how="left",
            )
            .groupby("cat_id")
            .agg(
                revenue=("revenue", "sum"),
                units_sold=("units_sold", "sum"),
            )
            .reset_index()
            .sort_values("revenue", ascending=False)
        )

        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Category Performance</div>
                <div class="chart-subtitle">
                    Revenue contribution within the selected store
                </div>
            """,
            unsafe_allow_html=True,
        )

        category_chart = px.pie(
            category_summary,
            names="cat_id",
            values="revenue",
            hole=0.55,
        )

        category_chart.update_traces(
            textposition="inside",
            textinfo="percent",
        )

        category_chart.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#60758d"),
        )

        st.plotly_chart(
            category_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    # Opportunity gap
    if revenue_gap < 0:
        opportunity_value = f"-${abs(revenue_gap):,.2f}"
        opportunity_color = "#d33147"
        opportunity_message = (
            f"{selected_store} is {abs(revenue_gap_pct):.1f}% below the "
            f"average store revenue of ${average_store_revenue:,.2f}. "
            "Investigate product mix, demand, and inventory allocation "
            "to understand the performance gap."
        )
    else:
        opportunity_value = f"+${revenue_gap:,.2f}"
        opportunity_color = "#16834d"
        opportunity_message = (
            f"{selected_store} is {revenue_gap_pct:.1f}% above the "
            f"average store revenue of ${average_store_revenue:,.2f}. "
            "Identify the products and demand patterns supporting this performance."
        )

    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">🎯 Opportunity Gap</div>
            <div style="
                font-size:24px;
                font-weight:800;
                color:{opportunity_color};
                margin:5px 0;
            ">
                {opportunity_value}
            </div>
            {opportunity_message}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)


    # Store detail
    st.markdown(
        """
        <div class="chart-title">Store Performance Detail</div>
        <div class="chart-subtitle">
            Revenue and unit performance across all locations
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_store = store_summary[
        ["rank", "store_id", "units_sold", "revenue"]
    ].copy()

    st.dataframe(
        display_store,
        use_container_width=True,
        hide_index=True,
        column_config={
            "rank": "#",
            "store_id": "Store",
            "units_sold": "Units Sold",
            "revenue": st.column_config.NumberColumn(
                "Revenue",
                format="$%,.2f",
            ),
        },
    )

    st.markdown("</div>", unsafe_allow_html=True)


    # --------------------------------------
