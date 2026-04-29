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
    import os

    mo.md("# MAANG Stock vs Internet Usage Correlation Analysis")
    return mo, pd, np, plt, sns, stats, os


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
    for comp in companies_list:
        analysis_df[f"{comp}_Price"] = pivot_price[comp]
        analysis_df[f"{comp}_Volume"] = pivot_volume[comp]
        analysis_df[f"{comp}_Volatility"] = pivot_volatility[comp]
        analysis_df[f"{comp}_InternetUsage"] = combined_df.pivot_table(
            index="YearMonth", columns="Company", values=trend_cols[comp]
        )[comp]
    
    analysis_df = analysis_df.dropna()
    
    return analysis_df, companies_list, combined_df, pivot_price, pivot_volume, pivot_volatility, trend_cols


@app.cell
def _(analysis_df, companies_list, mo):
    mo.md(f"**Analysis Period:** {analysis_df.index.min().date()} to {analysis_df.index.max().date()}")
    mo.md(f"**Total Observations:** {len(analysis_df)} months")
    return


@app.cell
def _(analysis_df, companies_list, plt):
    _fig1, _axes1 = plt.subplots(5, 1, figsize=(14, 20))
    _fig1.suptitle("Time Series: Stock Price vs Internet Usage", fontsize=16)
    
    for _idx1, _comp1 in enumerate(companies_list):
        _ax1 = _axes1[_idx1]
        _ax2_1 = _ax1.twinx()
        
        _line1_1 = _ax1.plot(analysis_df.index, analysis_df[f"{_comp1}_Price"], 
                       color="#1f77b4", label="Price", linewidth=2)
        _line2_1 = _ax2_1.plot(analysis_df.index, analysis_df[f"{_comp1}_InternetUsage"], 
                        color="#d62728", label="Internet Usage", linewidth=2, linestyle="--")
        
        _ax1.set_xlabel("Date")
        _ax1.set_ylabel("Stock Price ($)", color="#1f77b4")
        _ax2_1.set_ylabel("Internet Usage (Relative)", color="#d62728")
        _ax1.set_title(f"{_comp1}")
        _ax1.tick_params(axis="x", rotation=45)
        
        _lines1 = _line1_1 + _line2_1
        _labels1 = [l.get_label() for l in _lines1]
        _ax1.legend(_lines1, _labels1, loc="upper left")
        _ax1.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(analysis_df, companies_list, plt):
    _fig2, _axes2 = plt.subplots(5, 1, figsize=(14, 20))
    _fig2.suptitle("Time Series: Trading Volume vs Internet Usage", fontsize=16)
    
    for _idx2, _comp2 in enumerate(companies_list):
        _ax2 = _axes2[_idx2]
        _ax2_2 = _ax2.twinx()
        
        _line1_2 = _ax2.plot(analysis_df.index, analysis_df[f"{_comp2}_Volume"], 
                       color="#2ca02c", label="Volume", linewidth=2)
        _line2_2 = _ax2_2.plot(analysis_df.index, analysis_df[f"{_comp2}_InternetUsage"], 
                        color="#d62728", label="Internet Usage", linewidth=2, linestyle="--")
        
        _ax2.set_xlabel("Date")
        _ax2.set_ylabel("Trading Volume", color="#2ca02c")
        _ax2_2.set_ylabel("Internet Usage (Relative)", color="#d62728")
        _ax2.set_title(f"{_comp2}")
        _ax2.tick_params(axis="x", rotation=45)
        
        _lines2 = _line1_2 + _line2_2
        _labels2 = [l.get_label() for l in _lines2]
        _ax2.legend(_lines2, _labels2, loc="upper left")
        _ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(analysis_df, companies_list, plt):
    _fig3, _axes3 = plt.subplots(5, 1, figsize=(14, 20))
    _fig3.suptitle("Time Series: Volatility (30-day) vs Internet Usage", fontsize=16)
    
    for _idx3, _comp3 in enumerate(companies_list):
        _ax3 = _axes3[_idx3]
        _ax2_3 = _ax3.twinx()
        
        _line1_3 = _ax3.plot(analysis_df.index, analysis_df[f"{_comp3}_Volatility"], 
                       color="#ff7f0e", label="Volatility", linewidth=2)
        _line2_3 = _ax2_3.plot(analysis_df.index, analysis_df[f"{_comp3}_InternetUsage"], 
                        color="#d62728", label="Internet Usage", linewidth=2, linestyle="--")
        
        _ax3.set_xlabel("Date")
        _ax3.set_ylabel("Volatility (30-day std)", color="#ff7f0e")
        _ax2_3.set_ylabel("Internet Usage (Relative)", color="#d62728")
        _ax3.set_title(f"{_comp3}")
        _ax3.tick_params(axis="x", rotation=45)
        
        _lines3 = _line1_3 + _line2_3
        _labels3 = [l.get_label() for l in _lines3]
        _ax3.legend(_lines3, _labels3, loc="upper left")
        _ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(analysis_df, companies_list, plt):
    _fig4, _axes4 = plt.subplots(1, 3, figsize=(18, 6))
    _fig4.suptitle("Correlation Heatmaps by Metric", fontsize=16)
    
    for _idx4, _metric1 in enumerate(["Price", "Volume", "Volatility"]):
        _ax4 = _axes4[_idx4]
        
        _cols_corr = [f"{c}_{_metric1}" for c in companies_list] + [f"{c}_InternetUsage" for c in companies_list]
        _corr_matrix = analysis_df[_cols_corr].corr()
        
        _im = _ax4.imshow(_corr_matrix, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
        plt.colorbar(_im, ax=_ax4, label="Correlation")
        
        _ax4.set_xticks(range(len(_cols_corr)))
        _ax4.set_yticks(range(len(_cols_corr)))
        _short_labels = [c.replace("_InternetUsage", "").replace("_Price", "").replace("_Volume", "").replace("_Volatility", "") for c in _cols_corr]
        _ax4.set_xticklabels(_short_labels, rotation=45, ha="right", fontsize=8)
        _ax4.set_yticklabels(_short_labels, fontsize=8)
        _ax4.set_title(f"{_metric1} vs Internet Usage")
        
        for _i in range(len(_cols_corr)):
            for _j in range(len(_cols_corr)):
                _val = _corr_matrix.iloc[_i, _j]
                if abs(_val) > 0.1:
                    _ax4.text(_j, _i, f"{_val:.2f}", ha="center", va="center", fontsize=6)
    
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(analysis_df, companies_list, plt, np):
    _fig5, _axes5 = plt.subplots(5, 3, figsize=(15, 20))
    _fig5.suptitle("Scatter Plots: Stock Metrics vs Internet Usage", fontsize=16)
    
    _metrics = [("Price", "#1f77b4"), ("Volume", "#2ca02c"), ("Volatility", "#ff7f0e")]
    
    for _row_idx1, _comp4 in enumerate(companies_list):
        for _col_idx1, (_metric2, _color1) in enumerate(_metrics):
            _ax5 = _axes5[_row_idx1, _col_idx1]
            
            _x1 = analysis_df[f"{_comp4}_InternetUsage"]
            _y1 = analysis_df[f"{_comp4}_{_metric2}"]
            
            _ax5.scatter(_x1, _y1, alpha=0.5, s=30, color=_color1)
            
            if len(_x1) > 2:
                _z1 = np.polyfit(_x1, _y1, 1)
                _p1 = np.poly1d(_z1)
                _ax5.plot(_x1, _p1(_x1), "r--", alpha=0.7, linewidth=2)
                
                _corr1 = np.corrcoef(_x1, _y1)[0, 1]
                _ax5.set_title(f"{_comp4} {_metric2}\nr={_corr1:.3f}", fontsize=9)
            else:
                _ax5.set_title(f"{_comp4} {_metric2}", fontsize=9)
            
            _ax5.set_xlabel("Internet Usage")
            _ax5.set_ylabel(_metric2)
            _ax5.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(analysis_df, companies_list, stats, pd):
    _results_list = []
    
    for _comp5 in companies_list:
        for _metric3 in ["Price", "Volume", "Volatility"]:
            _metric_col = f"{_comp5}_{_metric3}"
            _internet_col = f"{_comp5}_InternetUsage"
            
            _pearson_r, _pearson_p = stats.pearsonr(analysis_df[_metric_col], analysis_df[_internet_col])
            _spearman_r, _spearman_p = stats.spearmanr(analysis_df[_metric_col], analysis_df[_internet_col])
            
            _results_list.append({
                "Company": _comp5,
                "Metric": _metric3,
                "Pearson_r": _pearson_r,
                "Pearson_p": _pearson_p,
                "Spearman_r": _spearman_r,
                "Spearman_p": _spearman_p,
                "Significant_Pearson": _pearson_p < 0.05,
                "Significant_Spearman": _spearman_p < 0.05
            })
    
    _results_df = pd.DataFrame(_results_list)
    
    return _results_df


@app.cell
def _(_results_df, mo):
    mo.md("## Correlation Analysis Results")
    
    _display_df = _results_df.copy()
    _display_df["Pearson_r"] = _display_df["Pearson_r"].round(4)
    _display_df["Pearson_p"] = _display_df["Pearson_p"].round(4)
    _display_df["Spearman_r"] = _display_df["Spearman_r"].round(4)
    _display_df["Spearman_p"] = _display_df["Spearman_p"].round(4)
    
    mo.md(_display_df[["Company", "Metric", "Pearson_r", "Pearson_p", "Spearman_r", "Spearman_p"]].to_markdown(index=False))
    
    _significant = _results_df[(_results_df["Significant_Pearson"]) | (_results_df["Significant_Spearman"])]
    if len(_significant) > 0:
        mo.md(f"**Statistically Significant Correlations (p < 0.05):** {len(_significant)} out of {len(_results_df)} tests")
    else:
        mo.md("**No statistically significant correlations found (p < 0.05)**")
    
    return _display_df, _significant


@app.cell
def _(analysis_df, companies_list, plt):
    _window = 36
    
    _fig6, _axes6 = plt.subplots(5, 3, figsize=(18, 20))
    _fig6.suptitle(f"Rolling Correlation ({_window}-month window)", fontsize=16)
    
    for _row_idx2, _comp6 in enumerate(companies_list):
        for _col_idx2, _metric4 in enumerate(["Price", "Volume", "Volatility"]):
            _ax6 = _axes6[_row_idx2, _col_idx2]
            
            _metric_col2 = f"{_comp6}_{_metric4}"
            _internet_col2 = f"{_comp6}_InternetUsage"
            
            _rolling_corr = analysis_df[_metric_col2].rolling(window=_window).corr(analysis_df[_internet_col2])
            
            _ax6.plot(analysis_df.index, _rolling_corr, linewidth=2, color="#1f77b4")
            _ax6.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)
            _ax6.axhline(y=0.5, color="red", linestyle=":", linewidth=1, alpha=0.5)
            _ax6.axhline(y=-0.5, color="red", linestyle=":", linewidth=1, alpha=0.5)
            _ax6.set_xlabel("Date")
            _ax6.set_ylabel("Correlation")
            _ax6.set_title(f"{_comp6} {_metric4}", fontsize=10)
            _ax6.grid(True, alpha=0.3)
            _ax6.tick_params(axis="x", rotation=45)
            _ax6.set_ylim(-1, 1)
    
    plt.tight_layout()
    plt.show()
    return _fig6, _axes6, _rolling_corr, _window


@app.cell
def _(_results_df, companies_list, mo):
    mo.md("## Summary")
    
    _summary_list = []
    for _comp7 in companies_list:
        _comp_results = _results_df[_results_df["Company"] == _comp7]
        _sig_count = len(_comp_results[(_comp_results["Significant_Pearson"]) | (_comp_results["Significant_Spearman"])])
        _summary_list.append(f"- **{_comp7}**: {_sig_count}/3 metrics with significant correlations")
    
    mo.md("\n".join(_summary_list))
    
    mo.md("""
### Key Findings:
- Pearson correlation measures linear relationships
- Spearman correlation measures monotonic (rank-based) relationships
- Rolling correlations show how relationships evolve over time
- Statistical significance (p < 0.05) indicates the correlation is unlikely to be due to random chance
    """)
    
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
