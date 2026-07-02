"""Strategy 1: Pure DCA - Buy fixed amount on salary day, hold forever."""

import ta
import pandas as pd


def pure_dca_strategy(date: pd.Timestamp, row, df: pd.DataFrame, state: dict, config) -> list:
    """Buy full monthly capital on salary day (or first trading day after)."""
    signals = []
    month_key = (date.year, date.month)

    if date.day >= config.salary_day and month_key not in state.get("dca_bought", set()):
        state.setdefault("dca_bought", set()).add(month_key)
        signals.append(("buy", config.monthly_capital))

    return signals
