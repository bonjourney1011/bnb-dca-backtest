"""Strategy 2: DCA + RSI Oversold - Base DCA + extra buy when RSI < 40."""

import ta
import pandas as pd
import numpy as np


def dca_rsi_strategy(date: pd.Timestamp, row, df: pd.DataFrame, state: dict, config) -> list:
    """Buy base DCA on salary day. Buy extra 50% if RSI(14) < 40."""
    signals = []
    month_key = (date.year, date.month)

    # Pre-compute RSI once
    if "rsi" not in state["indicators"]:
        state["indicators"]["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

    rsi_series = state["indicators"]["rsi"]
    current_rsi = rsi_series.get(date, 50)

    if pd.isna(current_rsi):
        current_rsi = 50

    if date.day >= config.salary_day and month_key not in state.get("dca_rsi_bought", set()):
        state.setdefault("dca_rsi_bought", set()).add(month_key)

        # Base DCA: 80% of capital
        base = config.monthly_capital * 0.8
        signals.append(("buy", base))

        # Extra buy if oversold
        if current_rsi < 40:
            extra = config.monthly_capital * 0.2 + config.monthly_capital * 0.3  # Use remaining + extra from reserve
            signals.append(("buy", min(extra, config.monthly_capital * 0.5)))
        else:
            # Still invest remaining 20%
            signals.append(("buy", config.monthly_capital * 0.2))

    # Mid-month RSI dip buy (if RSI < 30 and haven't done mid-month buy)
    mid_key = f"mid_{date.year}_{date.month}"
    if current_rsi < 30 and mid_key not in state.get("dca_rsi_bought", set()):
        if date.day > config.salary_day + 5:
            state.setdefault("dca_rsi_bought", set()).add(mid_key)
            # Use small amount for dip buying
            signals.append(("buy", config.monthly_capital * 0.1))

    return signals
