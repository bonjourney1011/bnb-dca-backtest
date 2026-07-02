# BNB DCA Trading Strategy Backtest

Data-driven analysis of BNB accumulation strategies for salary-based investors. All insights derived from **real Binance market data**, not theory.

## Problem Statement

> I receive salary on the 5th of each month in VND. I want to accumulate BNB optimally.
> Which strategy, buy day, and sell timing maximize my returns?

This project answers 6 questions using backtested data:

| # | Question | Script | Key Finding |
|---|----------|--------|-------------|
| 1 | Which DCA strategy is best? | `src/run_backtest.py` | Pure DCA beats all complex strategies (+493%) |
| 2 | What day should I buy? | `src/optimal_day_analysis.py` | Day 5 is already optimal; Thursday is cheapest weekday |
| 3 | Should I hold forever or sell? | `src/hold_vs_sell_analysis.py` | Hold forever beats ALL sell strategies by 10-72% |
| 4 | Where are we in the crypto cycle? | `src/cycle_analysis.py` | Mid-bear, predicted bottom Q4 2026, next halving Apr 2028 |
| 5 | Is $200K by 2029 feasible? | `src/plan_200k.py` | Needs ~100 BNB existing + $700/mo (cycle-aware DCA) |
| 6 | What's realistic for 5M VND/month? | `src/personal_plan.py` | 250-850M VND from 150M invested (base case) |

Additional analyses:
- **Wait vs DCA Now** (`src/wait_vs_dca_analysis.py`): Should you wait for bear bottom? No. DCA now wins on expected value.
- **Income Growth Plan** (`src/income_growth_plan.py`): Budget +20% every 6 months projection.

## Dataset

| Source | Period | Records | Fields |
|--------|--------|---------|--------|
| Binance API (BNB/USDT) | 2020-01-01 to 2026-07-02 | 2,375 days | OHLCV |
| Binance API (BNB/USDT) | 2017-11-06 to 2026-07-02 | 3,161 days | OHLCV (full history for cycle analysis) |
| alternative.me | 2018-02-01 to present | ~3,000 days | Crypto Fear & Greed Index |

Data is fetched live from Binance API (no API key required for public klines) and cached locally.

## Strategies Backtested

| Strategy | Logic | Result | Verdict |
|----------|-------|--------|---------|
| **Pure DCA** | Buy fixed $ on day 5, hold forever | **$231,118 (+493%)** | **WINNER** |
| DCA + RSI | 80% base + extra when RSI < 40 | $228,298 (+485%) | Marginal improvement, not worth complexity |
| Hybrid 80/15/5 | 80% DCA + 15% tactical + 5% reserve | $222,261 (+470%) | Psychological comfort, slightly worse |
| Fear & Greed DCA | Adjust allocation by sentiment index | $206,496 (+430%) | Underperforms Pure DCA by 12% |
| Value Averaging | Target linear portfolio growth | $141,658 (+263%) | Idle cash drag |
| Grid Trading | Buy dips, sell at +5% per level | $39,943 (+2%) | **Catastrophic** for trending assets |

**Config:** $500/month, day-5 salary, 0.1% Binance fee, 78 months (Jan 2020 - Jun 2026).

## Key Insights

### 1. Pure DCA wins everything
Complex strategies (RSI timing, sentiment analysis, grid trading) all **underperform** simple monthly buying. Time in market > timing the market.

### 2. Hold forever beats all sell strategies
| Sell Strategy | vs Hold Forever |
|---------------|-----------------|
| Trailing Stop -40% | -10.3% |
| Take Profit +200% | -28.5% |
| Sell 25% every 12mo | -24.6% |
| Take Profit +50% | **-72.5%** |

Every dollar sold is a dollar that misses future upside.

### 3. Day 5 is already a good buy day
Early month (days 1-5) prices average **1.3-1.5% below** monthly mean. No need to delay. If you want to optimize: limit order at -2%, cancel after 5 days.

### 4. -69% drawdown is unavoidable
All DCA strategies hit -69% max drawdown (2022 bear market). Recovery took **634 days**. If you can't stomach -69%, don't DCA into crypto.

### 5. Crypto cycles are real and predictable
| Cycle | Halving | Peak (days after) | Bear Bottom |
|-------|---------|-------------------|-------------|
| 1 | Jul 2016 | Dec 2017 (524d) | Dec 2018 |
| 2 | May 2020 | Nov 2021 (546d) | Jun 2022 |
| 3 | Apr 2024 | Oct 2025 (535d) | **~Q4 2026 (predicted)** |
| 4 | ~Apr 2028 | ~Q4 2029 (predicted) | - |

