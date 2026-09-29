import json
import math
import re

import pandas as pd
import streamlit as st

from src.ai.groq_recommendation import generate_groq_recommendation


# --------------------------------------
# Helpers
# --------------------------------------

def html(block: str) -> str:
    """Collapse HTML to one line and escape $ so Markdown never breaks it."""
    block = re.sub(r"\s*\n\s*", " ", block).strip()
    return block.replace("$", "&#36;")


# --------------------------------------
# Decision calculations (real numbers, no AI)
# --------------------------------------

def priority_items(executive, fact_sales, selected_store, top_n=5):
    """Top products for this store, ranked by inventory risk then revenue."""

    store_sales = fact_sales[fact_sales["store_id"] == selected_store]

    item_stats = (
        store_sales.groupby("item_id")
        .agg(revenue=("revenue", "sum"), units=("units_sold", "sum"))
        .reset_index()
    )

    return (
        executive[
            ["item_id", "inventory_risk_score", "abc_class", "risk_category"]
        ]
        .drop_duplicates("item_id")
        .merge(item_stats, on="item_id")
        .sort_values(["inventory_risk_score", "revenue"], ascending=False)
        .head(top_n)
    )


def build_action_plan(
    executive,
    fact_sales,
    fact_forecast,
    selected_store,
    lead_time_days,
    review_days,
    z_score,
    on_hand,
):
    """
    Per-product replenishment numbers for the selected store.

    demand/day   = forecast units per day (scaled to the store if the
                   forecast is chain-level)
    safety stock = z * std(daily demand) * sqrt(lead time)
    reorder pt   = demand/day * lead time + safety stock
    order-up-to  = demand/day * (lead time + review days) + safety stock
    order qty    = max(order-up-to - on hand, 0)
    """

    ranked = priority_items(executive, fact_sales, selected_store)

    if ranked.empty:
        return pd.DataFrame()

    store_sales = fact_sales[fact_sales["store_id"] == selected_store]

    last_date = store_sales["date"].max()
    window_start = last_date - pd.Timedelta(days=89)
    all_days = pd.date_range(window_start, last_date)
    recent = store_sales[store_sales["date"] >= window_start]

    chain_units = fact_sales.groupby("item_id")["units_sold"].sum()

    rows = []

    for _, r in ranked.iterrows():

        item = r["item_id"]
        price = r["revenue"] / r["units"] if r["units"] else 0

        daily = (
            recent[recent["item_id"] == item]
            .groupby("date")["units_sold"]
            .sum()
            .reindex(all_days, fill_value=0)
        )

        mean_daily = float(daily.mean())
        std_daily = float(daily.std(ddof=0))

        f = fact_forecast[fact_forecast["item_id"] == item]
        scale = 1.0

        if "store_id" in f.columns:
            f = f[f["store_id"] == selected_store]
        elif chain_units.get(item, 0) > 0:
            scale = r["units"] / chain_units[item]

        n_days = f["date"].nunique()

        demand = (
            f["predicted_units"].clip(lower=0).sum() / n_days * scale
            if n_days
            else mean_daily
        )

        if demand <= 0:
            demand = mean_daily

        safety = z_score * std_daily * math.sqrt(lead_time_days)
        reorder_point = demand * lead_time_days + safety
        order_up_to = demand * (lead_time_days + review_days) + safety
        stock = on_hand.get(item, 0)

        rows.append(
            {
                "item_id": item,
                "risk_score": float(r["inventory_risk_score"]),
                "abc_class": r["abc_class"],
                "demand_per_day": demand,
                "safety_stock": safety,
                "reorder_point": reorder_point,
                "order_up_to": order_up_to,
                "on_hand": stock,
                "suggested_order": max(order_up_to - stock, 0),
                "revenue_at_risk": demand * lead_time_days * price,
            }
        )

    return pd.DataFrame(rows)


