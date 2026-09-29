-- ======================================
-- RetailIQ - Business KPIs
-- ======================================


-- --------------------------------------
-- 1. Overall Business KPIs
-- --------------------------------------

SELECT
    COUNT(DISTINCT item_id) AS active_products,
    COUNT(DISTINCT store_id) AS active_stores,
    COUNT(DISTINCT date) AS active_sales_days,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(
        SUM(revenue) / NULLIF(SUM(units_sold), 0),
        2
    ) AS average_revenue_per_unit
FROM fact_sales;


-- --------------------------------------
-- 2. Revenue by State
-- --------------------------------------

SELECT
    s.state_id,
    COUNT(DISTINCT f.store_id) AS stores,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(f.revenue)
        / NULLIF((SELECT SUM(revenue) FROM fact_sales), 0),
        2
    ) AS revenue_share_pct
FROM fact_sales f
JOIN dim_store s
    ON f.store_id = s.store_id
GROUP BY s.state_id
ORDER BY total_revenue DESC;


-- --------------------------------------
-- 3. Revenue by Category
-- --------------------------------------

SELECT
    p.cat_id,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(f.revenue)
        / NULLIF((SELECT SUM(revenue) FROM fact_sales), 0),
        2
    ) AS revenue_share_pct
FROM fact_sales f
JOIN dim_product p
    ON f.item_id = p.item_id
GROUP BY p.cat_id
ORDER BY total_revenue DESC;


-- --------------------------------------
-- 4. Revenue by Department
-- --------------------------------------

SELECT
    p.dept_id,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(f.revenue)
        / NULLIF((SELECT SUM(revenue) FROM fact_sales), 0),
        2
    ) AS revenue_share_pct
FROM fact_sales f
JOIN dim_product p
    ON f.item_id = p.item_id
GROUP BY p.dept_id
ORDER BY total_revenue DESC;


-- --------------------------------------
-- 5. Top 10 Products by Revenue
-- --------------------------------------

SELECT
    f.item_id,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
GROUP BY f.item_id
ORDER BY total_revenue DESC
LIMIT 10;


-- --------------------------------------
-- 6. Top 10 Products by Units Sold
-- --------------------------------------

SELECT
    item_id,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_sales
GROUP BY item_id
ORDER BY total_units_sold DESC
LIMIT 10;


-- --------------------------------------
-- 7. Store Performance
-- --------------------------------------

WITH store_daily AS (
    SELECT
        store_id,
        date,
        SUM(units_sold) AS daily_units,
        SUM(revenue) AS daily_revenue
    FROM fact_sales
    GROUP BY store_id, date
)

SELECT
    store_id,
    SUM(daily_units) AS total_units_sold,
    ROUND(SUM(daily_revenue), 2) AS total_revenue,
    ROUND(AVG(daily_revenue), 2) AS avg_daily_revenue
FROM store_daily
GROUP BY store_id
ORDER BY total_revenue DESC;


-- --------------------------------------
-- 8. Daily Sales KPIs
-- --------------------------------------

SELECT
    date,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_sales
GROUP BY date
ORDER BY date;


-- --------------------------------------
-- 9. Monthly Sales KPIs
-- --------------------------------------

SELECT
    DATE_TRUNC('month', date) AS month,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_sales
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;


-- --------------------------------------
-- 10. ABC Inventory Summary
-- --------------------------------------

SELECT
    abc_class,
    COUNT(*) AS product_count,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(avg_daily_demand), 2) AS avg_daily_demand,
    ROUND(AVG(inventory_risk_score), 3) AS avg_inventory_risk
FROM fact_inventory
GROUP BY abc_class
ORDER BY abc_class;


-- --------------------------------------
-- 11. Inventory Risk Summary
-- --------------------------------------

SELECT
    risk_category,
    COUNT(*) AS product_count,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(avg_daily_demand), 2) AS avg_daily_demand,
    ROUND(AVG(inventory_risk_score), 3) AS avg_inventory_risk
FROM fact_inventory
GROUP BY risk_category
ORDER BY
    CASE risk_category
        WHEN 'High Risk' THEN 1
        WHEN 'Medium Risk' THEN 2
        WHEN 'Low Risk' THEN 3
        ELSE 4
    END;


-- --------------------------------------
-- 12. Highest-Risk Products
-- --------------------------------------

SELECT
    item_id,
    abc_class,
    ROUND(avg_daily_demand, 2) AS avg_daily_demand,
    ROUND(demand_std, 2) AS demand_std,
    ROUND(revenue, 2) AS revenue,
    ROUND(inventory_risk_score, 3) AS inventory_risk_score,
    risk_category
FROM fact_inventory
ORDER BY inventory_risk_score DESC
LIMIT 20;


-- --------------------------------------
-- 13. Forecast Accuracy KPIs
-- --------------------------------------

SELECT
    COUNT(*) AS forecast_records,
    COUNT(DISTINCT item_id) AS forecast_products,
    COUNT(DISTINCT date) AS forecast_days,
    ROUND(AVG(ABS(actual_units - predicted_units)), 4) AS mae,
    ROUND(
        SQRT(
            AVG(
                POWER(actual_units - predicted_units, 2)
            )
        ),
        4
    ) AS rmse
FROM fact_forecast;


-- --------------------------------------
-- 14. Forecast Performance by Product
-- --------------------------------------

SELECT
    item_id,
    SUM(actual_units) AS actual_30d_units,
    ROUND(SUM(predicted_units), 2) AS predicted_30d_units,
    ROUND(
        SUM(predicted_units) - SUM(actual_units),
        2
    ) AS forecast_gap,
    ROUND(
        100.0 *
        (SUM(predicted_units) - SUM(actual_units))
        / NULLIF(SUM(actual_units), 0),
        2
    ) AS forecast_gap_pct
FROM fact_forecast
GROUP BY item_id
ORDER BY ABS(forecast_gap) DESC
LIMIT 20;


-- --------------------------------------
-- 15. Executive KPI Summary
-- --------------------------------------

WITH business AS (
    SELECT
        COUNT(DISTINCT item_id) AS active_products,
        COUNT(DISTINCT store_id) AS active_stores,
        COUNT(DISTINCT date) AS active_sales_days,
        SUM(units_sold) AS total_units_sold,
        SUM(revenue) AS total_revenue
    FROM fact_sales
),

forecast AS (
    SELECT
        ROUND(
            AVG(ABS(actual_units - predicted_units)),
            4
        ) AS forecast_mae,

        ROUND(
            SQRT(
                AVG(
                    POWER(
                        actual_units - predicted_units,
                        2
                    )
                )
            ),
            4
        ) AS forecast_rmse
    FROM fact_forecast
),

risk AS (
    SELECT
        COUNT(*) FILTER (
            WHERE risk_category = 'High Risk'
        ) AS high_risk_products
    FROM fact_inventory
)

SELECT
    business.active_products,
    business.active_stores,
    business.active_sales_days,
    business.total_units_sold,
    ROUND(business.total_revenue, 2) AS total_revenue,
    forecast.forecast_mae,
    forecast.forecast_rmse,
    risk.high_risk_products
FROM business
CROSS JOIN forecast
CROSS JOIN risk;