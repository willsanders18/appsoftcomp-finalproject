# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.23.4",
#     "matplotlib==3.10.9",
#     "numpy==2.4.4",
#     "pandas==3.0.2",
#     "trendspyg==0.4.3",
#     "scipy==1.17.1",
#     "seaborn==0.13.2",
#     "plotly==6.7.0",
#     "openpyxl==3.1.5",
# ]
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    import os

    mo.md("# MAANG Stock vs Internet Usage Correlation Analysis")
    return mo, pd, np, plt, sns, stats, go, make_subplots, px, os


@app.cell
def _(pd):
    combined_df = pd.read_csv("data/cleaned/combined_analysis_data.csv", parse_dates=["YearMonth", "Date"])
    
    companies_list = ["Apple", "Amazon", "Google", "Microsoft", "Netflix"]
    
    pivot_price = combined_df.pivot_table(index="YearMonth", columns="Company", values="Close")
    pivot_volume = combined_df.pivot_table(index="YearMonth", columns="Company", values="Volume")
    pivot_volatility = combined_df.pivot_table(index="YearMonth", columns="Company", values="Volatility_30d")
    
    trend_cols = {
        "Apple": "Apple: (Worldwide)",
        "Google": "Google: (Worldwide)",
        "Amazon": "Amazon: (Worldwide)",
        "Microsoft": "Microsoft: (Worldwide)",
        "Netflix": "Netflix: (Worldwide)"
    }
    
    analysis_df = pd.DataFrame(index=pivot_price.index)
    for _comp in companies_list:
        analysis_df[f"{_comp}_Price"] = pivot_price[_comp]
        analysis_df[f"{_comp}_Volume"] = pivot_volume[_comp]
        analysis_df[f"{_comp}_Volatility"] = pivot_volatility[_comp]
        analysis_df[f"{_comp}_InternetUsage"] = combined_df.pivot_table(
            index="YearMonth", columns="Company", values=trend_cols[_comp]
        )[_comp]
    
    analysis_df = analysis_df.dropna()
    
    return analysis_df, companies_list, combined_df, pivot_price, pivot_volume, pivot_volatility, trend_cols


@app.cell
def _(analysis_df, companies_list, mo):
    mo.md(f"**Analysis Period:** {analysis_df.index.min().date()} to {analysis_df.index.max().date()}")
    mo.md(f"**Total Observations:** {len(analysis_df)} months")
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Correlation Analysis
    
    This section calculates both Pearson and Spearman correlation coefficients between internet usage and stock metrics (price, volume, volatility) for each company.
    
    - **Pearson correlation**: Measures linear relationships between variables
    - **Spearman correlation**: Measures monotonic (rank-based) relationships, more robust to outliers
    - **p-value**: Tests statistical significance (p < 0.05 indicates significant correlation)
    """)
    return mo


@app.cell
def _(analysis_df, companies_list, stats, pd):
    correlation_results = []
    
    for _comp in companies_list:
        for _metric in ["Price", "Volume", "Volatility"]:
            _metric_col = f"{_comp}_{_metric}"
            _internet_col = f"{_comp}_InternetUsage"
            
            pearson_r, pearson_p = stats.pearsonr(analysis_df[_metric_col], analysis_df[_internet_col])
            spearman_r, spearman_p = stats.spearmanr(analysis_df[_metric_col], analysis_df[_internet_col])
            
            correlation_results.append({
                "Company": _comp,
                "Metric": _metric,
                "Pearson_r": pearson_r,
                "Pearson_p": pearson_p,
                "Spearman_r": spearman_r,
                "Spearman_p": spearman_p,
                "Significant_Pearson": pearson_p < 0.05,
                "Significant_Spearman": spearman_p < 0.05
            })
    
    results_df = pd.DataFrame(correlation_results)
    
    return results_df


@app.cell
def _(results_df, mo):
    display_df = results_df.copy()
    display_df["Pearson_r"] = display_df["Pearson_r"].round(4)
    display_df["Pearson_p"] = display_df["Pearson_p"].round(4)
    display_df["Spearman_r"] = display_df["Spearman_r"].round(4)
    display_df["Spearman_p"] = display_df["Spearman_p"].round(4)
    
    significant = results_df[(results_df["Significant_Pearson"]) | (results_df["Significant_Spearman"])]
    significance_message = (
        f"**Statistically Significant Correlations (p < 0.05):** {len(significant)} out of {len(results_df)} tests"
        if len(significant) > 0
        else "**No statistically significant correlations found (p < 0.05)**"
    )
    mo.vstack([
        mo.md("## Correlation Analysis Results"),
        mo.ui.table(display_df[["Company", "Metric", "Pearson_r", "Pearson_p", "Spearman_r", "Spearman_p"]]),
        mo.md(significance_message),
    ])
    
    return display_df, significant


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Interactive Time Series Visualizations
    
    The following charts show the relationship between stock metrics and internet usage over time.
    Use the interactive features to:
    - **Hover** over data points to see exact values
    - **Zoom** by selecting a region
    - **Pan** by dragging the plot
    - **Toggle** legend items to show/hide specific companies
    """)
    return mo


