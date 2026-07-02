"""Backtesting engine for DCA-based trading strategies on daily OHLCV data."""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field


@dataclass
class TradeLog:
    date: pd.Timestamp
    action: str  # "buy" or "sell"
    price: float
    amount_usd: float
    quantity: float
    fee: float
    portfolio_value: float
    cash: float
    holdings: float
    strategy_label: str = ""


@dataclass
class BacktestConfig:
    monthly_capital: float = 500.0  # USD injected on salary day
    salary_day: int = 5
    fee_rate: float = 0.001  # 0.1% Binance fee
    initial_cash: float = 0.0
    initial_holdings: float = 0.0


@dataclass
class BacktestResult:
    name: str
    config: BacktestConfig
    trades: list = field(default_factory=list)
    daily_portfolio: pd.DataFrame = field(default_factory=pd.DataFrame)
    metrics: dict = field(default_factory=dict)


def run_backtest(df: pd.DataFrame, strategy_fn, config: BacktestConfig, name: str = "Strategy") -> BacktestResult:
    """
    Run backtest on daily OHLCV data.

    strategy_fn(date, row, state, config) -> list of (action, amount_usd)
    where action is "buy" or "sell", amount_usd is the dollar amount.
    """
    cash = config.initial_cash
    holdings = config.initial_holdings
    trades = []
    daily_records = []
    total_invested = 0.0
    capital_injected_dates = set()

    # Pre-compute any indicators the strategy needs
    state = {"indicators": {}, "month_invested": set()}

    for i, (date, row) in enumerate(df.iterrows()):
        price = row["close"]

        # Inject monthly capital on salary day
        day = date.day
        month_key = (date.year, date.month)

        if day >= config.salary_day and month_key not in capital_injected_dates:
            cash += config.monthly_capital
            total_invested += config.monthly_capital
            capital_injected_dates.add(month_key)

        # Get strategy signals
        signals = strategy_fn(date, row, df, state, config)

        for action, amount_usd in signals:
            if action == "buy" and amount_usd > 0 and cash >= amount_usd:
                fee = amount_usd * config.fee_rate
                net_amount = amount_usd - fee
                qty = net_amount / price
                holdings += qty
                cash -= amount_usd

                trades.append(TradeLog(
                    date=date, action="buy", price=price,
                    amount_usd=amount_usd, quantity=qty, fee=fee,
                    portfolio_value=cash + holdings * price,
                    cash=cash, holdings=holdings,
                    strategy_label=name
                ))

            elif action == "sell" and amount_usd > 0 and holdings > 0:
                qty_to_sell = min(amount_usd / price, holdings)
                gross = qty_to_sell * price
                fee = gross * config.fee_rate
                net = gross - fee
                holdings -= qty_to_sell
                cash += net

                trades.append(TradeLog(
                    date=date, action="sell", price=price,
                    amount_usd=gross, quantity=qty_to_sell, fee=fee,
                    portfolio_value=cash + holdings * price,
                    cash=cash, holdings=holdings,
                    strategy_label=name
                ))

        portfolio_value = cash + holdings * price

        daily_records.append({
            "date": date,
            "price": price,
            "cash": cash,
            "holdings": holdings,
            "portfolio_value": portfolio_value,
            "total_invested": total_invested,
        })

    daily_df = pd.DataFrame(daily_records).set_index("date")
    daily_df["daily_return"] = daily_df["portfolio_value"].pct_change()
    daily_df["cumulative_return"] = (daily_df["portfolio_value"] / daily_df["total_invested"].replace(0, np.nan)) - 1

    result = BacktestResult(name=name, config=config, trades=trades, daily_portfolio=daily_df)
    result.metrics = calculate_metrics(daily_df, total_invested, trades)
    return result


def calculate_metrics(daily_df: pd.DataFrame, total_invested: float, trades: list) -> dict:
    """Calculate comprehensive risk-return metrics."""
    portfolio = daily_df["portfolio_value"]

    # Filter out periods with zero portfolio value (before first investment)
    active_portfolio = portfolio[portfolio > 0]
    returns = active_portfolio.pct_change().dropna()
    # Remove inf/nan returns
    returns = returns.replace([np.inf, -np.inf], np.nan).dropna()

    # Basic returns
    final_value = portfolio.iloc[-1]
    total_return = (final_value / total_invested - 1) if total_invested > 0 else 0

    # CAGR - from first investment to end
    first_invest_idx = active_portfolio.index[0] if len(active_portfolio) > 0 else daily_df.index[0]
    days = (daily_df.index[-1] - first_invest_idx).days
    years = days / 365.25
    cagr = (final_value / total_invested) ** (1 / years) - 1 if years > 0 and total_invested > 0 else 0

    # Sharpe Ratio (annualized, risk-free = 4%)
    rf_daily = 0.04 / 252
    excess_returns = returns - rf_daily
    std = excess_returns.std()
    sharpe = np.sqrt(252) * excess_returns.mean() / std if std > 0 and not np.isnan(std) else 0

    # Sortino Ratio
    downside = returns[returns < rf_daily] - rf_daily
    down_std = downside.std()
    sortino = np.sqrt(252) * excess_returns.mean() / down_std if len(downside) > 0 and down_std > 0 and not np.isnan(down_std) else 0

    # Max Drawdown
    cummax = active_portfolio.cummax()
    drawdown = (active_portfolio - cummax) / cummax
    max_drawdown = drawdown.min() if len(drawdown) > 0 else 0

    # Calmar Ratio
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

    # Win Rate (monthly)
    monthly_returns = portfolio.resample("ME").last().pct_change().dropna()
    win_rate = (monthly_returns > 0).sum() / len(monthly_returns) if len(monthly_returns) > 0 else 0

    # Profit Factor
    positive_months = monthly_returns[monthly_returns > 0].sum()
    negative_months = abs(monthly_returns[monthly_returns < 0].sum())
    profit_factor = positive_months / negative_months if negative_months > 0 else float("inf")

    # Trade stats
    buy_trades = [t for t in trades if t.action == "buy"]
    sell_trades = [t for t in trades if t.action == "sell"]
    total_fees = sum(t.fee for t in trades)

    # Volatility
    annual_volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0

    # Recovery time from max drawdown
    dd_end_idx = drawdown.idxmin()
    post_dd = active_portfolio[dd_end_idx:]
    peak_before_dd = cummax[dd_end_idx]
    recovery_mask = post_dd >= peak_before_dd
    if recovery_mask.any():
        recovery_date = recovery_mask.idxmax()
        recovery_days = (recovery_date - dd_end_idx).days
    else:
        recovery_days = None  # Not recovered yet

    return {
        "total_invested": total_invested,
        "final_value": final_value,
        "total_return_pct": total_return * 100,
        "cagr_pct": cagr * 100,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown_pct": max_drawdown * 100,
        "calmar_ratio": calmar,
        "win_rate_pct": win_rate * 100,
        "profit_factor": profit_factor,
        "annual_volatility_pct": annual_volatility * 100,
        "total_trades": len(trades),
        "buy_trades": len(buy_trades),
        "sell_trades": len(sell_trades),
        "total_fees_usd": total_fees,
        "max_dd_recovery_days": recovery_days,
        "years": years,
        "holdings_final": daily_df["holdings"].iloc[-1],
        "cash_final": daily_df["cash"].iloc[-1],
    }
