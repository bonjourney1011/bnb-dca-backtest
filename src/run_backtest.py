"""Run all strategies on real BNB data and generate comparison report."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from tabulate import tabulate

from src.data_fetcher import load_data
from src.backtest_engine import run_backtest, BacktestConfig
from src.strategies import ALL_STRATEGIES


def run_all_backtests(monthly_capital: float = 500.0):
    """Run all strategies and return results."""
    df = load_data()
    print(f"Loaded {len(df)} days of BNB/USDT data")
    print(f"Date range: {df.index.min().date()} -> {df.index.max().date()}")
    print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"Monthly capital: ${monthly_capital}")
    print("=" * 80)

    config = BacktestConfig(monthly_capital=monthly_capital, salary_day=5, fee_rate=0.001)

    results = {}
    for name, strategy_fn in ALL_STRATEGIES.items():
        print(f"\nRunning: {name}...")
        result = run_backtest(df, strategy_fn, config, name=name)
        results[name] = result
        m = result.metrics
        print(f"  Total invested: ${m['total_invested']:,.0f}")
        print(f"  Final value: ${m['final_value']:,.0f}")
        print(f"  Total return: {m['total_return_pct']:.1f}%")
        print(f"  CAGR: {m['cagr_pct']:.1f}%")
        print(f"  Sharpe: {m['sharpe_ratio']:.2f}")
        print(f"  Max DD: {m['max_drawdown_pct']:.1f}%")

    # Buy-and-Hold benchmark
    print(f"\nRunning: Buy & Hold benchmark...")
    bh_invested = monthly_capital * len(pd.date_range(df.index.min(), df.index.max(), freq="MS"))
    bh_final = (bh_invested / df['close'].iloc[0]) * df['close'].iloc[-1]

    return results


def generate_comparison_table(results: dict):
    """Generate comparison table of all strategies."""
    rows = []
    for name, result in results.items():
        m = result.metrics
        rows.append({
            "Strategy": name,
            "Invested": f"${m['total_invested']:,.0f}",
            "Final Value": f"${m['final_value']:,.0f}",
            "Return %": f"{m['total_return_pct']:.1f}%",
            "CAGR %": f"{m['cagr_pct']:.1f}%",
            "Sharpe": f"{m['sharpe_ratio']:.2f}",
            "Sortino": f"{m['sortino_ratio']:.2f}",
            "Max DD": f"{m['max_drawdown_pct']:.1f}%",
            "Calmar": f"{m['calmar_ratio']:.2f}",
            "Win Rate": f"{m['win_rate_pct']:.0f}%",
            "Trades": m['total_trades'],
            "Fees $": f"${m['total_fees_usd']:.0f}",
        })

    table_df = pd.DataFrame(rows)
    return table_df


def generate_detailed_analysis(results: dict):
    """Generate detailed analysis text."""
    print("\n" + "=" * 80)
    print("DETAILED RISK-RETURN ANALYSIS (FROM REAL BNB DATA)")
    print("=" * 80)

    # Sort by Sharpe ratio
    sorted_results = sorted(results.items(), key=lambda x: x[1].metrics["sharpe_ratio"], reverse=True)

    print("\n## RANKING BY SHARPE RATIO (Risk-Adjusted Return)")
    for rank, (name, result) in enumerate(sorted_results, 1):
        m = result.metrics
        print(f"\n{'='*60}")
        print(f"#{rank} {name}")
        print(f"{'='*60}")
        print(f"  Return Metrics:")
        print(f"    Total Invested:    ${m['total_invested']:>12,.0f}")
        print(f"    Final Value:       ${m['final_value']:>12,.0f}")
        print(f"    Total Return:      {m['total_return_pct']:>11.1f}%")
        print(f"    CAGR:              {m['cagr_pct']:>11.1f}%")
        print(f"  Risk Metrics:")
        print(f"    Sharpe Ratio:      {m['sharpe_ratio']:>11.2f}")
        print(f"    Sortino Ratio:     {m['sortino_ratio']:>11.2f}")
        print(f"    Max Drawdown:      {m['max_drawdown_pct']:>11.1f}%")
        print(f"    Calmar Ratio:      {m['calmar_ratio']:>11.2f}")
        print(f"    Annual Volatility: {m['annual_volatility_pct']:>11.1f}%")
        print(f"  Trading Stats:")
        print(f"    Win Rate (monthly):{m['win_rate_pct']:>11.0f}%")
        print(f"    Profit Factor:     {m['profit_factor']:>11.2f}")
        print(f"    Total Trades:      {m['total_trades']:>11d}")
        print(f"    Total Fees:        ${m['total_fees_usd']:>10,.0f}")
        if m['max_dd_recovery_days'] is not None:
            print(f"    DD Recovery Days:  {m['max_dd_recovery_days']:>11d}")
        else:
            print(f"    DD Recovery Days:  Not recovered")
        print(f"  Final Position:")
        print(f"    BNB Holdings:      {m['holdings_final']:>11.4f}")
        print(f"    Cash Remaining:    ${m['cash_final']:>10,.0f}")

    # Best in each category
    print("\n" + "=" * 80)
    print("BEST STRATEGY BY CATEGORY")
    print("=" * 80)

    categories = {
        "Highest Total Return": ("total_return_pct", True),
        "Highest CAGR": ("cagr_pct", True),
        "Best Sharpe Ratio": ("sharpe_ratio", True),
        "Best Sortino Ratio": ("sortino_ratio", True),
        "Lowest Max Drawdown": ("max_drawdown_pct", False),
        "Best Calmar Ratio": ("calmar_ratio", True),
        "Highest Win Rate": ("win_rate_pct", True),
        "Best Profit Factor": ("profit_factor", True),
        "Lowest Fees": ("total_fees_usd", False),
    }

    for cat_name, (metric, higher_better) in categories.items():
        if higher_better:
            best = max(results.items(), key=lambda x: x[1].metrics[metric])
        else:
            best = min(results.items(), key=lambda x: x[1].metrics[metric])
        val = best[1].metrics[metric]
        if "pct" in metric:
            print(f"  {cat_name:30s} -> {best[0]:20s} ({val:.1f}%)")
        elif "usd" in metric or "fees" in metric:
            print(f"  {cat_name:30s} -> {best[0]:20s} (${val:,.0f})")
        else:
            print(f"  {cat_name:30s} -> {best[0]:20s} ({val:.2f})")


def generate_monthly_breakdown(results: dict):
    """Show monthly return distribution for top strategies."""
    print("\n" + "=" * 80)
    print("MONTHLY RETURN DISTRIBUTION (Top 3 by Sharpe)")
    print("=" * 80)

    sorted_results = sorted(results.items(), key=lambda x: x[1].metrics["sharpe_ratio"], reverse=True)[:3]

    for name, result in sorted_results:
        portfolio = result.daily_portfolio["portfolio_value"]
        monthly = portfolio.resample("ME").last().pct_change().dropna() * 100

        print(f"\n{name}:")
        print(f"  Mean monthly return:   {monthly.mean():>7.2f}%")
        print(f"  Median monthly return: {monthly.median():>7.2f}%")
        print(f"  Std monthly return:    {monthly.std():>7.2f}%")
        print(f"  Best month:            {monthly.max():>7.2f}% ({monthly.idxmax().strftime('%Y-%m')})")
        print(f"  Worst month:           {monthly.min():>7.2f}% ({monthly.idxmin().strftime('%Y-%m')})")
        print(f"  Months positive:       {(monthly > 0).sum()}/{len(monthly)}")
        print(f"  Months > +10%:         {(monthly > 10).sum()}")
        print(f"  Months < -10%:         {(monthly < -10).sum()}")


def generate_yearly_breakdown(results: dict):
    """Show yearly performance comparison."""
    print("\n" + "=" * 80)
    print("YEARLY PERFORMANCE COMPARISON (CAGR % by year)")
    print("=" * 80)

    years_data = {}
    for name, result in results.items():
        portfolio = result.daily_portfolio["portfolio_value"]
        yearly = portfolio.resample("YE").last()
        yearly_returns = yearly.pct_change().dropna() * 100
        years_data[name] = yearly_returns

    # Build table
    all_years = sorted(set(y for yr in years_data.values() for y in yr.index.year))
    header = ["Strategy"] + [str(y) for y in all_years]
    rows = []
    for name, yearly_ret in years_data.items():
        row = [name]
        for y in all_years:
            match = yearly_ret[yearly_ret.index.year == y]
            if len(match) > 0:
                row.append(f"{match.iloc[0]:.1f}%")
            else:
                row.append("N/A")
        rows.append(row)

    print(tabulate(rows, headers=header, tablefmt="grid"))


def save_results_csv(results: dict, output_dir: str):
    """Save daily portfolio data for each strategy."""
    os.makedirs(output_dir, exist_ok=True)

    for name, result in results.items():
        filename = name.lower().replace(" ", "_").replace("+", "plus").replace("/", "_").replace("&", "and")
        result.daily_portfolio.to_csv(os.path.join(output_dir, f"{filename}_daily.csv"))

    # Save comparison table
    table = generate_comparison_table(results)
    table.to_csv(os.path.join(output_dir, "strategy_comparison.csv"), index=False)
    print(f"\nResults saved to {output_dir}")


if __name__ == "__main__":
    results = run_all_backtests(monthly_capital=500.0)

    print("\n")
    table = generate_comparison_table(results)
    print(tabulate(table.values.tolist(), headers=table.columns.tolist(), tablefmt="grid"))

    generate_detailed_analysis(results)
    generate_monthly_breakdown(results)
    generate_yearly_breakdown(results)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    save_results_csv(results, output_dir)
