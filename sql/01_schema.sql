-- ======================================
-- RetailIQ Database Schema
-- ======================================

-- --------------------------------------
-- Product Dimension
-- --------------------------------------

CREATE TABLE IF NOT EXISTS dim_product (
    item_id VARCHAR PRIMARY KEY,
    dept_id VARCHAR,
    cat_id VARCHAR
);


-- --------------------------------------
-- Store Dimension
-- --------------------------------------

CREATE TABLE IF NOT EXISTS dim_store (
    store_id VARCHAR PRIMARY KEY,
    state_id VARCHAR
);


-- --------------------------------------
-- Date Dimension
-- --------------------------------------

CREATE TABLE IF NOT EXISTS dim_date (
    date DATE PRIMARY KEY,
    wm_yr_wk INTEGER,
    weekday VARCHAR,
    event_name_1 VARCHAR,
    event_type_1 VARCHAR,
    event_name_2 VARCHAR,
    event_type_2 VARCHAR,
    snap_CA INTEGER,
    snap_TX INTEGER,
    snap_WI INTEGER
);


-- --------------------------------------
-- Price Dimension
-- --------------------------------------

CREATE TABLE IF NOT EXISTS dim_price (
    store_id VARCHAR,
    item_id VARCHAR,
    wm_yr_wk INTEGER,
    sell_price DOUBLE
);


-- --------------------------------------
-- Sales Fact Table
-- --------------------------------------

CREATE TABLE IF NOT EXISTS fact_sales (
    item_id VARCHAR,
    store_id VARCHAR,
    date DATE,
    wm_yr_wk INTEGER,
    units_sold INTEGER,
    sell_price DOUBLE,
    revenue DOUBLE
);


-- --------------------------------------
-- Forecast Fact Table
-- --------------------------------------

CREATE TABLE IF NOT EXISTS fact_forecast (
    item_id VARCHAR,
    date DATE,
    actual_units INTEGER,
    predicted_units DOUBLE
);


-- --------------------------------------
-- Inventory Fact Table
-- --------------------------------------

CREATE TABLE IF NOT EXISTS fact_inventory (
    item_id VARCHAR,
    abc_class VARCHAR,
    avg_daily_demand DOUBLE,
    demand_std DOUBLE,
    revenue DOUBLE,
    inventory_risk_score DOUBLE,
    risk_category VARCHAR
);


-- --------------------------------------
-- Executive Decision Table
-- --------------------------------------

CREATE TABLE IF NOT EXISTS executive_decision (
    item_id VARCHAR PRIMARY KEY,
    abc_class VARCHAR,
    avg_daily_demand DOUBLE,
    demand_std DOUBLE,
    revenue DOUBLE,
    inventory_risk_score DOUBLE,
    risk_category VARCHAR,
    actual_30d_units INTEGER,
    predicted_30d_units DOUBLE,
    forecast_gap DOUBLE,
    forecast_gap_pct DOUBLE
);