def weakest_category(fact_sales, selected_store):
    """Department where the store trails the chain-average store the most."""

    sales = fact_sales.copy()
    sales["department"] = (
        sales["item_id"].astype(str).str.rsplit("_", n=1).str[0]
    )

    dept = (
        sales.groupby(["store_id", "department"])["revenue"]
        .sum()
        .unstack(fill_value=0)
    )

    if selected_store not in dept.index:
        return None

    gap = dept.mean() - dept.loc[selected_store]
    gap = gap[gap > 0].sort_values(ascending=False)

    if gap.empty:
        return None

    name = gap.index[0]
    chain_avg = float(dept[name].mean())
    store_rev = float(dept.loc[selected_store, name])

    return {
        "department": name,
        "store_revenue_usd": round(store_rev),
        "chain_average_store_revenue_usd": round(chain_avg),
        "gap_usd": round(chain_avg - store_rev),
        "gap_pct": round((chain_avg - store_rev) / chain_avg * 100, 1),
        "recover_half_gap_usd": round((chain_avg - store_rev) / 2),
    }


@st.cache_data(show_spinner="Groq is writing the action plan...")
def cached_recommendation(pack_json: str) -> str:
    return generate_groq_recommendation(json.loads(pack_json))


# --------------------------------------
# Render
# --------------------------------------