@app.cell
def _(analysis_df, companies_list, go, make_subplots):
    fig_price = make_subplots(specs=[[{"secondary_y": True}]])
    
    for _comp in companies_list:
        fig_price.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_Price"],
            name=f"{_comp} Price",
            line=dict(width=2),
            legendgroup=_comp,
            showlegend=True
        ), secondary_y=False)
        
        fig_price.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_InternetUsage"],
            name=f"{_comp} Internet",
            line=dict(dash="dash", width=2),
            legendgroup=_comp,
            showlegend=False,
            line_color='rgba(214,39,40,0.7)'
        ), secondary_y=True)
    
    fig_price.update_layout(
        title="Interactive: Stock Price vs Internet Usage",
        hovermode="x unified",
        height=600,
        legend_title="Companies"
    )
    fig_price.update_xaxes(title_text="Date")
    fig_price.update_yaxes(title_text="Stock Price ($)", secondary_y=False)
    fig_price.update_yaxes(title_text="Internet Usage (Relative)", secondary_y=True)
    
    return fig_price


@app.cell
def _(analysis_df, companies_list, go, make_subplots):
    fig_volume = make_subplots(specs=[[{"secondary_y": True}]])
    
    for _comp in companies_list:
        fig_volume.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_Volume"],
            name=f"{_comp} Volume",
            line=dict(width=2, color='#2ca02c'),
            legendgroup=_comp,
            showlegend=True
        ), secondary_y=False)
        
        fig_volume.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_InternetUsage"],
            name=f"{_comp} Internet",
            line=dict(dash="dash", width=2, color='#d62728'),
            legendgroup=_comp,
            showlegend=False
        ), secondary_y=True)
    
    fig_volume.update_layout(
        title="Interactive: Trading Volume vs Internet Usage",
        hovermode="x unified",
        height=600
    )
    fig_volume.update_xaxes(title_text="Date")
    fig_volume.update_yaxes(title_text="Trading Volume", secondary_y=False)
    fig_volume.update_yaxes(title_text="Internet Usage (Relative)", secondary_y=True)
    
    return fig_volume


