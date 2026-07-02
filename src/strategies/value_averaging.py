"""Strategy 3: Value Averaging - Target linear portfolio growth."""

import pandas as pd


def value_averaging_strategy(date: pd.Timestamp, row, df: pd.DataFrame, state: dict, config) -> list:
    """Adjust buy amount to maintain linear portfolio growth target."""
    signals = []
    month_key = (date.year, date.month)

    if date.day >= config.salary_day and month_key not in state.get("va_bought", set()):
        state.setdefault("va_bought", set()).add(month_key)
        state.setdefault("va_month_count", 0)
        state["va_month_count"] += 1

        # Target: portfolio should grow by monthly_capital each month
        target_value = config.monthly_capital * state["va_month_count"]
        current_holdings = state.get("va_holdings_value", 0)

        # Estimate current value based on price
        if "va_qty" not in state:
            state["va_qty"] = 0.0
            state["va_cash_reserve"] = 0.0

        current_value = state["va_qty"] * row["close"] + state["va_cash_reserve"]
        gap = target_value - current_value

        if gap > 0:
            # Need to buy more - cap at 2x monthly capital to prevent huge buys
            buy_amount = min(gap, config.monthly_capital * 2.0)
            signals.append(("buy", buy_amount))
            # Track internally
            fee = buy_amount * config.fee_rate
            state["va_qty"] += (buy_amount - fee) / row["close"]
        else:
            # Portfolio ahead of target - invest minimum (25%)
            buy_amount = config.monthly_capital * 0.25
            signals.append(("buy", buy_amount))
            fee = buy_amount * config.fee_rate
            state["va_qty"] += (buy_amount - fee) / row["close"]

    return signals