def render(
    executive,
    fact_sales,
    fact_forecast,
    fact_inventory,
    dim_product,
    selected_store,
):

    # ---------- Store analysis ----------

    store_data = fact_sales[fact_sales["store_id"] == selected_store]
    store_revenue = store_data["revenue"].sum()

    average_store_revenue = (
        fact_sales.groupby("store_id")["revenue"].sum().mean()
    )

    revenue_gap = store_revenue - average_store_revenue

    revenue_gap_pct = (
        revenue_gap / average_store_revenue * 100
        if average_store_revenue
        else 0
    )

    if revenue_gap < 0:
        store_action = f"Revenue is {abs(revenue_gap_pct):.1f}% below the average store."
        store_label = "Store Opportunity"
    else:
        store_action = f"Revenue is {revenue_gap_pct:.1f}% above the average store."
        store_label = "Store Strength"

    # ---------- Product analysis ----------

    product_store = (
        store_data.groupby("item_id")
        .agg(revenue=("revenue", "sum"), units_sold=("units_sold", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    top_product = product_store.iloc[0]["item_id"] if not product_store.empty else "N/A"
    top_product_revenue = product_store.iloc[0]["revenue"] if not product_store.empty else 0
    top_product_units = product_store.iloc[0]["units_sold"] if not product_store.empty else 0

    # ---------- Risk analysis ----------

    risk_table = fact_inventory.sort_values("inventory_risk_score", ascending=False)

    top_risk = risk_table.iloc[0]["item_id"] if not risk_table.empty else "N/A"
    top_risk_score = risk_table.iloc[0]["inventory_risk_score"] if not risk_table.empty else 0
    top_risk_class = risk_table.iloc[0]["abc_class"] if not risk_table.empty else "N/A"

    # ---------- Section ----------

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(key="executive-container"):

        st.markdown('<div class="section-kicker">SECTION 6 OF 6</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">AI Business Recommendation 🤖</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-question">What should we consider doing?</div>', unsafe_allow_html=True)

        # ---------- Signal cards ----------

        a1, a2, a3 = st.columns(3)

        with a1:
            st.markdown(
                html(f"""
                <div class="chart-card">
                    <div class="chart-title">🎯 {store_label}</div>
                    <div class="chart-subtitle">Selected store</div>
                    <p style="color:#52677f;line-height:1.7;">
                        <b>{selected_store}</b><br>
                        Revenue: <b>${store_revenue:,.2f}</b><br>
                        Store vs average: <b>{revenue_gap_pct:+.1f}%</b><br>
                        Average store revenue: <b>${average_store_revenue:,.2f}</b>
                    </p>
                    <p style="color:#52677f;line-height:1.6;">{store_action}</p>
                </div>
                """),
                unsafe_allow_html=True,
            )

        with a2:
            st.markdown(
                html(f"""
                <div class="chart-card">
                    <div class="chart-title">📦 Product Signal</div>
                    <div class="chart-subtitle">Top revenue product</div>
                    <p style="color:#52677f;line-height:1.7;">
                        Product: <b>{top_product}</b><br>
                        Revenue: <b>${top_product_revenue:,.2f}</b><br>
                        Units sold: <b>{top_product_units:,.0f}</b><br>
                        Store: <b>{selected_store}</b>
                    </p>
                    <p style="color:#52677f;line-height:1.6;">
                        This product is a useful starting point for reviewing demand and inventory.
                    </p>
                </div>
                """),
                unsafe_allow_html=True,
            )

        with a3:
            st.markdown(
                html(f"""
                <div class="chart-card">
                    <div class="chart-title">⚠️ Risk Signal</div>
                    <div class="chart-subtitle">Highest inventory priority</div>
                    <p style="color:#52677f;line-height:1.7;">
                        Product: <b>{top_risk}</b><br>
                        Risk score: <b>{top_risk_score:.4f}</b><br>
                        ABC class: <b>{top_risk_class}</b>
                    </p>
                    <p style="color:#52677f;line-height:1.6;">
                        The risk score is a RetailIQ prioritization score, not a probability.
                    </p>
                </div>
                """),
                unsafe_allow_html=True,
            )

        # ---------- Replenishment plan ----------

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            html("""
            <div class="chart-title">Replenishment Plan</div>
            <div class="chart-subtitle">
                Calculated from the demand forecast and the last 90 days of sales
                for the selected store. Adjust the assumptions to match your supplier.
            </div>
            """),
            unsafe_allow_html=True,
        )

        items = priority_items(executive, fact_sales, selected_store)["item_id"].tolist()

        on_hand = {}

        with st.expander("Assumptions and current stock", expanded=False):

            c1, c2, c3 = st.columns(3)

            lead_time_days = c1.number_input(
                "Supplier lead time (days)", 1, 60, 7, key="ai_lead_time"
            )

            review_days = c2.number_input(
                "Days of cover to order", 1, 90, 14, key="ai_review"
            )

            service_label = c3.selectbox(
                "Service level", ["90%", "95%", "99%"], index=1, key="ai_service"
            )

            z_score = {"90%": 1.28, "95%": 1.65, "99%": 2.33}[service_label]

            st.caption(
                "Enter current stock per product if you know it. "
                "Leave at 0 to see the full order-up-to quantity."
            )

            if items:
                stock_cols = st.columns(len(items))
                for col, item in zip(stock_cols, items):
                    on_hand[item] = col.number_input(
                        f"{item} on hand",
                        min_value=0,
                        value=0,
                        step=10,
                        key=f"ai_onhand_{selected_store}_{item}",
                    )

        plan = build_action_plan(
            executive, fact_sales, fact_forecast, selected_store,
            lead_time_days, review_days, z_score, on_hand,
        )

        if plan.empty:

            st.info("No sales history found for this store.")

        else:

            display = plan.rename(
                columns={
                    "item_id": "Product",
                    "abc_class": "ABC",
                    "demand_per_day": "Forecast units/day",
                    "safety_stock": "Safety stock",
                    "reorder_point": "Reorder point",
                    "order_up_to": "Order-up-to level",
                    "suggested_order": "Suggested order",
                    "revenue_at_risk": "Revenue at risk (lead time)",
                }
            )[
                [
                    "Product",
                    "ABC",
                    "Forecast units/day",
                    "Safety stock",
                    "Reorder point",
                    "Order-up-to level",
                    "Suggested order",
                    "Revenue at risk (lead time)",
                ]
            ]

            st.dataframe(
                display,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Forecast units/day": st.column_config.NumberColumn(format="%.1f"),
                    "Safety stock": st.column_config.NumberColumn(format="%.0f"),
                    "Reorder point": st.column_config.NumberColumn(format="%.0f"),
                    "Order-up-to level": st.column_config.NumberColumn(format="%.0f"),
                    "Suggested order": st.column_config.NumberColumn(format="%.0f"),
                    "Revenue at risk (lead time)": st.column_config.NumberColumn(format="$%.0f"),
                },
            )

        # ---------- AI decision layer ----------

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            html("""
            <div class="info-box">
                <div class="info-title">🤖 Groq AI Decision Layer</div>
                <div style="color:#52677f;font-size:13px;margin-top:4px;line-height:1.6;">
                    Concrete actions written by AI from the numbers above. The AI does not calculate or invent data.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        if not plan.empty:

            pack = {
                "store": selected_store,
                "store_revenue_usd": round(float(store_revenue)),
                "average_store_revenue_usd": round(float(average_store_revenue)),
                "store_vs_average_pct": round(float(revenue_gap_pct), 1),
                "assumptions": {
                    "lead_time_days": int(lead_time_days),
                    "review_days": int(review_days),
                    "service_level": service_label,
                },
                "products": [
                    {
                        "product": r["item_id"],
                        "abc_class": r["abc_class"],
                        "risk_score": round(r["risk_score"], 4),
                        "forecast_units_per_day": round(r["demand_per_day"], 1),
                        "safety_stock": round(r["safety_stock"]),
                        "reorder_point": round(r["reorder_point"]),
                        "order_up_to": round(r["order_up_to"]),
                        "on_hand_provided": bool(r["on_hand"] > 0),
                        "on_hand": int(r["on_hand"]),
                        "suggested_order": round(r["suggested_order"]),
                        "revenue_at_risk_usd": round(r["revenue_at_risk"]),
                    }
                    for _, r in plan.iterrows()
                ],
                "weakest_category": weakest_category(fact_sales, selected_store),
            }

            try:
                recommendation = cached_recommendation(
                    json.dumps(pack, sort_keys=True)
                )
                st.markdown(recommendation.replace("$", "\\$"))

            except Exception as e:
                st.warning(f"Groq AI error: {e}")
                st.caption(
                    "The Replenishment Plan above is still valid: it is "
                    "calculated without AI."
                )

        # ---------- Decision flow ----------

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            html("""
            <div class="chart-title">Decision Flow</div>
            <div class="chart-subtitle">How RetailIQ moves from data to a business decision</div>
            """),
            unsafe_allow_html=True,
        )

        flow_items = [
            ("📊", "Data", "Sales & product history"),
            ("🔎", "Insight", "Store & product performance"),
            ("🔮", "Prediction", "Demand forecast"),
            ("⚠️", "Risk", "Inventory prioritization"),
            ("🤖", "Decision", "Groq AI recommendation"),
        ]

        for col, (icon, title, description) in zip(st.columns(5), flow_items):
            with col:
                st.markdown(
                    html(f"""
                    <div style="text-align:center;padding:15px 8px;border:1px solid #e0e8f2;border-radius:14px;background:#fbfdff;">
                        <div style="font-size:25px;">{icon}</div>
                        <div style="color:#102b4c;font-weight:800;margin-top:5px;">{title}</div>
                        <div style="color:#8a99aa;font-size:11px;margin-top:4px;">{description}</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

        # ---------- Note ----------

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            html("""
            <div class="info-box">
                <div class="info-title">ℹ️ Recommendation Note</div>
                <p style="color:#52677f;line-height:1.6;margin-bottom:0;">
                    Quantities use the forecast, the last 90 days of store sales, and the
                    assumptions you set (lead time, days of cover, service level). Stock on
                    hand, supplier minimums, pending orders and unit cost are not in the data,
                    so verify them before ordering.
                </p>
            </div>
            """),
            unsafe_allow_html=True,
        )