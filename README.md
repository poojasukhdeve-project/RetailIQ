# RetailIQ — AI-Powered Retail Analytics & Inventory Intelligence

RetailIQ is an end-to-end retail analytics application that transforms historical Walmart sales data into business insights, demand forecasts, inventory-risk signals, and actionable recommendations. It combines Python analytics, SQL/DuckDB, machine learning, and a Streamlit dashboard, with an optional Groq-powered AI explanation layer.

**Live dashboard:** https://retailiq-hnxcr5qvazmbq45nbq9bar.streamlit.app/

**GitHub repository:** https://github.com/poojasukhdeve-project/RetailIQ

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Dataset and Scope](#dataset-and-scope)
- [Key Results](#key-results)
- [Forecasting Results](#forecasting-results)
- [Project Structure](#project-structure)
- [Run Locally](#run-locally)
- [Groq AI Configuration](#groq-ai-configuration)
- [How It Works](#how-it-works)
- [Challenges Faced](#challenges-faced)
- [Key Learnings](#key-learnings)
- [Limitations and Assumptions](#limitations-and-assumptions)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Overview

RetailIQ helps retail teams understand what sells, where sales are strongest, which products contribute most to revenue, and where inventory decisions deserve attention.

The dashboard follows a decision-oriented workflow:

**Data → Insights → Prediction → Risk → Recommendation → Decision**

It contains six sections:

1. **Executive Overview** — headline KPIs and overall performance.
2. **Store Performance** — compare sales across stores and states.
3. **Product & Sales Intelligence** — explore products, categories, departments, and sales patterns.
4. **Demand Forecast** — evaluate demand forecasting models.
5. **Inventory & Risk Intelligence** — highlight products that may need inventory review.
6. **AI Business Recommendation** — translate computed metrics and structured recommendations into plain-language guidance.

---

## Key Features

- Executive KPIs for revenue, units sold, store coverage, and product coverage.
- Store, state, category, department, and product performance analysis.
- ABC product classification based on cumulative revenue contribution.
- Time-series feature engineering with calendar variables, lagged sales, and rolling averages.
- Comparison of a naïve baseline, Random Forest, XGBoost, and LightGBM.
- Inventory and replenishment signals based on available sales and forecast data.
- Optional Groq-powered explanations of calculated business results.
- SQL-oriented analytics and DuckDB support.
- Modular Streamlit dashboard sections.

---

## Technology Stack

| Area | Tools |
|---|---|
| Language | Python |
| Data processing | pandas, NumPy |
| SQL / database | SQL, DuckDB |
| Dashboard and visualization | Streamlit, Plotly, Matplotlib, Seaborn |
| Machine learning | scikit-learn, XGBoost, LightGBM |
| AI explanation layer | Groq API (optional) |
| Data formats | CSV, Parquet |
| Version control and deployment | Git, GitHub, Streamlit Community Cloud |

See `requirements.txt` for the project's Python dependencies.

---

## Dataset and Scope

RetailIQ uses the **M5 Forecasting – Accuracy** retail sales dataset, containing Walmart product-store sales history, calendar information, and selling prices.

- **Dataset:** M5 Forecasting – Accuracy on Kaggle
- **Analysis window:** approximately April 26, 2015 – April 24, 2016
- **Stores analyzed:** 10
- **Product-store rows:** 30,490
- **Long-format sales records:** 11,128,850

Original M5 files may need to be downloaded separately from Kaggle. The dashboard uses prepared files in `data/processed/`.

---

## Key Results

Results from the prepared historical analysis:

| Metric | Result |
|---|---|
| Total units sold | 14,389,130 |
| Total revenue | $44,484,265.12 |
| Active stores | 10 |
| Historical sales days | 365 |
| Product-store rows | 30,490 |
| Long-format sales records | 11,128,850 |

### Revenue and product mix

- **Category revenue:** Foods approximately $24.68M; Household $13.74M; Hobbies $6.07M.
- **State revenue:** California approximately $19.80M; Texas $12.55M; Wisconsin $12.13M.
- **ABC classification:** Class A included 1,315 products and approximately 80% of revenue; Class B included 942 products and approximately 15%; Class C included 792 products and approximately 5%.

Values are rounded where appropriate and describe the prepared historical dataset, not live retail performance.

---

## Forecasting Results

The feature engineering workflow uses day of week, month, week of year, lagged sales at 1, 7, and 28 time steps, and rolling averages over 7 and 28 time steps.

Models were evaluated chronologically on a 30-day historical holdout from March 26, 2016 through April 24, 2016.

| Model | MAE | RMSE |
|---|---|---|
| Naïve baseline | 5.0627 | 10.1490 |
| Random Forest Regressor | 3.7537 | 7.1845 |
| XGBoost Regressor | 3.9227 | 9.7284 |
| LightGBM Regressor | ~3.757 | ~7.066 |

Lower values indicate less error on this holdout. LightGBM achieved the lowest RMSE, while Random Forest achieved a slightly lower MAE. The most appropriate model depends on the business cost of different forecasting errors.

> **Important:** This is a historical evaluation using 2015–2016 data, not a prediction of current or future 2026 sales. Historical performance does not guarantee future accuracy.

---

## Project Structure

```
RetailIQ/
├── data/
│   ├── raw/                         # Original source data; may need separate download
│   └── processed/                   # Prepared datasets used by the dashboard
├── notebooks/
│   └── 01_data_exploration.ipynb
├── src/
│   ├── analytics/
│   │   ├── sales.py
│   │   └── profitability.py
│   ├── forecasting/
│   │   └── demand_forecast.py
│   ├── ml/
│   │   └── risk_model.py
│   └── recommendations/
│       └── inventory.py
├── sql/
│   ├── 01_schema.sql
│   ├── 02_cleaning.sql
│   ├── 03_kpis.sql
│   └── 04_business_analysis.sql
├── dashboard/
│   ├── app.py
│   └── sections/
│       ├── __init__.py
│       ├── executive_overview.py
│       ├── store_performance.py
│       ├── product_sales_intelligence.py
│       ├── demand_forecast.py
│       ├── inventory_risk.py
│       └── ai_business_recommendation.py
├── requirements.txt
└── README.md
```

The dashboard requires the processed files referenced by its data-loading code. Some generated or local files may not be present in every clone.

---

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/poojasukhdeve-project/RetailIQ.git
cd RetailIQ
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Check the processed data

Confirm that the files expected by `dashboard/app.py` exist in `data/processed/`, including:

- `fact_sales_optimized.parquet`
- `fact_forecast.parquet`
- `fact_inventory.csv`
- `dim_store.csv`
- `dim_product.csv`
- `executive_decision.csv`

If these files are missing, prepare them from the M5 source data using the project's data-processing workflow before starting the dashboard.

### 5. Launch the app

From the repository root:

```bash
streamlit run dashboard/app.py
```

Open the local URL printed in the terminal.

---

## Groq AI Configuration

The AI recommendation section can use Groq to generate a plain-language explanation of computed business results. The language model is an **explanation layer**; sales totals and model metrics are calculated by the analytics workflow.

For local development, create `.streamlit/secrets.toml` in the project root:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

Keep this file private and never commit API keys to GitHub. Ensure `.streamlit/secrets.toml` is excluded by `.gitignore`.

For Streamlit Community Cloud, configure `GROQ_API_KEY` in the app's **Secrets** settings rather than hard-coding it in Python. AI explanations may be unavailable if no key is configured, depending on the app's fallback behavior.

---

## How It Works

1. **Prepare data:** transform sales, calendar, and price information into analysis-ready tables.
2. **Analyze performance:** calculate KPIs and aggregate results by store, product, category, and time.
3. **Evaluate forecasts:** engineer historical features and compare candidate models on a chronological holdout.
4. **Assess inventory:** combine available sales and forecast signals to highlight products for review.
5. **Explain results:** optionally use an LLM to turn structured findings into readable business recommendations.
6. **Support decisions:** present the analysis and recommendations in the Streamlit dashboard.

---

## Challenges Faced

### 1. Working with a large, wide dataset
The M5 data arrives in a wide format (one column per day) and expands to **11,128,850 long-format records** once reshaped. Loading and transforming this in plain pandas CSV workflows was slow and memory-heavy.
**How it was handled:** converted the data to long format once, stored the result as **Parquet** (`fact_sales_optimized.parquet`) for fast, compact reads, and used **DuckDB/SQL** for heavy aggregations instead of repeatedly scanning data in pandas.

### 2. Avoiding data leakage in time-series evaluation
A random train/test split would let the model "see the future" through lag and rolling features, making results look better than they really are.
**How it was handled:** used a **chronological 30-day holdout** (March 26 – April 24, 2016) and built lag (1, 7, 28) and rolling (7, 28) features only from past values.

### 3. Comparing models fairly when metrics disagree
Random Forest had the lowest MAE (3.7537), while LightGBM had the lowest RMSE (~7.066). XGBoost had a competitive MAE but a much worse RMSE (9.7284), suggesting larger errors on high-demand days.
**How it was handled:** reported both metrics instead of declaring a single "winner," and noted that the best model depends on the business cost of different error types (e.g., large misses vs. average error).

### 4. Making inventory risk honest without stockout labels
The dataset records sales, not stockouts, so there are no defensible "stockout" labels to train or validate a true stockout classifier.
**How it was handled:** framed the outputs as **risk signals for review** based on sales and forecast data, and explicitly documented that they are not validated stockout probabilities.

### 5. Profitability without real cost data
M5 has selling prices but no actual cost of goods sold, so true profit cannot be computed.
**How it was handled:** used a clearly labeled **70% COGS assumption** and flagged any profitability output as an estimate.

### 6. Using an LLM without letting it invent numbers
Language models can produce fluent but incorrect statements, which is risky in a business-decision context.
**How it was handled:** kept all KPIs and model metrics in the analytics pipeline and used Groq only as an **explanation layer** over already-computed results. The README and dashboard advise verifying AI output against calculated metrics.

### 7. Deployment and secrets management
The app needed to run both locally and on Streamlit Community Cloud, with an API key that must never be committed to GitHub.
**How it was handled:** used `.streamlit/secrets.toml` locally (excluded via `.gitignore`) and the Streamlit Cloud **Secrets** settings in production, with the AI section designed to degrade gracefully if no key is available.

### 8. Reproducibility across clones
Raw M5 files are large and are not stored in the repository, so a fresh clone may be missing the processed files the dashboard expects.
**How it was handled:** documented the required files in `data/processed/` and added a "check the processed data" step to the setup instructions.

---

## Key Learnings

- **Start with a baseline.** The naïve baseline (MAE 5.0627) made it clear how much value the ML models actually added; every model was judged against it.
- **Validation design matters as much as model choice.** Chronological splitting and leakage-aware feature engineering had a bigger impact on trustworthy results than tuning algorithms.
- **No single metric tells the whole story.** MAE and RMSE ranked the models differently; understanding *why* connects model evaluation to business cost.
- **Data format is a performance decision.** Moving from wide CSV to long-format Parquet with DuckDB made an 11M-row analysis practical for an interactive dashboard.
- **Be explicit about assumptions.** Labeling the 70% COGS ratio and the limits of the risk signals builds more credibility than presenting unsupported precision.
- **LLMs work best as translators, not calculators.** Separating computation (Python/SQL) from explanation (Groq) keeps the numbers reliable and the language accessible.
- **Think in decisions, not charts.** Structuring the dashboard as Data → Insights → Prediction → Risk → Recommendation → Decision keeps every section tied to an action a retail team could take.
- **Modular code pays off.** Splitting the dashboard into section modules and the logic into `analytics`, `forecasting`, `ml`, and `recommendations` made the project easier to debug, extend, and explain.
- **Ship responsibly.** Handling secrets properly, documenting limitations, and making setup reproducible are part of building a real application, not afterthoughts.

---

## Limitations and Assumptions

- **Historical data:** the model evaluation uses data from 2015–2016 and should not be interpreted as a current forecast.
- **Profitability:** where profitability is estimated, a 70% cost-of-goods-sold ratio is an assumption, not actual retailer cost data. Such outputs should be labeled as estimates.
- **Inventory risk:** a reliable stockout classifier requires defensible stockout labels. Risk signals should not be interpreted as validated stockout probabilities unless suitable labels and validation are added.
- **Forecast scope:** holdout performance does not establish performance for every store-product combination or future time horizon.
- **AI output:** LLM-generated explanations can be incomplete or incorrect. Verify recommendations against calculated metrics and operational context.

---

## Future Improvements

- Evaluate genuine future 7-day and 30-day forecasts from a clearly defined forecasting origin.
- Expand and validate store-product-level forecasting.
- Backtest across multiple time windows and forecast horizons.
- Validate inventory-risk labels against real stockout or replenishment outcomes.
- Incorporate actual cost, margin, supplier lead-time, and replenishment data where available.
- Add automated tests and data-quality checks to deployment.

---

## Author

**Pooja Sukhdeve**

- GitHub: [poojasukhdeve-project](https://github.com/poojasukhdeve-project)
- Portfolio: Pooja Sukhdeve Portfolio

*RetailIQ is a portfolio and analytical decision-support project. Findings depend on the available historical dataset and stated assumptions; they are not live operational data or financial guarantees.*