**Current position (Jul 2026):** Mid-bear, BNB -57% from ATH. Predicted bottom in 3-6 months.

### 6. $200K needs massive capital or massive BNB price
With 0.74 BNB and 5M VND/month (~$198), reaching $200K requires BNB to hit $10,700 (8.2x ATH). **Not realistic.**

Realistic targets: **250-850M VND** from 150M invested = ROI +67% to +467%.

## Output

### Charts (in `output/`)
| File | Description |
|------|-------------|
| `equity_curves.png` | Portfolio value over time for all 6 strategies |
| `risk_return_scatter.png` | Sharpe ratio vs total return scatter |
| `monthly_returns_heatmap.png` | Month-by-month return heatmap |
| `bnb_accumulation.png` | BNB token accumulation over time |
| `strategy_comparison_bars.png` | Side-by-side strategy comparison |

### Reports
| File | Description |
|------|-------------|
| `output/INSIGHT_REPORT.md` | Full analysis report with all findings |
| `output/strategy_comparison.csv` | Raw metrics for all strategies |
| `output/*_daily.csv` | Daily portfolio data per strategy |

## Action Plan

```
+----------------------------------------------------------+
|  MONTHLY ROUTINE (5 minutes/month, NO MORE):              |
|                                                           |
|  Day 5:                                                   |
|  1. Buy USDT with monthly budget (VND -> USDT via P2P)   |
|  2. Market buy BNB (USDT -> BNB)                         |
|  3. Log: date, price, quantity                            |
|  4. Close app. Done.                                      |
|                                                           |
|  DO NOT:                                                  |
|  - Check price daily                                      |
|  - Read crypto news                                       |
|  - Change the amount                                      |
|  - Sell                                                    |
|  - Use leverage/futures                                    |
|  - Buy other altcoins                                      |
+----------------------------------------------------------+
```

## Project Structure

```
bnb-trading/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── processed/          # Cached CSV data (gitignored, re-fetchable)
├── output/
│   ├── INSIGHT_REPORT.md   # Full analysis report
│   ├── *.png               # Charts and visualizations
│   └── *.csv               # Raw backtest results (gitignored)
└── src/
    ├── data_fetcher.py          # Binance API data fetching + caching
    ├── backtest_engine.py       # Core backtest engine + risk metrics
    ├── run_backtest.py          # Run all strategies + comparison
    ├── generate_charts.py       # Generate PNG charts
    ├── optimal_day_analysis.py  # Optimal buy day analysis
    ├── hold_vs_sell_analysis.py # Hold vs sell strategy comparison
    ├── cycle_analysis.py        # Crypto cycle timing analysis
    ├── plan_200k.py             # $200K target feasibility
    ├── personal_plan.py         # Personal plan (5M VND/month)
    ├── wait_vs_dca_analysis.py  # Wait for bear bottom vs DCA now
    ├── income_growth_plan.py    # Income +20%/6mo projection
    └── strategies/
        ├── __init__.py
        ├── pure_dca.py          # Simple monthly DCA
        ├── dca_rsi.py           # DCA with RSI oversold trigger
        ├── value_averaging.py   # Target-based value averaging
        ├── grid_trading.py      # Grid buy/sell levels
        ├── hybrid.py            # 80% DCA + 15% tactical + 5% reserve
        └── fear_greed_dca.py    # Sentiment-adjusted DCA
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch data + run full backtest
python src/run_backtest.py

# Generate charts
python src/generate_charts.py

# Run specific analyses
python src/optimal_day_analysis.py    # Best buy day
python src/hold_vs_sell_analysis.py   # Hold vs sell
python src/cycle_analysis.py          # Crypto cycle analysis
python src/personal_plan.py           # Personal plan simulation
python src/wait_vs_dca_analysis.py    # Wait vs DCA now
python src/income_growth_plan.py      # Income growth projection
```

## Risk Warnings

- **Drawdown -69% is real.** Portfolio $39K dropped to $12K in 2022. Recovery took 634 days.
- **CAGR 31.6% includes a +1,409% outlier year (2021).** Realistic future expectation: 10-20%.
- **BNB is currently -57% from ATH.** We are in a bear market (Jul 2026).
- **Crypto annual volatility: 78.5%.** That's 5x the S&P 500.
- **This is NOT financial advice.** This is a personal data analysis project.

## Tech Stack

- **Python 3.10+**
- **python-binance** - Binance API client (no API key needed for public data)
- **pandas / numpy** - Data processing
- **matplotlib** - Chart generation
- **ta** - Technical analysis (RSI calculation)
- **tabulate** - Terminal table formatting

## License

Personal project. Not financial advice.
