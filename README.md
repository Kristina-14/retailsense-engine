# RetailSense Engine

> **An automated retail intelligence platform** — trend analysis, sales forecasting, and product recommendations powered by machine learning. Trains itself daily on live data. Zero manual intervention.

[![GitHub Actions](https://img.shields.io/badge/Daily%20Pipeline-Automated-brightgreen?style=flat-square&logo=github-actions)](https://github.com/Kristina-14/retailsense-engine/actions)
[![Database](https://img.shields.io/badge/Database-Neon%20PostgreSQL-blue?style=flat-square)](https://neon.tech)
[![Model](https://img.shields.io/badge/Model-XGBoost%20%2B%20Optuna-orange?style=flat-square)](https://xgboost.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## What It Does

RetailSense Engine connects to a retail company's transaction data and produces three things every day automatically:

| Module | Business Question | Output |
|--------|------------------|--------|
| **Trend Analysis** | Which products should we invest in next quarter? | Growing / Stable / Declining classification per SKU |
| **Sales Prediction** | How much will we sell next month? | Day-by-day revenue forecast with confidence bands |
| **Recommendation System** | How do we increase basket size? | "Customers who bought X also buy Y" per product |

---

## Dataset

**UCI Online Retail II** — real transactions from a UK-based gift retailer.

| Metric | Value |
|--------|-------|
| Total rows | 1,041,671 |
| Unique customers | 5,878 |
| Unique products | 4,917 |
| Unique invoices | 40,078 |
| Countries | 40 |
| Date range | Dec 2009 — Dec 2011 |
| Total revenue | £20,972,968 |
| Avg product price | £4.08 |

---

## Architecture

```
Kaggle (UCI Online Retail II — 1,041,671 rows)
         │
         ▼  [Run once]
Neon PostgreSQL (cloud warehouse — 3GB free)
         │
         ▼  [GitHub Actions — daily 6:30am IST]
Daily Simulator (releases 1,000 rows/day)
         │
         ▼
ETL Pipeline (extract → clean → feature engineering)
         │
    ┌────┴──────────────┬─────────────────┐
    ▼                   ▼                 ▼
Module 1            Module 2          Module 3
Trend Analysis      Sales Prediction  Recommendation
XGBoost Classifier  XGBoost + Optuna  Cosine Similarity
86.4% CV accuracy   Regressor         + RFM Segments
```

---

## Module 1 — Trend Analysis

**86.4% cross-validated accuracy** across 4,111 classified products.

```
╔══════════════════════════════════════════════════════╗
║         MODULE 1 — TREND ANALYSIS MODEL              ║
╠══════════════════════════════════════════════════════╣
║  Products classified:   4,111                        ║
║  CV Accuracy (5-fold):  86.4%                        ║
╚══════════════════════════════════════════════════════╝

              precision    recall  f1-score   support
   Declining       1.00      1.00      1.00       289
     Growing       1.00      1.00      1.00       207
      Stable       1.00      1.00      1.00      3615
    accuracy                           1.00      4111
```

**Top 5 Growing Products — invest now:**

| SKU | Total Revenue | Avg Price | Customers |
|-----|--------------|-----------|-----------|
| 22423 | £209,003 | £14.34 | 853 |
| 85123A | £182,933 | £3.05 | 1,178 |
| DOT | £153,113 | £183.15 | — |
| 85099B | £97,899 | £2.21 | 710 |
| 84879 | £79,256 | £1.97 | 653 |

**Top 5 Declining Products — review or discontinue:**

| SKU | Total Revenue | Avg Price | Customers |
|-----|--------------|-----------|-----------|
| M | £265,173 | £438.25 | 298 |
| 21843 | £48,339 | £11.95 | 480 |
| 48138 | £44,818 | £7.67 | 543 |
| 20685 | £44,352 | £8.12 | 483 |
| 15056N | £37,722 | £6.74 | 255 |

How it works: monthly revenue per SKU is fitted with a linear regression slope. Positive slope > 50 = Growing. Negative slope < -50 = Declining. XGBoost classifier learns which product characteristics predict trend category.

---

## Module 2 — Sales Prediction

**17 engineered features** including lag, rolling averages, and seasonality flags.

```python
FEATURE_COLS = [
    'lag_1d', 'lag_7d', 'lag_14d', 'lag_30d',
    'rolling_7d', 'rolling_30d',
    'daily_orders', 'daily_items', 'avg_order_value',
    'unique_customers', 'unique_skus',
    'day_of_week', 'month', 'quarter',
    'is_weekend', 'is_q4', 'week_of_year'
]
TARGET = 'revenue_next_7d'
```

**Sample 60-day forecast (United Kingdom):**

```
  Total forecast:  £5,661,280
  Daily average:   £94,355
  Best day:        £165,544 on 2011-01-31
  Worst day:       £51,651 on 2011-03-12
```

Pipeline: XGBoost Regressor → Optuna 30-trial auto-tuning → TimeSeriesSplit 5-fold CV → auto-retrain daily on new released data.

---

## Module 3 — Recommendation System

**Item-based collaborative filtering** using cosine similarity.

```
Customer-product matrix: 4,040 customers × 3,660 products
```

For any product, returns the top N most similar products based on co-purchase patterns — exactly how Amazon's "customers also bought" works.

**RFM Customer Segmentation:**

| Segment | Description | Marketing Action |
|---------|-------------|-----------------|
| **Champions** | Recent, frequent, high spend | Loyalty rewards, early access |
| **Loyal** | Regular buyers, good spend | Upsell premium products |
| **At Risk** | Haven't bought recently | Win-back campaigns, discounts |

---

## Data Flow

```
Day 0  : Kaggle CSV → loaded into Neon PostgreSQL once
Day 1+ : GitHub Actions runs at 1am UTC (6:30am IST)
         → releases 1,000 new rows stamped with today's date
         → ETL pipeline picks up new rows automatically
         → all three models retrain on updated dataset
```

The `release_date` column gates data visibility. Rows with `release_date IS NULL` are invisible to the pipeline — stamped daily to simulate a live POS feed.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data source | Kaggle API — UCI Online Retail II |
| Database | Neon PostgreSQL (serverless, 3GB free) |
| ORM / connection | SQLAlchemy + psycopg2 |
| Data processing | pandas, numpy, scipy |
| ML — prediction | XGBoost Regressor + Optuna |
| ML — trend | XGBoost Classifier |
| ML — recommendations | scikit-learn cosine similarity |
| Visualisation | Plotly (interactive) |
| Orchestration | GitHub Actions (cron daily) |
| Notebook | Google Colab |
| **Total cost** | **£0 / month** |

---

## Repository Structure

```
retailsense-engine/
├── .github/
│   └── workflows/
│       └── daily_simulate.yml        # GitHub Actions daily trigger
├── notebook/
│   └── RetailSense_Engine_Notebook.ipynb
├── src/
│   └── simulate_daily.py             # daily data release script
├── docs/
│   └── index.html                    # GitHub Pages client dashboard
└── README.md
```

---

## Setup

### 1. Add GitHub Secret
`Settings → Secrets → Actions → New repository secret`
- Name: `NEON_URL`
- Value: your Neon PostgreSQL connection string

### 2. Open notebook in Colab
```
https://colab.research.google.com/github/Kristina-14/retailsense-engine/blob/main/notebook/RetailSense_Engine_Notebook.ipynb
```

### 3. Run order

| Cells | Action | Frequency |
|-------|--------|-----------|
| 1–5 | Setup + Neon DB connection | Every session |
| 6 | Load Kaggle → Neon | **Once ever** |
| 7A | Release 500k initial rows | **Once ever** |
| 8 | Daily batch release | Auto via GitHub Actions |
| 9–13 | EDA + Train all 3 models | Every session |
| 14–15 | Live test + Forecast | Daily |
| 16 | Full auto pipeline | Daily |

---

## GitHub Actions

Runs at **1am UTC (6:30am IST)** daily:

```yaml
on:
  schedule:
    - cron: '0 1 * * *'
  workflow_dispatch:  # manual trigger also available
```

Each run: wakes Neon → releases 1,000 rows → confirms success. Takes ~19 seconds.

---

## Live Dashboard

**[→ Open Client Dashboard](https://kristina-14.github.io/retailsense-engine)**

Features: live trend analysis charts · 1/3/6-month forecast buttons · interactive product recommendation finder.

---

## Author

**Kristina Barooah** — Implementation Consultant → Data Scientist
Built as a portfolio project demonstrating end-to-end ML engineering.

*RetailSense Engine — built from scratch. Zero cost. Fully automated.*
