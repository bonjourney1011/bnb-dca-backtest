"""Generate visualization charts from backtest results."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
STRATEGY_FILES = {
    "Pure DCA": "pure_dca_daily.csv",
    "DCA + RSI": "dca_plus_rsi_daily.csv",
    "Value Averaging": "value_averaging_daily.csv",
    "Grid Trading": "grid_trading_daily.csv",
    "Hybrid 80/15/5": "hybrid_80_15_5_daily.csv",
    "Fear & Greed DCA": "fear_and_greed_dca_daily.csv",
}

COLORS = {
    "Pure DCA": "#2196F3",
    "DCA + RSI": "#FF9800",
    "Value Averaging": "#4CAF50",
    "Grid Trading": "#9C27B0",
    "Hybrid 80/15/5": "#F44336",
    "Fear & Greed DCA": "#00BCD4",
}


def load_all_results():
    results = {}
    for name, filename in STRATEGY_FILES.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, index_col="date", parse_dates=True)
            results[name] = df
    return results


def plot_equity_curves(results):
    """Equity curves for all strategies."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[2, 1])

    for name, df in results.items():
        ax1.plot(df.index, df["portfolio_value"], label=name, color=COLORS.get(name, "gray"), linewidth=1.5)

    # Also plot total invested
    sample = list(results.values())[0]
    ax1.plot(sample.index, sample["total_invested"], label="Total Invested", color="gray", linestyle="--", linewidth=1)

    ax1.set_title("BNB Trading Strategies - Equity Curves (2020-2026)\n$500/month DCA on 5th, Real Binance Data", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Portfolio Value (USD)")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # BNB price on secondary axis
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
    bnb = pd.read_csv(os.path.join(data_dir, "bnb_usdt_daily.csv"), index_col="timestamp", parse_dates=True)
    ax1b = ax1.twinx()
    ax1b.plot(bnb.index, bnb["close"], color="gold", alpha=0.3, linewidth=0.8, label="BNB Price")
    ax1b.set_ylabel("BNB Price (USD)", color="gold")
    ax1b.tick_params(axis="y", labelcolor="gold")

    # Drawdown chart
    for name, df in results.items():
        if name == "Grid Trading":
            continue
        pv = df["portfolio_value"]
        cummax = pv.cummax()
        dd = (pv - cummax) / cummax * 100
        ax2.fill_between(df.index, dd, 0, alpha=0.3, color=COLORS.get(name, "gray"), label=name)

    ax2.set_title("Drawdown (%)", fontsize=12)
    ax2.set_ylabel("Drawdown %")
    ax2.legend(loc="lower left", fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "equity_curves.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filepath}")


def plot_monthly_returns_heatmap(results):
    """Monthly returns heatmap for top strategy."""
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))

    for idx, name in enumerate(["Pure DCA", "Hybrid 80/15/5"]):
        if name not in results:
            continue
        df = results[name]
        monthly = df["portfolio_value"].resample("ME").last().pct_change().dropna() * 100

        # Pivot to year x month
        monthly_df = pd.DataFrame({"return": monthly})
        monthly_df["year"] = monthly_df.index.year
        monthly_df["month"] = monthly_df.index.month
        pivot = monthly_df.pivot_table(index="year", columns="month", values="return")

        ax = axes[idx]
        im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto", vmin=-40, vmax=40)

        ax.set_xticks(range(12))
        ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_title(f"{name} - Monthly Returns (%)", fontsize=12, fontweight="bold")

        # Add text annotations
        for i in range(len(pivot.index)):
            for j in range(12):
                val = pivot.values[i, j] if j < pivot.shape[1] else np.nan
                if not np.isnan(val):
                    color = "white" if abs(val) > 25 else "black"
                    ax.text(j, i, f"{val:.0f}%", ha="center", va="center", fontsize=7, color=color)

        fig.colorbar(im, ax=ax, label="Return %")

    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "monthly_returns_heatmap.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filepath}")


def plot_risk_return_scatter(results):
    """Risk-return scatter plot."""
    fig, ax = plt.subplots(figsize=(10, 8))

    for name, df in results.items():
        pv = df["portfolio_value"]
        active = pv[pv > 0]
        returns = active.pct_change().dropna()
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()

        annual_vol = returns.std() * np.sqrt(252) * 100
        total_return = (pv.iloc[-1] / df["total_invested"].iloc[-1] - 1) * 100

        cummax = active.cummax()
        dd = ((active - cummax) / cummax).min() * 100

        ax.scatter(annual_vol, total_return, s=200, color=COLORS.get(name, "gray"),
                  edgecolors="black", linewidth=1, zorder=5)
        ax.annotate(name, (annual_vol, total_return), fontsize=9,
                   textcoords="offset points", xytext=(10, 5))

        # Add MaxDD as text
        ax.annotate(f"DD:{dd:.0f}%", (annual_vol, total_return),
                   fontsize=7, color="red", textcoords="offset points", xytext=(10, -10))

    ax.set_xlabel("Annual Volatility (%)", fontsize=12)
    ax.set_ylabel("Total Return (%)", fontsize=12)
    ax.set_title("Risk-Return Profile: BNB Strategies (2020-2026)\nBubble = Strategy, Red = Max Drawdown", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "risk_return_scatter.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filepath}")


def plot_accumulation_comparison(results):
    """BNB accumulation over time."""
    fig, ax = plt.subplots(figsize=(14, 7))

    for name, df in results.items():
        ax.plot(df.index, df["holdings"], label=name, color=COLORS.get(name, "gray"), linewidth=1.5)

    ax.set_title("BNB Accumulation Over Time\n$500/month starting Jan 2020", fontsize=13, fontweight="bold")
    ax.set_ylabel("BNB Holdings (units)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "bnb_accumulation.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filepath}")


def plot_strategy_comparison_bar(results):
    """Bar chart comparing key metrics across strategies."""
    metrics_data = {}
    for name, df in results.items():
        pv = df["portfolio_value"]
        active = pv[pv > 0]
        returns = active.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        invested = df["total_invested"].iloc[-1]

        rf_daily = 0.04 / 252
        excess = returns - rf_daily
        sharpe = np.sqrt(252) * excess.mean() / excess.std() if excess.std() > 0 else 0

        cummax = active.cummax()
        dd = ((active - cummax) / cummax).min() * 100

        total_ret = (pv.iloc[-1] / invested - 1) * 100

        metrics_data[name] = {
            "Total Return %": total_ret,
            "Sharpe": sharpe,
            "Max DD %": dd,
            "Final Value $K": pv.iloc[-1] / 1000,
        }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    metric_names = ["Total Return %", "Sharpe", "Max DD %", "Final Value $K"]

    for ax, metric in zip(axes.flat, metric_names):
        names = list(metrics_data.keys())
        values = [metrics_data[n][metric] for n in names]
        colors = [COLORS.get(n, "gray") for n in names]

        bars = ax.barh(names, values, color=colors, edgecolor="black", linewidth=0.5)
        ax.set_title(metric, fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="x")

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + (max(values) - min(values)) * 0.02, bar.get_y() + bar.get_height()/2,
                   f"{val:.1f}", va="center", fontsize=8)

    plt.suptitle("Strategy Comparison Dashboard", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "strategy_comparison_bars.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filepath}")


if __name__ == "__main__":
    results = load_all_results()
    print(f"Loaded {len(results)} strategy results")

    plot_equity_curves(results)
    plot_monthly_returns_heatmap(results)
    plot_risk_return_scatter(results)
    plot_accumulation_comparison(results)
    plot_strategy_comparison_bar(results)

    print("\nAll charts generated!")