@app.cell
def _(analysis_df, companies_list, go, make_subplots):
    fig_volatility = make_subplots(specs=[[{"secondary_y": True}]])
    
    for _comp in companies_list:
        fig_volatility.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_Volatility"],
            name=f"{_comp} Volatility",
            line=dict(width=2, color='#ff7f0e'),
            legendgroup=_comp,
            showlegend=True
        ), secondary_y=False)
        
        fig_volatility.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_InternetUsage"],
            name=f"{_comp} Internet",
            line=dict(dash="dash", width=2, color='#d62728'),
            legendgroup=_comp,
            showlegend=False
        ), secondary_y=True)
    
    fig_volatility.update_layout(
        title="Interactive: Volatility (30-day) vs Internet Usage",
        hovermode="x unified",
        height=600
    )
    fig_volatility.update_xaxes(title_text="Date")
    fig_volatility.update_yaxes(title_text="Volatility (30-day std)", secondary_y=False)
    fig_volatility.update_yaxes(title_text="Internet Usage (Relative)", secondary_y=True)
    
    return fig_volatility


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Correlation Heatmaps
    
    Heatmaps showing correlation coefficients between all stock prices and internet usage metrics.
    - Values range from -1 (perfect negative) to +1 (perfect positive)
    - Darker colors indicate stronger correlations
    """)
    return mo


@app.cell
def _(analysis_df, companies_list, px):
    metric_select = "Price"
    cols_for_heatmap = [f"{c}_{metric_select}" for c in companies_list] + [f"{c}_InternetUsage" for c in companies_list]
    corr_matrix_hm = analysis_df[cols_for_heatmap].corr()
    
    fig_heatmap = px.imshow(
        corr_matrix_hm,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Correlation Heatmap: {metric_select} & Internet Usage",
        aspect="auto"
    )
    fig_heatmap.update_layout(height=600, width=800)
    fig_heatmap.update_xaxes(tickangle=45)
    
    return fig_heatmap


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Scatter Plots with Regression Lines
    
    Scatter plots showing the relationship between internet usage and each stock metric.
    - Each point represents one month of data
    - Red dashed line shows the linear regression fit
    - Correlation coefficient (r) displayed in each subplot title
    """)
    return mo


@app.cell
def _(analysis_df, companies_list, go, make_subplots, np):
    fig_scatter = make_subplots(rows=5, cols=3, subplot_titles=[
        f"{_c} {_m}" for _c in companies_list for _m in ["Price", "Volume", "Volatility"]
    ])
    
    colors = {"Price": "#1f77b4", "Volume": "#2ca02c", "Volatility": "#ff7f0e"}
    
    for _row_idx, _comp in enumerate(companies_list):
        for _col_idx, (_metric, _color) in enumerate(zip(["Price", "Volume", "Volatility"], [colors["Price"], colors["Volume"], colors["Volatility"]])):
            x = analysis_df[f"{_comp}_InternetUsage"]
            y = analysis_df[f"{_comp}_{_metric}"]
            corr = np.corrcoef(x, y)[0, 1]
            
            fig_scatter.add_trace(go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(color=_color, opacity=0.5, size=8),
                name=f"{_comp} {_metric}",
                showlegend=False,
                hovertemplate=f"Internet: %{{x}}<br>{_metric}: %{{y}}<extra></extra>"
            ), row=_row_idx+1, col=_col_idx+1)
            
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(x.min(), x.max(), 100)
            fig_scatter.add_trace(go.Scatter(
                x=x_line,
                y=p(x_line),
                mode="lines",
                line=dict(color="red", dash="dash"),
                showlegend=False,
                hoverinfo="skip"
            ), row=_row_idx+1, col=_col_idx+1)
            
            fig_scatter.update_xaxes(title_text="Internet Usage", row=_row_idx+1, col=_col_idx+1)
            fig_scatter.update_yaxes(title_text=_metric, row=_row_idx+1, col=_col_idx+1)
    
    fig_scatter.update_layout(
        title="Scatter Plots: Stock Metrics vs Internet Usage",
        height=1200,
        width=1200
    )
    
    return fig_scatter


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Rolling Correlation Analysis
    
    Shows how the correlation between internet usage and stock metrics changes over time.
    - Uses a 36-month rolling window
    - Helps identify if relationships strengthen or weaken over different time periods
    - Red dotted lines at ±0.5 indicate moderate correlation thresholds
    """)
    return mo


@app.cell
def _(analysis_df, companies_list, go, make_subplots):
    window = 36
    
    fig_rolling = make_subplots(rows=5, cols=3, subplot_titles=[
        f"{_c} {_m}" for _c in companies_list for _m in ["Price", "Volume", "Volatility"]
    ])
    
    for _row_idx, _comp in enumerate(companies_list):
        for _col_idx, _metric in enumerate(["Price", "Volume", "Volatility"]):
            _metric_col = f"{_comp}_{_metric}"
            _internet_col = f"{_comp}_InternetUsage"
            
            rolling_corr = analysis_df[_metric_col].rolling(window=window).corr(analysis_df[_internet_col])
            
            fig_rolling.add_trace(go.Scatter(
                x=analysis_df.index,
                y=rolling_corr,
                mode="lines",
                line=dict(width=2),
                name=f"{_comp} {_metric}",
                showlegend=False,
                hovertemplate=f"Date: %{{x}}<br>Correlation: %{{y:.3f}}<extra></extra>"
            ), row=_row_idx+1, col=_col_idx+1)
            
            fig_rolling.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=_row_idx+1, col=_col_idx+1)
            fig_rolling.add_hline(y=0.5, line_dash="dot", line_color="red", opacity=0.5, row=_row_idx+1, col=_col_idx+1)
            fig_rolling.add_hline(y=-0.5, line_dash="dot", line_color="red", opacity=0.5, row=_row_idx+1, col=_col_idx+1)
            
            fig_rolling.update_xaxes(title_text="Date", row=_row_idx+1, col=_col_idx+1)
            fig_rolling.update_yaxes(title_text="Correlation", range=[-1, 1], row=_row_idx+1, col=_col_idx+1)
    
    fig_rolling.update_layout(
        title=f"Rolling Correlation ({window}-month window)",
        height=1200,
        width=1200
    )
    
    return fig_rolling, rolling_corr, window


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Export Results
    
    This section exports all analysis results to files for further use or reporting.
    Files are saved to the `data/exports/` directory.
    """)
    return mo


