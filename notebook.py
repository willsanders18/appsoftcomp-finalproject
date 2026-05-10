# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.23.4",
#     "matplotlib==3.10.9",
#     "numpy==2.4.4",
#     "pandas==3.0.2",
#     "trendspyg==0.4.3",
#     "scipy==1.15",
#     "seaborn==0.13.2",
#     "plotly==6.7.0",
#     "openpyxl==3.1.5",
#     "statsmodels==0.14.5",
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
    import warnings
    from statsmodels.tsa.stattools import grangercausalitytests
    
    warnings.filterwarnings("ignore", category=FutureWarning)

    mo.md("# MAANG Stock vs Internet Usage Correlation Analysis")
    return mo, pd, np, plt, sns, stats, go, make_subplots, px, os, grangercausalitytests


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
    log_sp500 = np.log(combined_df.pivot_table(index="YearMonth", values="SP500_Close")["SP500_Close"])
    
    for _comp in companies_list:
        log_price = np.log(pivot_price[_comp])
        analysis_df[f"{_comp}_Price"] = log_price
        analysis_df[f"{_comp}_RelativePrice"] = log_price - log_sp500
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
    return


@app.cell
def _(analysis_df, companies_list, stats, pd):
    correlation_results = []
    
    for _comp in companies_list:
        for _metric in ["Price", "RelativePrice", "Volume", "Volatility"]:
            _metric_col = f"{_comp}_{_metric}"
            _internet_col = f"{_comp}_InternetUsage"
            
            _pearson_r, _pearson_p = stats.pearsonr(analysis_df[_metric_col], analysis_df[_internet_col])
            _spearman_r, _spearman_p = stats.spearmanr(analysis_df[_metric_col], analysis_df[_internet_col])
            
            correlation_results.append({
                "Company": _comp,
                "Metric": _metric,
                "Pearson_r": _pearson_r,
                "Pearson_p": _pearson_p,
                "Spearman_r": _spearman_r,
                "Spearman_p": _spearman_p,
                "Significant_Pearson": _pearson_p < 0.05,
                "Significant_Spearman": _spearman_p < 0.05
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
    _significance_message = (
        f"**Statistically Significant Correlations (p < 0.05):** {len(significant)} out of {len(results_df)} tests"
        if len(significant) > 0
        else "**No statistically significant correlations found (p < 0.05)**"
    )
    mo.vstack([
        mo.md("## Correlation Analysis Results"),
        mo.ui.table(display_df[["Company", "Metric", "Pearson_r", "Pearson_p", "Spearman_r", "Spearman_p"]]),
        mo.md(_significance_message),
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
    return


@app.cell
def _(analysis_df, companies_list, go, make_subplots):
    fig_price = make_subplots(specs=[[{"secondary_y": True}]])
    
    for _comp in companies_list:
        fig_price.add_trace(go.Scatter(
            x=analysis_df.index,
            y=analysis_df[f"{_comp}_RelativePrice"],
            name=f"{_comp} Rel Price",
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
        title="Interactive: Relative Log Price (vs S&P 500) vs Internet Usage",
        hovermode="x unified",
        height=600,
        legend_title="Companies"
    )
    fig_price.update_xaxes(title_text="Date")
    fig_price.update_yaxes(title_text="Log Price Diff (vs S&P 500)", secondary_y=False)
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
    return


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
    return


@app.cell
def _(analysis_df, companies_list, go, make_subplots, np):
    fig_scatter = make_subplots(rows=5, cols=4, subplot_titles=[
        f"{_c} {_m}" for _c in companies_list for _m in ["Price", "RelativePrice", "Volume", "Volatility"]
    ])
    
    colors_map = {"Price": "#1f77b4", "Volume": "#2ca02c", "Volatility": "#ff7f0e"}
    
    for _row_idx, _comp in enumerate(companies_list):
        for _col_idx, (_metric, _color) in enumerate(zip(["Price", "RelativePrice", "Volume", "Volatility"], [colors_map["Price"], "#9467bd", colors_map["Volume"], colors_map["Volatility"]])):
            _x = analysis_df[f"{_comp}_InternetUsage"]
            _y = analysis_df[f"{_comp}_{_metric}"]
            _corr = np.corrcoef(_x, _y)[0, 1]
            
            fig_scatter.add_trace(go.Scatter(
                x=_x,
                y=_y,
                mode="markers",
                marker=dict(color=_color, opacity=0.5, size=8),
                name=f"{_comp} {_metric}",
                showlegend=False,
                hovertemplate=f"Internet: %{{x}}<br>{_metric}: %{{y}}<extra></extra>"
            ), row=_row_idx+1, col=_col_idx+1)
            
            _z = np.polyfit(_x, _y, 1)
            _p = np.poly1d(_z)
            _x_line = np.linspace(_x.min(), _x.max(), 100)
            fig_scatter.add_trace(go.Scatter(
                x=_x_line,
                y=_p(_x_line),
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
    return


@app.cell
def _(analysis_df, companies_list, go, make_subplots):
    window = 36
    
    fig_rolling = make_subplots(rows=5, cols=4, subplot_titles=[
        f"{_c} {_m}" for _c in companies_list for _m in ["Price", "RelativePrice", "Volume", "Volatility"]
    ])
    
    for _row_idx, _comp in enumerate(companies_list):
        for _col_idx, _metric in enumerate(["Price", "RelativePrice", "Volume", "Volatility"]):
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
    _lag_markdown = "---\n\n## Lag Analysis\n\nThis section analyzes whether internet usage at time t correlates with stock metrics at future time periods (t+1, t+2, etc.).\n\n**Purpose:** Identify if changes in internet usage can predict future stock price movements.\n\n**Method:** Calculate correlations between internet usage at time t and stock metrics at time t+lag for lags 1-12 months.\n\n**Interpretation:**\n- Significant positive lag correlation suggests internet usage increases precede price increases\n- Significant negative lag correlation suggests internet usage increases precede price decreases"
    mo.md(_lag_markdown)
    return


@app.cell
def _(analysis_df, companies_list, stats, pd, np):
    lag_analysis_results = []
    max_lag = 12
    
    for _comp in companies_list:
        for _metric in ["Price", "RelativePrice", "Volume", "Volatility"]:
            _metric_col = f"{_comp}_{_metric}"
            _internet_col = f"{_comp}_InternetUsage"
            
            for _lag in range(1, max_lag + 1):
                _internet_lagged = analysis_df[_internet_col].shift(_lag)
                _metric_current = analysis_df[_metric_col]
                
                _valid_mask = ~(_internet_lagged.isna() | _metric_current.isna())
                if _valid_mask.sum() > 10:
                    _pearson_r, _pearson_p = stats.pearsonr(
                        _metric_current[_valid_mask], 
                        _internet_lagged[_valid_mask]
                    )
                    
                    lag_analysis_results.append({
                        "Company": _comp,
                        "Metric": _metric,
                        "Lag_Months": _lag,
                        "Pearson_r": _pearson_r,
                        "Pearson_p": _pearson_p,
                        "Significant": _pearson_p < 0.05
                    })
    
    lag_results_df = pd.DataFrame(lag_analysis_results)
    
    return lag_results_df, max_lag


@app.cell
def _(lag_results_df, mo):
    lag_display = lag_results_df.copy()
    lag_display["Pearson_r"] = lag_display["Pearson_r"].round(4)
    lag_display["Pearson_p"] = lag_display["Pearson_p"].round(4)
    lag_display["abs_corr"] = lag_display["Pearson_r"].abs()
    top_10 = lag_display.nlargest(10, "abs_corr")[["Company", "Metric", "Lag_Months", "Pearson_r", "Pearson_p", "Significant"]]
    
    significant_lags = lag_results_df[lag_results_df["Significant"]]
    mo.vstack([
        mo.md("### Lag Correlation Results (Top 10 by Absolute Correlation)"),
        mo.ui.table(top_10),
        mo.md(f"**Significant Lag Correlations (p < 0.05):** {len(significant_lags)} out of {len(lag_results_df)} tests"),
    ])
    
    return lag_display, top_10, significant_lags


@app.cell
def _(lag_results_df, companies_list, go, make_subplots):
    fig_lag = make_subplots(rows=3, cols=2, subplot_titles=[f"{c} - All Metrics" for c in companies_list])
    
    _metrics = ["Price", "Volume", "Volatility"]
    colors_lag = {"Price": "#1f77b4", "Volume": "#2ca02c", "Volatility": "#ff7f0e"}
    
    for _idx, _comp in enumerate(companies_list):
        _row = (_idx // 2) + 1
        _col = (_idx % 2) + 1
        
        for _metric in _metrics:
            _metric_data = lag_results_df[(lag_results_df["Company"] == _comp) & (lag_results_df["Metric"] == _metric)]
            
            fig_lag.add_trace(go.Scatter(
                x=_metric_data["Lag_Months"],
                y=_metric_data["Pearson_r"],
                mode="lines+markers",
                name=f"{_comp} {_metric}",
                line=dict(color=colors_lag[_metric], width=2),
                showlegend=(_idx == 0),
                hovertemplate=f"Lag: %{{x}} months<br>Correlation: %{{y:.3f}}<extra>{_metric}</extra>"
            ), row=_row, col=_col)
        
        fig_lag.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=_row, col=_col)
        fig_lag.update_yaxes(range=[-1, 1], row=_row, col=_col)
        fig_lag.update_xaxes(title_text="Lag (Months)", row=_row, col=_col)
        fig_lag.update_yaxes(title_text="Correlation", row=_row, col=_col)
    
    fig_lag.update_layout(
        title="Lag Analysis: Internet Usage vs Future Stock Metrics",
        height=900,
        width=1200
    )
    
    return fig_lag


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Granger Causality Testing
    
    Statistical test to determine if one time series can predict another.
    
    **Null Hypothesis (H0):** Internet usage does NOT Granger-cause stock metric changes
    
    **Alternative Hypothesis (H1):** Internet usage DOES Granger-cause stock metric changes
    
    **Interpretation:**
    - p-value < 0.05: Reject null hypothesis - internet usage has predictive power for stock metrics
    - p-value >= 0.05: Cannot reject null hypothesis - no evidence of predictive relationship
    
    **Note:** Granger causality does not imply true causation, only predictive relationship.
    """)
    return


@app.cell
def _(analysis_df, companies_list, grangercausalitytests, pd, np):
    granger_results = []
    max_lag_gc = 12
    
    for _comp in companies_list:
        for _metric in ["Price", "RelativePrice", "Volume", "Volatility"]:
            _metric_col = f"{_comp}_{_metric}"
            _internet_col = f"{_comp}_InternetUsage"
            
            _data_pair = pd.DataFrame({
                "metric": analysis_df[_metric_col].values,
                "internet": analysis_df[_internet_col].values
            })
            
            _data_pair = _data_pair.dropna()
            
            if len(_data_pair) > max_lag_gc * 2:
                try:
                    _gc_test = grangercausalitytests(
                        _data_pair[["metric", "internet"]],
                        maxlag=max_lag_gc,
                        verbose=False
                    )
                    
                    for _lag_num in range(1, max_lag_gc + 1):
                        if _lag_num in _gc_test:
                            _test_results = _gc_test[_lag_num][0]
                            for _test_name, _test_values in _test_results.items():
                                 _stat = _test_values[0]
                                 _pval = _test_values[1]
                                 granger_results.append({
                                     "Company": _comp,
                                     "Metric": _metric,
                                     "Lag": _lag_num,
                                     "Test": _test_name,
                                     "F_statistic": _stat,
                                     "p_value": _pval,
                                     "Significant": _pval < 0.05
                                 })
                except Exception as e:
                    print(f"Granger test failed for {_comp} {_metric}: {e}")

    
    granger_results_df = pd.DataFrame(granger_results)
    
    return granger_results_df, max_lag_gc


@app.cell
def _(granger_results_df, mo):
    _granger_output = None
    if len(granger_results_df) > 0:
        granger_display = granger_results_df.copy()
        granger_display["p_value"] = granger_display["p_value"].round(6)
        granger_display["F_statistic"] = granger_display["F_statistic"].round(4)
        
        _f_test_results = granger_display[granger_display["Test"] == "ssr_ftest"][["Company", "Metric", "Lag", "F_statistic", "p_value", "Significant"]]
        
        significant_gc = granger_results_df[granger_results_df["Significant"]]
        _significant_message = f"**Significant Granger Causality Tests (p < 0.05):** {len(significant_gc)} out of {len(granger_results_df)} tests"
        
        _summary_by_company = granger_results_df.groupby("Company").agg({
            "Significant": "sum",
            "p_value": "mean"
        }).reset_index()
        _summary_by_company.columns = ["Company", "Significant_Tests", "Avg_p_value"]
        _summary_by_company["Avg_p_value"] = _summary_by_company["Avg_p_value"].round(4)
        
        _granger_output = mo.vstack([
            mo.md("### Granger Causality Test Results"),
            mo.md("### All Granger Test Results (F-test)"),
            mo.ui.table(_f_test_results),
            mo.md(_significant_message),
            mo.md("### Summary by Company"),
            mo.ui.table(_summary_by_company),
        ])
    else:
        granger_display = None
        _granger_output = mo.vstack([
            mo.md("### Granger Causality Test Results"),
            mo.md("**No Granger causality test results available**"),
        ])
    _granger_output
    
    return granger_display


@app.cell
def _(granger_results_df, companies_list, go, make_subplots):
    fig_granger = None
    if len(granger_results_df) > 0:
        _f_tests = granger_results_df[granger_results_df["Test"] == "ssr_ftest"]
        
        fig_granger = make_subplots(rows=5, cols=4, subplot_titles=[f"{c} - All Metrics" for c in companies_list])
        
        _metrics = ["Price", "RelativePrice", "Volume", "Volatility"]
        colors_gc = {"Price": "#1f77b4", "RelativePrice": "#9467bd", "Volume": "#2ca02c", "Volatility": "#ff7f0e"}
        
        for _idx, _comp in enumerate(companies_list):
            _row = (_idx // 4) + 1
            _col = (_idx % 4) + 1
            
            for _metric in _metrics:
                _metric_data = _f_tests[(_f_tests["Company"] == _comp) & (_f_tests["Metric"] == _metric)]
                
                fig_granger.add_trace(go.Scatter(
                    x=_metric_data["Lag"],
                    y=_metric_data["p_value"],
                    mode="lines+markers",
                    name=f"{_comp} {_metric}",
                    line=dict(color=colors_gc[_metric], width=2),
                    showlegend=(_idx == 0),
                    hovertemplate=f"Lag: %{{x}} months<br>p-value: %{{y:.4f}}<extra>{_metric}</extra>"
                ), row=_row, col=_col)
            fig_granger.add_hline(y=0.05, line_dash="dash", line_color="red", opacity=0.7, row=_row, col=_col, annotation_text="p=0.05")
            fig_granger.update_yaxes(type="log", row=_row, col=_col)
            fig_granger.update_xaxes(title_text="Lag (Months)", row=_row, col=_col)
            fig_granger.update_yaxes(title_text="p-value (log scale)", row=_row, col=_col)
 la

        
        fig_granger.update_layout(
            title="Granger Causality Test: Internet Usage -> Stock Metrics (p-values)",
            height=900,
            width=1200
        )
    
    return fig_granger


@app.cell
def _(mo):
    mo.md("""
    ---
    
    ## Export Results
    
    This section exports all analysis results to files for further use or reporting.
    Files are saved to the `data/exports/` directory.
    """)
    return


@app.cell
def _(analysis_df, companies_list, granger_results_df, lag_results_df, mo, os, pd, results_df):
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
    
    lag_export = lag_results_df.copy()
    lag_export["Pearson_r"] = lag_export["Pearson_r"].round(6)
    lag_export["Pearson_p"] = lag_export["Pearson_p"].round(6)
    lag_path = os.path.join(export_dir, "lag_analysis_results.csv")
    lag_export.to_csv(lag_path, index=False)
    
    if len(granger_results_df) > 0:
        granger_export = granger_results_df.copy()
        granger_export["p_value"] = granger_export["p_value"].round(6)
        granger_export["F_statistic"] = granger_export["F_statistic"].round(6)
        granger_path = os.path.join(export_dir, "granger_causality_results.csv")
        granger_export.to_csv(granger_path, index=False)
    else:
        granger_path = None
    
    excel_path = os.path.join(export_dir, "full_analysis_results.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        corr_export.to_excel(writer, sheet_name="Correlations", index=False)
        analysis_df.to_excel(writer, sheet_name="Analysis_Data", index=True)
        lag_export.to_excel(writer, sheet_name="Lag_Analysis", index=False)
        if len(granger_results_df) > 0:
            granger_export.to_excel(writer, sheet_name="Granger_Tests", index=False)
    
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
    
    export_files = [csv_path, lag_path, excel_path, summary_path]
    if granger_path:
        export_files.append(granger_path)
    
    mo.md(f"""
**Exported Files:**
- `{csv_path}` - Correlation results (CSV)
- `{lag_path}` - Lag analysis results (CSV)
{f"- `{granger_path}` - Granger causality results (CSV)" if granger_path else ""}
- `{excel_path}` - Full results with analysis data (Excel)
- `{summary_path}` - Summary statistics (CSV)
    """)
    
    return export_dir, export_files


if __name__ == "__main__":
    app.run()
