-- SQL data cleaning transformations will be added here.
-- ======================================
-- RetailIQ - Data Quality & Cleaning
-- ======================================


-- --------------------------------------
-- 1. Check Duplicate Products
-- --------------------------------------

SELECT
    item_id,
    COUNT(*) AS duplicate_count
FROM dim_product
GROUP BY item_id
HAVING COUNT(*) > 1;


-- --------------------------------------
-- 2. Check Duplicate Stores
-- --------------------------------------

SELECT
    store_id,
    COUNT(*) AS duplicate_count
FROM dim_store
GROUP BY store_id
HAVING COUNT(*) > 1;


-- --------------------------------------
-- 3. Check Duplicate Dates
-- --------------------------------------

SELECT
    date,
    COUNT(*) AS duplicate_count
FROM dim_date
GROUP BY date
HAVING COUNT(*) > 1;


-- --------------------------------------
-- 4. Check Missing Product Information
-- --------------------------------------

SELECT
    COUNT(*) AS missing_product_fields
FROM dim_product
WHERE item_id IS NULL
   OR dept_id IS NULL
   OR cat_id IS NULL;


-- --------------------------------------
-- 5. Check Missing Store Information
-- --------------------------------------

SELECT
    COUNT(*) AS missing_store_fields
FROM dim_store
WHERE store_id IS NULL
   OR state_id IS NULL;


-- --------------------------------------
-- 6. Check Missing Sales Values
-- --------------------------------------

SELECT
    COUNT(*) AS missing_sales_values
FROM fact_sales
WHERE item_id IS NULL
   OR store_id IS NULL
   OR date IS NULL
   OR units_sold IS NULL
   OR revenue IS NULL;


-- --------------------------------------
-- 7. Check Negative Sales
-- --------------------------------------

SELECT
    COUNT(*) AS negative_sales_records
FROM fact_sales
WHERE units_sold < 0
   OR revenue < 0;


-- --------------------------------------
-- 8. Check Negative Prices
-- --------------------------------------

SELECT
    COUNT(*) AS negative_price_records
FROM dim_price
WHERE sell_price < 0;


-- --------------------------------------
-- 9. Check Missing Forecast Values
-- --------------------------------------

SELECT
    COUNT(*) AS missing_forecast_values
FROM fact_forecast
WHERE item_id IS NULL
   OR date IS NULL
   OR actual_units IS NULL
   OR predicted_units IS NULL;


-- --------------------------------------
-- 10. Check Negative Forecast Predictions
-- --------------------------------------

SELECT
    COUNT(*) AS negative_forecast_predictions
FROM fact_forecast
WHERE predicted_units < 0;


-- --------------------------------------
-- 11. Check Inventory Risk Values
-- --------------------------------------

SELECT
    COUNT(*) AS invalid_inventory_risk
FROM fact_inventory
WHERE inventory_risk_score IS NULL
   OR inventory_risk_score < 0;


-- --------------------------------------
-- 12. Overall Sales Quality Summary
-- --------------------------------------

SELECT
    COUNT(*) AS total_sales_records,
    COUNT(DISTINCT item_id) AS unique_products,
    COUNT(DISTINCT store_id) AS unique_stores,
    COUNT(DISTINCT date) AS sales_days,
    SUM(units_sold) AS total_units,
    SUM(revenue) AS total_revenue
FROM fact_sales;


-- --------------------------------------
-- 13. Overall Forecast Quality Summary
-- --------------------------------------

SELECT
    COUNT(*) AS forecast_records,
    COUNT(DISTINCT item_id) AS forecast_products,
    COUNT(DISTINCT date) AS forecast_days,
    SUM(actual_units) AS actual_units,
    SUM(predicted_units) AS predicted_units
FROM fact_forecast;


-- --------------------------------------
-- Cleaning Checks Completed
-- --------------------------------------