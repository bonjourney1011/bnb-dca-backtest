"""Strategy 5: Hybrid 80/15/5 - DCA base + RSI tactical + dry powder."""

import ta
import pandas as pd


def hybrid_strategy(date: pd.Timestamp, row, df: pd.DataFrame, state: dict, config) -> list:
    """
    80% capital -> Pure DCA on salary day
    15% capital -> Buy when RSI < 35 within ±5 days of salary day
    5% capital -> Panic buy when RSI < 25 (anytime)
    """
    signals = []
    month_key = (date.year, date.month)
    price = row["close"]

    # Pre-compute RSI
    if "rsi" not in state["indicators"]:
        state["indicators"]["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

    rsi = state["indicators"]["rsi"].get(date, 50)
    if pd.isna(rsi):
        rsi = 50

    state.setdefault("hybrid_dca", set())
    state.setdefault("hybrid_tactical", set())
    state.setdefault("hybrid_panic", set())

    # 80% DCA on salary day
    if date.day >= config.salary_day and month_key not in state["hybrid_dca"]:
        state["hybrid_dca"].add(month_key)
        dca_amount = config.monthly_capital * 0.80
        signals.append(("buy", dca_amount))

    # 15% tactical RSI buy within ±5 days of salary day
    in_window = abs(date.day - config.salary_day) <= 5 or (
        config.salary_day > 25 and date.day <= 5  # Handle month wrap
    )
    if in_window and rsi < 35 and month_key not in state["hybrid_tactical"]:
        state["hybrid_tactical"].add(month_key)
        tactical_amount = config.monthly_capital * 0.15
        signals.append(("buy", tactical_amount))

    # If tactical window passed without trigger, deploy on last day of window
    if date.day == config.salary_day + 5 and month_key not in state["hybrid_tactical"]:
        state["hybrid_tactical"].add(month_key)
        signals.append(("buy", config.monthly_capital * 0.15))

    # 5% panic buy: RSI < 25 anytime (max once per month)
    if rsi < 25 and month_key not in state["hybrid_panic"]:
        state["hybrid_panic"].add(month_key)
        signals.append(("buy", config.monthly_capital * 0.05))

    return signals