@app.cell
def _(analysis_df, companies_list, mo, os, pd, results_df):
    mo.md("## Export Results")
    
    export_dir = "data/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    corr_export = results_df.copy()
    corr_export["Pearson_r"] = corr_export["Pearson_r"].round(6)
    corr_export["Pearson_p"] = corr_export["Pearson_p"].round(6)
    corr_export["Spearman_r"] = corr_export["Spearman_r"].round(6)
    corr_export["Spearman_p"] = corr_export["Spearman_p"].round(6)
    
    csv_path = os.path.join(export_dir, "correlation_results.csv")
    corr_export.to_csv(csv_path, index=False)
    
    excel_path = os.path.join(export_dir, "correlation_results.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        corr_export.to_excel(writer, sheet_name="Correlations", index=False)
        analysis_df.to_excel(writer, sheet_name="Analysis_Data", index=True)
    
    summary_path = os.path.join(export_dir, "summary_statistics.csv")
    summary_stats = []
    for _comp in companies_list:
        for _metric in ["Price", "Volume", "Volatility"]:
            _col = f"{_comp}_{_metric}"
            summary_stats.append({
                "Company": _comp,
                "Metric": _metric,
                "Mean": analysis_df[_col].mean(),
                "Std": analysis_df[_col].std(),
                "Min": analysis_df[_col].min(),
                "Max": analysis_df[_col].max(),
                "Median": analysis_df[_col].median()
            })
    summary_df = pd.DataFrame(summary_stats)
    summary_df.to_csv(summary_path, index=False)
    
    mo.md(f"""
**Exported Files:**
- `{csv_path}` - Correlation results (CSV)
- `{excel_path}` - Full results with analysis data (Excel)
- `{summary_path}` - Summary statistics (CSV)
    """)
    
    return export_dir


if __name__ == "__main__":
    app.run()
