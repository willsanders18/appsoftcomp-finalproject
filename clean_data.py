"""
Data Cleaning Script for MAANG Stock and Internet Usage Data

This script cleans raw stock market data and internet usage trend data,
then saves the cleaned datasets to the data/cleaned folder.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path


def load_stock_data(data_dir: str, companies: list) -> dict:
    """Load all stock CSV files into a dictionary of DataFrames."""
    stock_dfs = {}
    for company in companies:
        file_path = os.path.join(data_dir, f"{company}.csv")
        df = pd.read_csv(file_path, parse_dates=["Date"])
        df["Company"] = company
        stock_dfs[company] = df
        print(f"Loaded {company}: {df.shape[0]} rows, {df.shape[1]} columns")
    return stock_dfs


def load_trend_data(trend_path: str) -> pd.DataFrame:
    """Load Google Trends internet usage data."""
    df = pd.read_csv(trend_path, skiprows=2)
    print(f"Loaded trend data: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean_trend_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean internet usage data:
    - Convert '<1' values to numeric (0.5)
    - Handle missing values
    - Convert Month column to datetime
    """
    df_clean = df.copy()
    
    for col in df_clean.columns[1:]:
        df_clean[col] = df_clean[col].replace("<1", "0.5")
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    
    df_clean["Month"] = pd.to_datetime(df_clean["Month"])
    df_clean = df_clean.dropna(subset=["Month"])
    df_clean = df_clean.sort_values("Month").reset_index(drop=True)
    
    return df_clean


def clean_stock_data(stock_dfs: dict, companies: list) -> dict:
    """
    Clean stock data for each company:
    - Standardize date formats
    - Remove duplicates
    - Handle missing values
    - Sort by date
    """
    cleaned_dfs = {}
    for company in companies:
        df = stock_dfs[company].copy()
        
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.drop_duplicates(subset=["Date"])
        df = df.sort_values("Date")
        
        numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=numeric_cols)
        df = df.reset_index(drop=True)
        
        cleaned_dfs[company] = df
        print(f"Cleaned {company}: {df.shape[0]} rows (removed {stock_dfs[company].shape[0] - df.shape[0]} rows)")
    
    return cleaned_dfs


def aggregate_to_monthly(stock_dfs: dict, companies: list) -> pd.DataFrame:
    """
    Aggregate daily stock data to monthly frequency:
    - Mean for prices (Close)
    - Sum for Volume
    - Last value for Volatility (30-day rolling std of log returns)
    """
    monthly_dfs = []
    
    for company in companies:
        df = stock_dfs[company].copy()
        
        df["LogReturn"] = np.log(df["Close"] / df["Close"].shift(1))
        df["Volatility_30d"] = df["LogReturn"].rolling(window=30).std()
        
        df["YearMonth"] = df["Date"].dt.to_period("M")
        
        monthly_agg = df.groupby("YearMonth").agg({
            "Date": "last",
            "Close": "mean",
            "Volume": "sum",
            "Volatility_30d": "last"
        }).reset_index()
        
        monthly_agg["YearMonth"] = monthly_agg["YearMonth"].dt.to_timestamp()
        monthly_agg["Company"] = company
        
        monthly_dfs.append(monthly_agg)
    
    merged = pd.concat(monthly_dfs, ignore_index=True)
    return merged


def align_datasets(monthly_stocks: pd.DataFrame, trend_df: pd.DataFrame) -> pd.DataFrame:
    """
    Align stock and trend data to overlapping time period.
    Merge on YearMonth to create combined analysis dataset.
    """
    min_date = trend_df["Month"].min()
    max_date = trend_df["Month"].max()
    
    monthly_stocks = monthly_stocks[
        (monthly_stocks["YearMonth"] >= min_date) & 
        (monthly_stocks["YearMonth"] <= max_date)
    ].copy()
    
    trend_df_renamed = trend_df.rename(columns={"Month": "YearMonth"})
    
    combined = monthly_stocks.merge(
        trend_df_renamed,
        on="YearMonth",
        how="inner"
    )
    
    print(f"Aligned dataset: {combined.shape[0]} rows, {combined.shape[1]} columns")
    print(f"Date range: {combined['YearMonth'].min()} to {combined['YearMonth'].max()}")
    
    return combined


def save_cleaned_data(
    cleaned_stocks: dict,
    trend_df: pd.DataFrame,
    monthly_stocks: pd.DataFrame,
    combined_df: pd.DataFrame,
    output_dir: str
):
    """Save all cleaned datasets to the cleaned data folder."""
    os.makedirs(output_dir, exist_ok=True)
    
    for company, df in cleaned_stocks.items():
        output_path = os.path.join(output_dir, f"{company}_cleaned.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")
    
    trend_output = os.path.join(output_dir, "internet_usage_cleaned.csv")
    trend_df.to_csv(trend_output, index=False)
    print(f"Saved: {trend_output}")
    
    monthly_output = os.path.join(output_dir, "stocks_monthly_aggregated.csv")
    monthly_stocks.to_csv(monthly_output, index=False)
    print(f"Saved: {monthly_output}")
    
    combined_output = os.path.join(output_dir, "combined_analysis_data.csv")
    combined_df.to_csv(combined_output, index=False)
    print(f"Saved: {combined_output}")


def main():
    base_dir = Path(__file__).parent
    raw_stock_dir = base_dir / "data" / "raw" / "company_stock_data"
    raw_trend_path = base_dir / "data" / "raw" / "company_trend_data" / "multiTimeline.csv"
    cleaned_dir = base_dir / "data" / "cleaned"
    
    companies = ["Apple", "Amazon", "Google", "Microsoft", "Netflix"]
    
    print("=" * 60)
    print("MAANG Data Cleaning Pipeline")
    print("=" * 60)
    
    print("\n[1/6] Loading stock data...")
    stock_dfs = load_stock_data(str(raw_stock_dir), companies)
    
    print("\n[2/6] Loading trend data...")
    trend_df = load_trend_data(str(raw_trend_path))
    
    print("\n[3/6] Cleaning trend data...")
    trend_df_clean = clean_trend_data(trend_df)
    
    print("\n[4/6] Cleaning stock data...")
    stock_dfs_clean = clean_stock_data(stock_dfs, companies)
    
    print("\n[5/6] Aggregating stock data to monthly...")
    monthly_stocks = aggregate_to_monthly(stock_dfs_clean, companies)
    
    print("\n[6/6] Aligning datasets...")
    combined_df = align_datasets(monthly_stocks, trend_df_clean)
    
    print("\n" + "=" * 60)
    print("Saving cleaned data...")
    print("=" * 60)
    save_cleaned_data(stock_dfs_clean, trend_df_clean, monthly_stocks, combined_df, str(cleaned_dir))
    
    print("\n" + "=" * 60)
    print("Data cleaning complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
