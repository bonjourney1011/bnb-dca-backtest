"""Strategy 4: Grid Trading on DCA Day - Split buys + take profit grids."""

import pandas as pd
import numpy as np


def grid_trading_strategy(date: pd.Timestamp, row, df: pd.DataFrame, state: dict, config) -> list:
    """On salary day: place 3 buy levels. Sell grids at +5% per level."""
    signals = []
    month_key = (date.year, date.month)
    price = row["close"]

    # Initialize grid state
    state.setdefault("grid_orders", [])
    state.setdefault("grid_bought", set())

    # On salary day: set up buy grid
    if date.day >= config.salary_day and month_key not in state.get("grid_bought", set()):
        state.setdefault("grid_bought", set()).add(month_key)

        # Split capital into 3 levels
        level1_amount = config.monthly_capital * 0.40  # Buy at current price
        level2_amount = config.monthly_capital * 0.35  # Buy at -3%
        level3_amount = config.monthly_capital * 0.25  # Buy at -6%

        # Level 1: buy immediately
        signals.append(("buy", level1_amount))
        state["grid_orders"].append({
            "buy_price": price,
            "amount": level1_amount,
            "target_sell_price": price * 1.05,
            "qty": (level1_amount * (1 - config.fee_rate)) / price,
            "filled": True
        })

        # Level 2 & 3: limit buy orders
        state["grid_orders"].append({
            "trigger_price": price * 0.97,
            "amount": level2_amount,
            "target_sell_price": price * 0.97 * 1.05,
            "filled": False,
            "type": "limit_buy"
        })
        state["grid_orders"].append({
            "trigger_price": price * 0.94,
            "amount": level3_amount,
            "target_sell_price": price * 0.94 * 1.05,
            "filled": False,
            "type": "limit_buy"
        })

    # Check pending limit buy orders
    for order in state["grid_orders"]:
        if not order.get("filled") and order.get("type") == "limit_buy":
            if row["low"] <= order.get("trigger_price", 0):
                order["filled"] = True
                order["buy_price"] = order["trigger_price"]
                order["qty"] = (order["amount"] * (1 - config.fee_rate)) / order["trigger_price"]
                signals.append(("buy", order["amount"]))

    # Check take profit orders
    filled_sells = []
    for i, order in enumerate(state["grid_orders"]):
        if order.get("filled") and order.get("qty", 0) > 0:
            if row["high"] >= order.get("target_sell_price", float("inf")):
                sell_value = order["qty"] * order["target_sell_price"]
                signals.append(("sell", sell_value))
                order["qty"] = 0
                filled_sells.append(i)

    # Clean up filled sell orders
    state["grid_orders"] = [o for i, o in enumerate(state["grid_orders"])
                           if i not in filled_sells or o.get("qty", 0) > 0]

    # Keep grid orders manageable
    if len(state["grid_orders"]) > 50:
        state["grid_orders"] = state["grid_orders"][-30:]

    return signals
