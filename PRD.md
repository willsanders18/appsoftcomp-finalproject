# PRD: MAANG Stock vs Internet Usage Correlation Analysis

## Overview
A Jupyter notebook that performs correlation analysis between MAANG company stock data (price, volume, volatility) and internet usage trends. The analysis uses historical stock market data and Google Trends internet usage data, cleaning and aligning them to identify correlations.

---

## Task 1: Data Loading and Exploration
- **Goal:** Load raw stock and internet usage data from CSV files and perform initial exploration
- **Inputs:** 
  - `data/raw/company_stock_data/{Apple,Amazon,Google,Microsoft,Netflix}.csv`
  - `data/raw/company_trend_data/multiTimeline.csv`
- **Outputs:** Loaded DataFrames ready for cleaning
- **Specification 1:** Load all 5 stock CSV files with proper date parsing
- **Specification 2:** Load internet usage data and identify data types/columns

---

## Task 0: Data Cleaning Script
- **Goal:** Create standalone script to clean and preprocess all raw data
- **Inputs:** Same as Task 1 (raw CSV files)
- **Outputs:** Cleaned CSVs in `data/cleaned/` folder
- **Specification 1:** Handle "<1" values, missing data, duplicates, date standardization
- **Specification 2:** Save individual cleaned stock files, cleaned trend data, monthly aggregated stocks, and combined analysis dataset

---

## Task 2: Data Cleaning
- **Goal:** Clean and standardize both datasets to prevent errors in analysis/visualization
- **Inputs:** Raw DataFrames from Task 1
- **Outputs:** Cleaned DataFrames saved to `data/cleaned/`
- **Specification 1:** Handle "<1" values in internet usage data (convert to numeric)
- **Specification 2:** Standardize date formats, handle missing values, remove duplicates
- **Specification 3:** Save merged stock data and cleaned internet usage data as CSVs

---

## Task 3: Data Alignment and Aggregation
- **Goal:** Align datasets to overlapping time period and aggregate to monthly frequency
- **Inputs:** Cleaned DataFrames from Task 2
- **Outputs:** Aligned monthly DataFrames for analysis
- **Specification 1:** Filter to overlapping period (2004-08 onwards)
- **Specification 2:** Aggregate daily stock data to monthly (mean for prices, sum for volume)
- **Specification 3:** Calculate monthly volatility using 30-day rolling std of log returns

---

## Task 4: Correlation Analysis
- **Goal:** Calculate Pearson and Spearman correlation coefficients
- **Inputs:** Aligned monthly DataFrames from Task 3
- **Outputs:** Correlation matrices and statistical results
- **Specification 1:** Calculate Pearson correlation between internet usage and stock metrics
- **Specification 2:** Calculate Spearman correlation for rank-based relationships
- **Specification 3:** Generate correlation summary tables

---

## Task 5: Data Visualization
- **Goal:** Create comprehensive visualizations of correlations and trends
- **Inputs:** Correlation results and aligned data from Tasks 3-4
- **Outputs:** Charts embedded in notebook
- **Specification 1:** Time series plots showing stock metrics vs internet usage over time
- **Specification 2:** Correlation heatmaps for all MAANG companies
- **Specification 3:** Scatter plots with regression lines
- **Specification 4:** Rolling correlation plots showing correlation changes over time

---

## MVP Status: COMPLETE

**Analysis Period:** 2004-10 to 2023-03 (222 months)

**Key Findings:**
- Netflix shows strongest price-internet correlation (Pearson: 0.88, Spearman: 0.97)
- Amazon also shows strong positive price correlation (Pearson: 0.78, Spearman: 0.93)
- Microsoft shows negative price correlation but positive volume correlation
- All companies show statistically significant correlations (p < 0.05) for most metrics

---
