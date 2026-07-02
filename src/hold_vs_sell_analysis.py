"""
Analyze Hold Forever vs various Sell strategies.

Compare:
1. Hold forever (never sell)
2. Sell after N months holding
3. Take profit at +X%
4. Sell partial at milestones
5. Cycle strategy (accumulate → sell → re-accumulate)
6. Trailing stop sell
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from tabulate import tabulate
from src.data_fetcher import load_data


def strategy_hold_forever(df, monthly_capital=500.0, salary_day=5):
    """Baseline: Buy on salary day, never sell."""
    cash = 0.0
    holdings = 0.0
    total_invested = 0.0
    months_bought = set()
    records = []

    for date, row in df.iterrows():
        month_key = (date.year, date.month)
        if date.day >= salary_day and month_key not in months_bought:
            months_bought.add(month_key)
            cash += monthly_capital
            total_invested += monthly_capital
            price = row["close"]
            fee = monthly_capital * 0.001
            qty = (monthly_capital - fee) / price
            holdings += qty
            cash -= monthly_capital

        records.append({
            "date": date,
            "portfolio": max(0, cash) + holdings * row["close"],
            "holdings": holdings,
            "cash": max(0, cash),
            "total_invested": total_invested,
            "realized_profit": 0,
        })

    return pd.DataFrame(records).set_index("date")


def strategy_take_profit(df, monthly_capital=500.0, salary_day=5, take_profit_pct=50.0, sell_pct=0.5):
    """Sell sell_pct of holdings when unrealized gain exceeds take_profit_pct."""
    cash = 0.0
    holdings = 0.0
    total_invested = 0.0
    cost_basis = 0.0  # Total cost of current holdings
    realized_profit = 0.0
    months_bought = set()
    last_sell_month = None
    records = []

    for date, row in df.iterrows():
        month_key = (date.year, date.month)
        price = row["close"]

        # Buy on salary day
        if date.day >= salary_day and month_key not in months_bought:
            months_bought.add(month_key)
            cash += monthly_capital
            total_invested += monthly_capital
            fee = monthly_capital * 0.001
            qty = (monthly_capital - fee) / price
            holdings += qty
            cost_basis += monthly_capital
            cash -= monthly_capital

        # Check take profit
        if holdings > 0 and cost_basis > 0:
            current_value = holdings * price
            unrealized_gain_pct = (current_value / cost_basis - 1) * 100

            # Only sell if gain > threshold and at least 1 month since last sell
            if unrealized_gain_pct >= take_profit_pct and month_key != last_sell_month:
                sell_qty = holdings * sell_pct
                sell_value = sell_qty * price
                sell_fee = sell_value * 0.001
                net_sell = sell_value - sell_fee

                # Proportional cost basis
                sell_cost = cost_basis * sell_pct
                realized_profit += (net_sell - sell_cost)

                holdings -= sell_qty
                cash += net_sell
                cost_basis -= sell_cost
                last_sell_month = month_key

        records.append({
            "date": date,
            "portfolio": max(0, cash) + holdings * price,
            "holdings": holdings,
            "cash": max(0, cash),
            "total_invested": total_invested,
            "realized_profit": realized_profit,
        })

    return pd.DataFrame(records).set_index("date")


def strategy_periodic_sell(df, monthly_capital=500.0, salary_day=5, hold_months=12, sell_pct=0.25):
    """Hold for N months, then sell sell_pct of holdings periodically."""
    cash = 0.0
    holdings = 0.0
    total_invested = 0.0
    realized_profit = 0.0
    cost_basis = 0.0
    months_bought = set()
    buy_count = 0
    records = []

    for date, row in df.iterrows():
        month_key = (date.year, date.month)
        price = row["close"]

        # Buy on salary day
        if date.day >= salary_day and month_key not in months_bought:
            months_bought.add(month_key)
            cash += monthly_capital
            total_invested += monthly_capital
            fee = monthly_capital * 0.001
            qty = (monthly_capital - fee) / price
            holdings += qty
            cost_basis += monthly_capital
            cash -= monthly_capital
            buy_count += 1

        # Sell periodically after hold_months
        if buy_count > 0 and buy_count % hold_months == 0 and date.day == salary_day:
            if holdings > 0 and cost_basis > 0:
                sell_qty = holdings * sell_pct
                sell_value = sell_qty * price
                sell_fee = sell_value * 0.001
                net_sell = sell_value - sell_fee

                sell_cost = cost_basis * sell_pct
                realized_profit += (net_sell - sell_cost)

                holdings -= sell_qty
                cash += net_sell
                cost_basis -= sell_cost

        records.append({
            "date": date,
            "portfolio": max(0, cash) + holdings * price,
            "holdings": holdings,
            "cash": max(0, cash),
            "total_invested": total_invested,
            "realized_profit": realized_profit,
        })

    return pd.DataFrame(records).set_index("date")


def strategy_trailing_stop(df, monthly_capital=500.0, salary_day=5, trail_pct=30.0, sell_pct=0.5):
    """Sell sell_pct when price drops trail_pct from ATH. Re-buy when price recovers."""
    cash = 0.0
    holdings = 0.0
    total_invested = 0.0
    realized_profit = 0.0
    cost_basis = 0.0
    months_bought = set()
    price_ath = 0.0
    in_cash_mode = False
    records = []

    for date, row in df.iterrows():
        month_key = (date.year, date.month)
        price = row["close"]

        # Track ATH
        if price > price_ath:
            price_ath = price

        # Buy on salary day (always DCA regardless of mode)
        if date.day >= salary_day and month_key not in months_bought:
            months_bought.add(month_key)
            cash += monthly_capital
            total_invested += monthly_capital
            fee = monthly_capital * 0.001
            qty = (monthly_capital - fee) / price
            holdings += qty
            cost_basis += monthly_capital
            cash -= monthly_capital

        # Trailing stop: sell when price drops trail_pct from ATH
        if not in_cash_mode and price_ath > 0:
            drop_from_ath = (1 - price / price_ath) * 100
            if drop_from_ath >= trail_pct and holdings > 0:
                sell_qty = holdings * sell_pct
                sell_value = sell_qty * price
                sell_fee = sell_value * 0.001
                net_sell = sell_value - sell_fee

                sell_cost = cost_basis * sell_pct if cost_basis > 0 else 0
                realized_profit += (net_sell - sell_cost)

                holdings -= sell_qty
                cash += net_sell
                cost_basis = max(0, cost_basis - sell_cost)
                in_cash_mode = True

        # Re-enter: buy back when price recovers 10% from local low
        if in_cash_mode and cash > monthly_capital:
            # Simple: wait for price to be above 20-day moving avg
            if len(df.loc[:date]) >= 20:
                ma20 = df.loc[:date]["close"].tail(20).mean()
                if price > ma20 * 1.05:
                    buy_amount = cash * 0.8  # Deploy 80% of cash
                    fee = buy_amount * 0.001
                    qty = (buy_amount - fee) / price
                    holdings += qty
                    cost_basis += buy_amount
                    cash -= buy_amount
                    in_cash_mode = False
                    price_ath = price  # Reset ATH

        records.append({
            "date": date,
            "portfolio": max(0, cash) + holdings * price,
            "holdings": holdings,
            "cash": max(0, cash),
            "total_invested": total_invested,
            "realized_profit": realized_profit,
        })

    return pd.DataFrame(records).set_index("date")


def strategy_milestone_sell(df, monthly_capital=500.0, salary_day=5):
    """Sell fixed portions at price milestones."""
    cash = 0.0
    holdings = 0.0
    total_invested = 0.0
    realized_profit = 0.0
    cost_basis = 0.0
    months_bought = set()
    milestones_hit = set()
    records = []

    # Define milestones: when portfolio reaches Nx invested, sell Y%
    milestones = [
        (2.0, 0.10),   # Portfolio = 2x invested → sell 10%
        (3.0, 0.10),   # Portfolio = 3x → sell 10%
        (5.0, 0.15),   # Portfolio = 5x → sell 15%
        (8.0, 0.15),   # Portfolio = 8x → sell 15%
        (10.0, 0.20),  # Portfolio = 10x → sell 20%
    ]

    for date, row in df.iterrows():
        month_key = (date.year, date.month)
        price = row["close"]

        if date.day >= salary_day and month_key not in months_bought:
            months_bought.add(month_key)
            cash += monthly_capital
            total_invested += monthly_capital
            fee = monthly_capital * 0.001
            qty = (monthly_capital - fee) / price
            holdings += qty
            cost_basis += monthly_capital
            cash -= monthly_capital

        # Check milestones
        if total_invested > 0 and holdings > 0:
            portfolio = holdings * price + max(0, cash)
            multiple = portfolio / total_invested

            for threshold, sell_frac in milestones:
                if multiple >= threshold and threshold not in milestones_hit:
                    milestones_hit.add(threshold)
                    sell_qty = holdings * sell_frac
                    sell_value = sell_qty * price
                    sell_fee = sell_value * 0.001
                    net_sell = sell_value - sell_fee

                    sell_cost = cost_basis * sell_frac if cost_basis > 0 else 0
                    realized_profit += (net_sell - sell_cost)

                    holdings -= sell_qty
                    cash += net_sell
                    cost_basis = max(0, cost_basis - sell_cost)

        records.append({
            "date": date,
            "portfolio": max(0, cash) + holdings * price,
            "holdings": holdings,
            "cash": max(0, cash),
            "total_invested": total_invested,
            "realized_profit": realized_profit,
        })

    return pd.DataFrame(records).set_index("date")


def calculate_result_metrics(result_df, name):
    """Calculate key metrics from result DataFrame."""
    portfolio = result_df["portfolio"]
    invested = result_df["total_invested"].iloc[-1]
    final = portfolio.iloc[-1]
    total_return = (final / invested - 1) * 100 if invested > 0 else 0

    days = (result_df.index[-1] - result_df.index[0]).days
    years = days / 365.25
    cagr = (final / invested) ** (1 / years) - 1 if years > 0 and invested > 0 else 0

    active = portfolio[portfolio > 0]
    cummax = active.cummax()
    dd = ((active - cummax) / cummax)
    max_dd = dd.min() * 100 if len(dd) > 0 else 0

    realized = result_df["realized_profit"].iloc[-1]
    holdings_final = result_df["holdings"].iloc[-1]
    cash_final = result_df["cash"].iloc[-1]

    return {
        "Strategy": name,
        "Invested": f"${invested:,.0f}",
        "Final Value": f"${final:,.0f}",
        "Return %": f"{total_return:.1f}%",
        "CAGR %": f"{cagr * 100:.1f}%",
        "Max DD %": f"{max_dd:.1f}%",
        "Realized $": f"${realized:,.0f}",
        "BNB Left": f"{holdings_final:.2f}",
        "Cash Left": f"${cash_final:,.0f}",
    }


if __name__ == "__main__":
    df = load_data()
    print(f"Data: {len(df)} days, {df.index.min().date()} → {df.index.max().date()}\n")

    print("=" * 100)
    print("HOLD FOREVER vs SELL STRATEGIES — Real BNB Data 2020-2026")
    print("$500/month DCA on 5th, Binance 0.1% fee")
    print("=" * 100)

    strategies = {
        "1. Hold Forever": strategy_hold_forever(df),
        "2. Take Profit 50% (sell 50%)": strategy_take_profit(df, take_profit_pct=50, sell_pct=0.5),
        "3. Take Profit 100% (sell 30%)": strategy_take_profit(df, take_profit_pct=100, sell_pct=0.3),
        "4. Take Profit 200% (sell 25%)": strategy_take_profit(df, take_profit_pct=200, sell_pct=0.25),
        "5. Sell 25% every 12 months": strategy_periodic_sell(df, hold_months=12, sell_pct=0.25),
        "6. Sell 25% every 6 months": strategy_periodic_sell(df, hold_months=6, sell_pct=0.25),
        "7. Trailing Stop -30% (sell 50%)": strategy_trailing_stop(df, trail_pct=30, sell_pct=0.5),
        "8. Trailing Stop -40% (sell 50%)": strategy_trailing_stop(df, trail_pct=40, sell_pct=0.5),
        "9. Milestone Sell (2x/3x/5x/8x/10x)": strategy_milestone_sell(df),
    }

    results = []
    for name, result_df in strategies.items():
        metrics = calculate_result_metrics(result_df, name)
        results.append(metrics)

    print("\n" + tabulate(results, headers="keys", tablefmt="grid"))

    # Detailed analysis
    print("\n" + "=" * 100)
    print("CHI TIẾT PHÂN TÍCH")
    print("=" * 100)

    hold_final = float(results[0]["Final Value"].replace("$", "").replace(",", ""))

    for r in results:
        final = float(r["Final Value"].replace("$", "").replace(",", ""))
        diff = final - hold_final
        diff_pct = (final / hold_final - 1) * 100
        realized = r["Realized $"]
        print(f"\n{r['Strategy']}:")
        print(f"  Final: {r['Final Value']} | Return: {r['Return %']} | Max DD: {r['Max DD %']}")
        print(f"  vs Hold Forever: {'+'if diff>=0 else ''}{diff:,.0f} ({diff_pct:+.1f}%)")
        print(f"  Realized profit: {realized} | BNB remaining: {r['BNB Left']} | Cash: {r['Cash Left']}")

    # Save results
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    pd.DataFrame(results).to_csv(os.path.join(output_dir, "hold_vs_sell_comparison.csv"), index=False)
    print(f"\nResults saved to {output_dir}/hold_vs_sell_comparison.csv")
