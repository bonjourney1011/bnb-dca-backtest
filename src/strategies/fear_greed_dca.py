"""Strategy 6: Fear & Greed DCA - Only buy when Fear & Greed Index < 50."""

import os
import pandas as pd


def _load_fear_greed():
    """Load cached Fear & Greed Index data."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")
    filepath = os.path.join(data_dir, "fear_greed_index.csv")
    if os.path.exists(filepath):
        fg = pd.read_csv(filepath, index_col="timestamp", parse_dates=True)
        return fg
    return pd.DataFrame()


def fear_greed_dca_strategy(date: pd.Timestamp, row, df: pd.DataFrame, state: dict, config) -> list:
    """
    Pure DCA on salary day, but:
    - If F&G < 30 (Extreme Fear): buy 130% of normal
    - If F&G 30-50 (Fear): buy 100% of normal
    - If F&G 50-70 (Greed): buy 70% of normal
    - If F&G > 70 (Extreme Greed): buy 50% of normal, defer rest

    Deferred capital accumulates and deploys on next Fear day.
    """
    signals = []
    month_key = (date.year, date.month)

    # Load F&G data
    if "fg_data" not in state:
        state["fg_data"] = _load_fear_greed()
        state["fg_reserve"] = 0.0
        state["fg_bought"] = set()

    fg_df = state["fg_data"]

    # Get F&G value for this date
    fg_value = 50  # Default neutral
    if not fg_df.empty:
        # Find closest date
        date_normalized = date.normalize()
        if date_normalized in fg_df.index:
            fg_value = fg_df.loc[date_normalized, "fear_greed"]
        else:
            # Try nearest date within 3 days
            mask = abs((fg_df.index - date_normalized).days) <= 3
            if mask.any():
                nearest = fg_df[mask].index[-1]
                fg_value = fg_df.loc[nearest, "fear_greed"]

    if isinstance(fg_value, pd.Series):
        fg_value = fg_value.iloc[0]

    # Salary day: decide allocation based on F&G
    if date.day >= config.salary_day and month_key not in state["fg_bought"]:
        state["fg_bought"].add(month_key)
        available = config.monthly_capital + state["fg_reserve"]

        if fg_value < 30:  # Extreme Fear - deploy aggressively
            buy_amount = min(available, config.monthly_capital * 1.3)
            state["fg_reserve"] = max(0, available - buy_amount)
        elif fg_value < 50:  # Fear - normal buy
            buy_amount = config.monthly_capital
            state["fg_reserve"] = max(0, available - buy_amount)
        elif fg_value < 70:  # Greed - reduce buy
            buy_amount = config.monthly_capital * 0.7
            state["fg_reserve"] += config.monthly_capital * 0.3
        else:  # Extreme Greed - minimal buy
            buy_amount = config.monthly_capital * 0.5
            state["fg_reserve"] += config.monthly_capital * 0.5

        if buy_amount > 0:
            signals.append(("buy", buy_amount))

    # Mid-month: deploy reserve if extreme fear hits
    mid_key = f"fg_mid_{date.year}_{date.month}"
    if fg_value < 25 and state["fg_reserve"] > config.monthly_capital * 0.3 and mid_key not in state["fg_bought"]:
        state["fg_bought"].add(mid_key)
        deploy = state["fg_reserve"] * 0.5
        state["fg_reserve"] -= deploy
        signals.append(("buy", deploy))

    return signals
