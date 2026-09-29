-- ======================================
-- RetailIQ - Business Analysis
-- ======================================


-- --------------------------------------
-- 1. Store Performance Ranking
-- --------------------------------------

WITH store_performance AS (
    SELECT
        store_id,
        SUM(units_sold) AS total_units_sold,
        SUM(revenue) AS total_revenue
    FROM fact_sales
    GROUP BY store_id
)

SELECT
    store_id,
    total_units_sold,
    ROUND(total_revenue, 2) AS total_revenue,
    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS revenue_rank
FROM store_performance
ORDER BY revenue_rank;


-- --------------------------------------
-- 2. Underperforming Stores
-- --------------------------------------

WITH store_revenue AS (
    SELECT
        store_id,
        SUM(revenue) AS total_revenue
    FROM fact_sales
    GROUP BY store_id
),

average_store AS (
    SELECT AVG(total_revenue) AS avg_store_revenue
    FROM store_revenue
)

SELECT
    s.store_id,
    ROUND(s.total_revenue, 2) AS total_revenue,
    ROUND(a.avg_store_revenue, 2) AS average_store_revenue,
    ROUND(
        s.total_revenue - a.avg_store_revenue,
        2
    ) AS revenue_gap,
    ROUND(
        100.0 *
        (s.total_revenue - a.avg_store_revenue)
        / NULLIF(a.avg_store_revenue, 0),
        2
    ) AS gap_pct
FROM store_revenue s
CROSS JOIN average_store a
WHERE s.total_revenue < a.avg_store_revenue
ORDER BY revenue_gap;


-- --------------------------------------
-- 3. Top Revenue Products
-- --------------------------------------

SELECT
    f.item_id,
    p.dept_id,
    p.cat_id,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.item_id = p.item_id
GROUP BY
    f.item_id,
    p.dept_id,
    p.cat_id
ORDER BY total_revenue DESC
LIMIT 20;


-- --------------------------------------
-- 4. High-Risk Products
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
WHERE risk_category = 'High Risk'
ORDER BY inventory_risk_score DESC
LIMIT 20;


-- --------------------------------------
-- 5. High-Value High-Risk Products
-- --------------------------------------

SELECT
    item_id,
    abc_class,
    ROUND(revenue, 2) AS revenue,
    ROUND(avg_daily_demand, 2) AS avg_daily_demand,
    ROUND(inventory_risk_score, 3) AS inventory_risk_score,
    risk_category
FROM fact_inventory
WHERE abc_class = 'A'
  AND risk_category = 'High Risk'
ORDER BY revenue DESC
LIMIT 20;


-- --------------------------------------
-- 6. Forecast Underestimation
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
HAVING SUM(actual_units) > 0
   AND SUM(predicted_units) < SUM(actual_units)
ORDER BY forecast_gap ASC
LIMIT 20;


-- --------------------------------------
-- 7. Forecast Overestimation
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
HAVING SUM(actual_units) > 0
   AND SUM(predicted_units) > SUM(actual_units)
ORDER BY forecast_gap DESC
LIMIT 20;


-- --------------------------------------
-- 8. Revenue Opportunity by Store
-- --------------------------------------

WITH store_revenue AS (
    SELECT
        store_id,
        SUM(revenue) AS total_revenue
    FROM fact_sales
    GROUP BY store_id
),

average_store AS (
    SELECT AVG(total_revenue) AS avg_revenue
    FROM store_revenue
)

SELECT
    s.store_id,
    ROUND(s.total_revenue, 2) AS total_revenue,
    ROUND(a.avg_revenue, 2) AS average_revenue,
    ROUND(
        a.avg_revenue - s.total_revenue,
        2
    ) AS opportunity_gap,
    CASE
        WHEN s.total_revenue < a.avg_revenue
            THEN 'Growth Opportunity'
        ELSE 'At or Above Average'
    END AS opportunity_type
FROM store_revenue s
CROSS JOIN average_store a
ORDER BY opportunity_gap DESC;


-- --------------------------------------
-- 9. Product Revenue Concentration
-- --------------------------------------

WITH product_revenue AS (
    SELECT
        item_id,
        SUM(revenue) AS revenue
    FROM fact_sales
    GROUP BY item_id
),

ranked_products AS (
    SELECT
        item_id,
        revenue,
        SUM(revenue) OVER (
            ORDER BY revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue
    FROM product_revenue
),

total AS (
    SELECT SUM(revenue) AS total_revenue
    FROM product_revenue
)

SELECT
    r.item_id,
    ROUND(r.revenue, 2) AS revenue,
    ROUND(
        100.0 * r.revenue / t.total_revenue,
        2
    ) AS revenue_share_pct,
    ROUND(
        100.0 * r.cumulative_revenue / t.total_revenue,
        2
    ) AS cumulative_revenue_pct
FROM ranked_products r
CROSS JOIN total t
ORDER BY r.revenue DESC
LIMIT 20;


-- --------------------------------------
-- 10. Store-Category Performance
-- --------------------------------------

SELECT
    f.store_id,
    p.cat_id,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(f.revenue)
        / NULLIF(
            SUM(SUM(f.revenue))
            OVER (PARTITION BY f.store_id),
            0
        ),
        2
    ) AS store_category_share_pct
FROM fact_sales f
JOIN dim_product p
    ON f.item_id = p.item_id
GROUP BY
    f.store_id,
    p.cat_id
ORDER BY
    f.store_id,
    total_revenue DESC;


-- --------------------------------------
-- 11. Inventory Risk by ABC Class
-- --------------------------------------

SELECT
    abc_class,
    risk_category,
    COUNT(*) AS product_count,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(avg_daily_demand), 2) AS avg_daily_demand,
    ROUND(AVG(inventory_risk_score), 3) AS avg_inventory_risk
FROM fact_inventory
GROUP BY
    abc_class,
    risk_category
ORDER BY
    abc_class,
    risk_category;


-- --------------------------------------
-- 12. Executive Business Opportunities
-- --------------------------------------

WITH store_revenue AS (
    SELECT
        store_id,
        SUM(revenue) AS total_revenue
    FROM fact_sales
    GROUP BY store_id
),

average_store AS (
    SELECT AVG(total_revenue) AS avg_revenue
    FROM store_revenue
),

risk_summary AS (
    SELECT
        COUNT(*) FILTER (
            WHERE risk_category = 'High Risk'
        ) AS high_risk_products,

        SUM(revenue) FILTER (
            WHERE risk_category = 'High Risk'
        ) AS high_risk_revenue
    FROM fact_inventory
),

forecast_summary AS (
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
)

SELECT
    ROUND(a.avg_revenue, 2) AS average_store_revenue,

    COUNT(
        CASE
            WHEN s.total_revenue < a.avg_revenue
            THEN 1
        END
    ) AS stores_below_average,

    ROUND(
        SUM(
            CASE
                WHEN s.total_revenue < a.avg_revenue
                THEN a.avg_revenue - s.total_revenue
                ELSE 0
            END
        ),
        2
    ) AS total_store_revenue_opportunity,

    r.high_risk_products,

    ROUND(r.high_risk_revenue, 2)
        AS high_risk_revenue,

    f.forecast_mae,
    f.forecast_rmse

FROM store_revenue s
CROSS JOIN average_store a
CROSS JOIN risk_summary r
CROSS JOIN forecast_summary f
GROUP BY
    a.avg_revenue,
    r.high_risk_products,
    r.high_risk_revenue,
    f.forecast_mae,
    f.forecast_rmse;