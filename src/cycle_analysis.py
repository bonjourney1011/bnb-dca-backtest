"""
Crypto Cycle Analysis for BNB.

Analyzes:
1. BTC halving cycles and BNB correlation
2. Bull/Bear phase identification
3. Cycle timing patterns
4. 2026 cycle position prediction
5. $200K target plan for 2029
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate
from src.data_fetcher import fetch_bnb_daily, save_data, load_data


# ==================== BTC HALVING DATES ====================
BTC_HALVINGS = {
    1: datetime(2012, 11, 28),
    2: datetime(2016, 7, 9),
    3: datetime(2020, 5, 11),
    4: datetime(2024, 4, 19),
    5: datetime(2028, 4, 1),  # Estimated
}

# Known cycle phases (from historical data)
CYCLE_PHASES = {
    "Cycle 2 (2016-2020)": {
        "halving": datetime(2016, 7, 9),
        "bull_start": datetime(2017, 1, 1),
        "bull_peak": datetime(2018, 1, 7),   # BTC ATH ~$19,800
        "bear_bottom": datetime(2018, 12, 15),  # BTC ~$3,200
        "recovery": datetime(2019, 6, 26),   # BTC ~$13,000
        "pre_halving_low": datetime(2020, 3, 13),  # COVID crash
    },
    "Cycle 3 (2020-2024)": {
        "halving": datetime(2020, 5, 11),
        "bull_start": datetime(2020, 10, 1),
        "bull_peak": datetime(2021, 11, 10),  # BTC ATH ~$69,000
        "bear_bottom": datetime(2022, 11, 21),  # BTC ~$15,500
        "recovery": datetime(2023, 10, 1),
        "pre_halving_low": datetime(2024, 1, 1),
    },
    "Cycle 4 (2024-2028)": {
        "halving": datetime(2024, 4, 19),
        "bull_start": datetime(2024, 10, 1),  # Post-ETF rally
        "bull_peak": None,  # TBD
        "bear_bottom": None,
        "recovery": None,
        "pre_halving_low": None,
    },
}


def fetch_full_history():
    """Fetch BNB from 2017 ICO to present."""
    print("Fetching BNB full history from 2017...")
    df = fetch_bnb_daily("2017-07-01")
    save_data(df, "bnb_usdt_full_history.csv")
    return df


def load_full_history():
    """Load full history data."""
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "processed", "bnb_usdt_full_history.csv"
    )
    if os.path.exists(filepath):
        return pd.read_csv(filepath, index_col="timestamp", parse_dates=True)
    return fetch_full_history()


def analyze_cycle_phases(df):
    """Identify and analyze bull/bear phases in BNB price history."""
    print("\n" + "=" * 100)
    print("PHAN TICH CHU KY GIA BNB (2017-2026)")
    print("=" * 100)

    # Define BNB-specific cycle events
    bnb_cycles = {
        "Cycle 1 - ICO & First Bull (2017-2018)": {
            "start": "2017-07-01",
            "peak": None,  # Will find from data
            "bottom": None,
            "end": "2020-05-11",
        },
        "Cycle 2 - DeFi & ATH (2020-2024)": {
            "start": "2020-05-11",
            "peak": None,
            "bottom": None,
            "end": "2024-04-19",
        },
        "Cycle 3 - Current (2024-present)": {
            "start": "2024-04-19",
            "peak": None,
            "bottom": None,
            "end": None,
        },
    }

    # Find peaks and bottoms for each cycle
    print("\n### BNB Price Milestones by Cycle ###\n")

    cycle_data = []

    # Cycle 1: 2017-07 to 2020-05
    c1 = df["2017-07":"2020-05"]
    if len(c1) > 0:
        c1_peak_date = c1["close"].idxmax()
        c1_peak_price = c1["close"].max()
        c1_bottom_date = c1.loc[c1_peak_date:]["close"].idxmin()
        c1_bottom_price = c1.loc[c1_peak_date:]["close"].min()
        c1_start_price = c1["close"].iloc[0]
        c1_drawdown = (c1_bottom_price / c1_peak_price - 1) * 100
        c1_bull_gain = (c1_peak_price / c1_start_price - 1) * 100

        # Days from halving to peak
        halving_to_peak_1 = (c1_peak_date - BTC_HALVINGS[2]).days
        peak_to_bottom_1 = (c1_bottom_date - c1_peak_date).days
        bottom_to_next_1 = (BTC_HALVINGS[3] - c1_bottom_date).days

        cycle_data.append({
            "Cycle": "1 (2017-2020)",
            "Halving": BTC_HALVINGS[2].strftime("%Y-%m-%d"),
            "Start Price": f"${c1_start_price:.2f}",
            "Peak Date": c1_peak_date.strftime("%Y-%m-%d"),
            "Peak Price": f"${c1_peak_price:.2f}",
            "Bull Gain": f"+{c1_bull_gain:.0f}%",
            "Bottom Date": c1_bottom_date.strftime("%Y-%m-%d"),
            "Bottom Price": f"${c1_bottom_price:.2f}",
            "Bear DD": f"{c1_drawdown:.0f}%",
            "Halving->Peak (days)": halving_to_peak_1,
            "Peak->Bottom (days)": peak_to_bottom_1,
            "Bottom->Next Halving": bottom_to_next_1,
        })

        print(f"Cycle 1 (BTC Halving Jul 2016):")
        print(f"  BNB Launch: ${c1_start_price:.2f}")
        print(f"  Bull Peak: ${c1_peak_price:.2f} on {c1_peak_date.strftime('%Y-%m-%d')} (+{c1_bull_gain:.0f}%)")
        print(f"  Bear Bottom: ${c1_bottom_price:.2f} on {c1_bottom_date.strftime('%Y-%m-%d')} ({c1_drawdown:.0f}% from peak)")
        print(f"  Halving -> Peak: {halving_to_peak_1} days")
        print(f"  Peak -> Bottom: {peak_to_bottom_1} days")

    # Cycle 2: 2020-05 to 2024-04
    c2 = df["2020-05":"2024-04"]
    if len(c2) > 0:
        c2_start_price = c2["close"].iloc[0]
        c2_peak_date = c2["close"].idxmax()
        c2_peak_price = c2["close"].max()
        c2_bottom_date = c2.loc[c2_peak_date:]["close"].idxmin()
        c2_bottom_price = c2.loc[c2_peak_date:]["close"].min()
        c2_drawdown = (c2_bottom_price / c2_peak_price - 1) * 100
        c2_bull_gain = (c2_peak_price / c2_start_price - 1) * 100

        halving_to_peak_2 = (c2_peak_date - BTC_HALVINGS[3]).days
        peak_to_bottom_2 = (c2_bottom_date - c2_peak_date).days
        bottom_to_next_2 = (BTC_HALVINGS[4] - c2_bottom_date).days

        cycle_data.append({
            "Cycle": "2 (2020-2024)",
            "Halving": BTC_HALVINGS[3].strftime("%Y-%m-%d"),
            "Start Price": f"${c2_start_price:.2f}",
            "Peak Date": c2_peak_date.strftime("%Y-%m-%d"),
            "Peak Price": f"${c2_peak_price:.2f}",
            "Bull Gain": f"+{c2_bull_gain:.0f}%",
            "Bottom Date": c2_bottom_date.strftime("%Y-%m-%d"),
            "Bottom Price": f"${c2_bottom_price:.2f}",
            "Bear DD": f"{c2_drawdown:.0f}%",
            "Halving->Peak (days)": halving_to_peak_2,
            "Peak->Bottom (days)": peak_to_bottom_2,
            "Bottom->Next Halving": bottom_to_next_2,
        })

        print(f"\nCycle 2 (BTC Halving May 2020):")
        print(f"  Start: ${c2_start_price:.2f}")
        print(f"  Bull Peak: ${c2_peak_price:.2f} on {c2_peak_date.strftime('%Y-%m-%d')} (+{c2_bull_gain:.0f}%)")
        print(f"  Bear Bottom: ${c2_bottom_price:.2f} on {c2_bottom_date.strftime('%Y-%m-%d')} ({c2_drawdown:.0f}% from peak)")
        print(f"  Halving -> Peak: {halving_to_peak_2} days")
        print(f"  Peak -> Bottom: {peak_to_bottom_2} days")

    # Cycle 3: 2024-04 to present
    c3 = df["2024-04":]
    if len(c3) > 0:
        c3_start_price = c3["close"].iloc[0]
        c3_peak_date = c3["close"].idxmax()
        c3_peak_price = c3["close"].max()
        c3_current_price = c3["close"].iloc[-1]
        c3_current_date = c3.index[-1]
        days_since_halving = (c3_current_date - BTC_HALVINGS[4]).days

        # Current drawdown from cycle peak
        c3_dd_from_peak = (c3_current_price / c3_peak_price - 1) * 100

        cycle_data.append({
            "Cycle": "3 (2024-now)",
            "Halving": BTC_HALVINGS[4].strftime("%Y-%m-%d"),
            "Start Price": f"${c3_start_price:.2f}",
            "Peak Date": c3_peak_date.strftime("%Y-%m-%d"),
            "Peak Price": f"${c3_peak_price:.2f}",
            "Bull Gain": f"+{(c3_peak_price/c3_start_price-1)*100:.0f}%",
            "Bottom Date": "TBD",
            "Bottom Price": f"Current: ${c3_current_price:.2f}",
            "Bear DD": f"{c3_dd_from_peak:.0f}% from peak",
            "Halving->Peak (days)": (c3_peak_date - BTC_HALVINGS[4]).days,
            "Peak->Bottom (days)": "TBD",
            "Bottom->Next Halving": "TBD",
        })

        print(f"\nCycle 3 (BTC Halving Apr 2024) - CURRENT:")
        print(f"  Start: ${c3_start_price:.2f}")
        print(f"  Peak so far: ${c3_peak_price:.2f} on {c3_peak_date.strftime('%Y-%m-%d')}")
        print(f"  Current: ${c3_current_price:.2f} ({c3_dd_from_peak:.1f}% from peak)")
        print(f"  Days since halving: {days_since_halving}")

    print("\n" + tabulate(cycle_data, headers="keys", tablefmt="grid"))

    return cycle_data


def analyze_cycle_timing_patterns(df):
    """Analyze timing patterns across cycles."""
    print("\n" + "=" * 100)
    print("CYCLE TIMING PATTERNS - Halving -> Peak -> Bottom")
    print("=" * 100)

    # Cycle timing summary
    timing = [
        {
            "Metric": "Halving -> Bull Peak",
            "Cycle 1 (BTC)": "~525 days (Dec 2017)",
            "Cycle 2 (BTC)": "~546 days (Nov 2021)",
            "Average": "~535 days",
            "Cycle 3 Prediction": "",
        },
        {
            "Metric": "Bull Peak -> Bear Bottom",
            "Cycle 1 (BTC)": "~364 days",
            "Cycle 2 (BTC)": "~376 days",
            "Average": "~370 days",
            "Cycle 3 Prediction": "",
        },
        {
            "Metric": "Full Cycle Length",
            "Cycle 1 (BTC)": "~1,400 days",
            "Cycle 2 (BTC)": "~1,400 days",
            "Average": "~1,400 days (~4 years)",
            "Cycle 3 Prediction": "",
        },
        {
            "Metric": "Bear DD from Peak",
            "Cycle 1 (BTC)": "-84% (BTC), -93% (BNB)",
            "Cycle 2 (BTC)": "-77% (BTC), -69% (BNB)",
            "Average": "-80% BTC, -81% BNB",
            "Cycle 3 Prediction": "",
        },
    ]

    # Predictions for Cycle 3
    halving_4 = BTC_HALVINGS[4]  # Apr 19, 2024
    predicted_peak = halving_4 + timedelta(days=535)
    predicted_bottom = predicted_peak + timedelta(days=370)
    predicted_next_halving = BTC_HALVINGS[5]

    timing[0]["Cycle 3 Prediction"] = f"~{predicted_peak.strftime('%b %Y')} (535d from halving)"
    timing[1]["Cycle 3 Prediction"] = f"~{predicted_bottom.strftime('%b %Y')} (370d from peak)"
    timing[2]["Cycle 3 Prediction"] = f"~{predicted_next_halving.strftime('%b %Y')} (next halving)"
    timing[3]["Cycle 3 Prediction"] = "Expected -60% to -80%"

    print(tabulate(timing, headers="keys", tablefmt="grid"))

    print(f"\n### CYCLE 3 PREDICTION TIMELINE ###")
    print(f"  Halving:           {halving_4.strftime('%Y-%m-%d')} (DONE)")
    print(f"  Predicted Peak:    ~{predicted_peak.strftime('%Y-%m-%d')} (+/- 3 months)")
    print(f"  Predicted Bottom:  ~{predicted_bottom.strftime('%Y-%m-%d')} (+/- 3 months)")
    print(f"  Next Halving:      ~{predicted_next_halving.strftime('%Y-%m-%d')}")
    print(f"  Today (2026-07-02): {(datetime(2026, 7, 2) - halving_4).days} days post-halving")

    # Where are we in the cycle?
    days_post_halving = (datetime(2026, 7, 2) - halving_4).days
    if days_post_halving < 535:
        pct_to_peak = days_post_halving / 535 * 100
        print(f"\n  >>> WE ARE {pct_to_peak:.0f}% through the bull phase (if cycle repeats)")
        print(f"  >>> {535 - days_post_halving} days until predicted peak")
    else:
        print(f"\n  >>> We are PAST the average peak timing")
        print(f"  >>> Cycle may have peaked or is extended")

    return predicted_peak, predicted_bottom


def analyze_bnb_cycle_returns(df):
    """Analyze BNB returns at different points in the cycle."""
    print("\n" + "=" * 100)
    print("BNB RETURNS BY CYCLE PHASE")
    print("=" * 100)

    halving_4 = BTC_HALVINGS[4]

    # Measure BNB return from halving to various points
    points = [
        (90, "3 months"),
        (180, "6 months"),
        (270, "9 months"),
        (365, "1 year"),
        (450, "15 months"),
        (535, "18 months (avg peak)"),
        (630, "21 months"),
        (730, "2 years"),
        (900, "2.5 years"),
    ]

    print("\n### Cycle 3 - BNB Return from Halving (Apr 2024) ###\n")
    halving_price_row = df[df.index >= halving_4]
    if len(halving_price_row) > 0:
        halving_price = halving_price_row["close"].iloc[0]
        print(f"BNB at halving: ${halving_price:.2f}")

        rows = []
        for days, label in points:
            target_date = halving_4 + timedelta(days=days)
            # Find closest date in data
            mask = df.index >= target_date
            if mask.any():
                actual_date = df[mask].index[0]
                price = df.loc[actual_date, "close"]
                ret = (price / halving_price - 1) * 100
                rows.append({
                    "Phase": label,
                    "Date": actual_date.strftime("%Y-%m-%d"),
                    "BNB Price": f"${price:.2f}",
                    "Return from Halving": f"{ret:+.1f}%",
                    "Status": "ACTUAL" if actual_date <= datetime(2026, 7, 2) else "FUTURE",
                })
            else:
                rows.append({
                    "Phase": label,
                    "Date": target_date.strftime("%Y-%m-%d"),
                    "BNB Price": "N/A",
                    "Return from Halving": "FUTURE",
                    "Status": "FUTURE",
                })

        print(tabulate(rows, headers="keys", tablefmt="grid"))

    # Compare with Cycle 2
    print("\n### Cycle 2 - BNB Return from Halving (May 2020) for comparison ###\n")
    halving_3 = BTC_HALVINGS[3]
    h3_data = df[df.index >= halving_3]
    if len(h3_data) > 0:
        h3_price = h3_data["close"].iloc[0]
        print(f"BNB at halving: ${h3_price:.2f}")

        rows2 = []
        for days, label in points:
            target_date = halving_3 + timedelta(days=days)
            mask = (df.index >= target_date) & (df.index <= halving_4)
            if mask.any():
                actual_date = df[mask].index[0]
                price = df.loc[actual_date, "close"]
                ret = (price / h3_price - 1) * 100
                rows2.append({
                    "Phase": label,
                    "Date": actual_date.strftime("%Y-%m-%d"),
                    "BNB Price": f"${price:.2f}",
                    "Return from Halving": f"{ret:+.1f}%",
                })

        print(tabulate(rows2, headers="keys", tablefmt="grid"))


def analyze_cycle_position_now(df):
    """Determine where we are in the current cycle and what to expect."""
    print("\n" + "=" * 100)
    print("CURRENT CYCLE POSITION (Jul 2026)")
    print("=" * 100)

    current_price = df["close"].iloc[-1]
    halving_4 = BTC_HALVINGS[4]
    days_since_halving = (datetime(2026, 7, 2) - halving_4).days

    # Cycle 3 peak so far
    c3_data = df["2024-04":]
    peak_price = c3_data["close"].max()
    peak_date = c3_data["close"].idxmax()
    dd_from_peak = (current_price / peak_price - 1) * 100

    # Price at halving
    halving_data = df[df.index >= halving_4]
    halving_price = halving_data["close"].iloc[0] if len(halving_data) > 0 else current_price
    gain_from_halving = (current_price / halving_price - 1) * 100

    print(f"\n  Current BNB Price:     ${current_price:.2f}")
    print(f"  Price at Halving:      ${halving_price:.2f}")
    print(f"  Cycle Peak:            ${peak_price:.2f} ({peak_date.strftime('%Y-%m-%d')})")
    print(f"  Gain from Halving:     {gain_from_halving:+.1f}%")
    print(f"  Drop from Peak:        {dd_from_peak:.1f}%")
    print(f"  Days since Halving:    {days_since_halving}")

    # Compare same point in Cycle 2
    c2_same_point = halving_4 - timedelta(days=1461) + timedelta(days=days_since_halving)  # ~4 years back
    c2_halving_data = df[df.index >= BTC_HALVINGS[3]]
    if len(c2_halving_data) > 0:
        c2_halving_price = c2_halving_data["close"].iloc[0]
        c2_same = df[df.index >= c2_same_point]
        if len(c2_same) > 0:
            c2_price_then = c2_same["close"].iloc[0]
            c2_gain_then = (c2_price_then / c2_halving_price - 1) * 100
            print(f"\n  At same point in Cycle 2 ({c2_same_point.strftime('%Y-%m-%d')}):")
            print(f"    BNB was: ${c2_price_then:.2f}")
            print(f"    Gain from C2 halving: {c2_gain_then:+.1f}%")

            if c2_gain_then > gain_from_halving:
                print(f"    >>> Cycle 3 is LAGGING Cycle 2 by {c2_gain_then - gain_from_halving:.0f}%")
            else:
                print(f"    >>> Cycle 3 is LEADING Cycle 2 by {gain_from_halving - c2_gain_then:.0f}%")

    # Scenarios
    print(f"\n### CYCLE 3 SCENARIOS FOR BNB ###")

    # Based on Cycle 2 patterns
    scenarios = []

    # Bull scenario: BNB repeats Cycle 2 peak multiplier from halving
    c2_peak_from_halving = None
    if len(c2_halving_data) > 0:
        c2_halving_price = c2_halving_data["close"].iloc[0]
        c2_peak = df["2020-05":"2024-04"]["close"].max()
        c2_peak_from_halving = c2_peak / c2_halving_price

    if c2_peak_from_halving:
        # Diminishing returns: each cycle typically has lower multiplier
        scenarios.append({
            "Scenario": "Bull (repeat C2 multiplier)",
            "BNB Peak": f"${halving_price * c2_peak_from_halving:.0f}",
            "Multiplier": f"{c2_peak_from_halving:.1f}x from halving",
            "Timeline": "Oct-Dec 2025 (avg peak timing)",
            "Probability": "20%",
            "Note": "Already past avg peak window",
        })

        # Diminished bull: 50% of C2 multiplier
        dim_mult = 1 + (c2_peak_from_halving - 1) * 0.5
        scenarios.append({
            "Scenario": "Moderate Bull (50% of C2)",
            "BNB Peak": f"${halving_price * dim_mult:.0f}",
            "Multiplier": f"{dim_mult:.1f}x from halving",
            "Timeline": "Q3-Q4 2026",
            "Probability": "35%",
            "Note": "Diminishing returns pattern",
        })

        # Extended cycle (longer than 535 days)
        scenarios.append({
            "Scenario": "Extended Cycle (peak late)",
            "BNB Peak": f"${halving_price * dim_mult * 0.8:.0f}",
            "Multiplier": f"{dim_mult * 0.8:.1f}x",
            "Timeline": "Q1-Q2 2027",
            "Probability": "25%",
            "Note": "Institutional cycle = longer",
        })

        # Bear already started
        scenarios.append({
            "Scenario": "Bear Market (peak was ATH)",
            "BNB Bottom": f"${peak_price * 0.3:.0f}",
            "Multiplier": f"-70% from {peak_price:.0f}",
            "Timeline": "Q2-Q4 2027",
            "Probability": "20%",
            "Note": "If C3 peak was Nov 2024 ATH",
        })

    print(tabulate(scenarios, headers="keys", tablefmt="grid"))

    return scenarios


def plan_200k_target(df):
    """Build concrete plan to reach $200K by 2029."""
    print("\n" + "=" * 100)
    print("PLAN: DAT $200,000 TRUOC 2029")
    print("=" * 100)

    current_price = df["close"].iloc[-1]
    current_date = df.index[-1]

    # Months from now to Jan 2029
    months_to_target = (datetime(2029, 1, 1) - datetime(2026, 7, 2)).days / 30.44
    months_to_target = int(months_to_target)

    print(f"\n  Current date:    2026-07-02")
    print(f"  Target date:     2029-01-01")
    print(f"  Months:          {months_to_target}")
    print(f"  Target:          $200,000")
    print(f"  Current BNB:     ${current_price:.2f}")

    # Scenario modeling
    monthly_amounts = [300, 500, 700, 1000]
    bnb_scenarios = {
        "Bear ($200)": 200,
        "Flat ($550)": 550,
        "Moderate ($1000)": 1000,
        "Bull ($1500)": 1500,
        "Super Bull ($2500)": 2500,
    }

    print(f"\n### Scenario Matrix: Monthly DCA x BNB Price in 2029 ###")
    print(f"    (Value = Portfolio value at BNB target price)\n")

    # Build matrix
    header = ["Monthly $"] + list(bnb_scenarios.keys())
    rows = []

    for monthly in monthly_amounts:
        row = [f"${monthly}"]
        for scenario_name, target_price in bnb_scenarios.items():
            # Total invested
            total_invested = monthly * months_to_target
            # Estimate BNB accumulated (assume avg buy price = average of current and target/2)
            # More accurate: simulate DCA with price path
            # Simple model: avg price = current * (1 + (target/current)^0.5) / 2
            if target_price > current_price:
                # Bull: prices rise, avg price higher
                avg_buy_price = current_price * (1 + (target_price / current_price) ** 0.3) / 2
            else:
                # Bear: prices fall, avg price lower (good for accumulation!)
                avg_buy_price = (current_price + target_price) / 2

            total_bnb = (total_invested * 0.999) / avg_buy_price  # 0.1% fee
            portfolio_value = total_bnb * target_price

            marker = " **" if portfolio_value >= 200000 else ""
            row.append(f"${portfolio_value:,.0f}{marker}")

        rows.append(row)

    print(tabulate(rows, headers=header, tablefmt="grid"))
    print("  ** = Dat muc tieu $200K")

    # Detailed plan for each monthly amount
    print(f"\n### Chi tiet: Can bao nhieu/thang de dat $200K? ###\n")

    for scenario_name, target_price in bnb_scenarios.items():
        for monthly in [300, 500, 700, 1000, 1500, 2000]:
            total_invested = monthly * months_to_target
            if target_price > current_price:
                avg_buy_price = current_price * (1 + (target_price / current_price) ** 0.3) / 2
            else:
                avg_buy_price = (current_price + target_price) / 2

            total_bnb = (total_invested * 0.999) / avg_buy_price
            portfolio_value = total_bnb * target_price

            if portfolio_value >= 200000:
                print(f"  {scenario_name}: ${monthly}/thang x {months_to_target} thang = ${total_invested:,} invested -> {total_bnb:.1f} BNB -> ${portfolio_value:,.0f} (DAT TARGET)")
                break
        else:
            print(f"  {scenario_name}: Can > $2000/thang (kho dat $200K)")

    # Cycle-aware strategy
    print(f"\n### CHIEN LUOC CYCLE-AWARE ###\n")

    print("""
PHASE 1: ACCUMULATION (Jul 2026 - Mar 2027)
  - Status: Dang o giai doan mid-cycle, co the con upside
  - Action: DCA $500-700/thang
  - Ly do: Accumulate truoc khi cycle peak

PHASE 2: PEAK ZONE (Q3-Q4 2026 hoac Q1-Q2 2027)
  - Trigger: BNB > $1000 hoac BTC > $150K
  - Action: GIAM DCA xuong $300/thang
  - Ly do: Gia cao = mua it BNB hon, risk tang

PHASE 3: BEAR MARKET (2027-2028 estimated)
  - Trigger: BNB giam > 50% tu peak
  - Action: TANG DCA len $1000-1500/thang (max affordable)
  - Ly do: DAY LA GIAI DOAN QUAN TRONG NHAT
  - Bear market = mua duoc nhieu BNB voi gia re
  - $1000/thang khi BNB = $200 = 5 BNB/thang (vs 0.9 BNB khi $1100)

PHASE 4: RECOVERY (2028-2029)
  - Trigger: BNB hoi phuc > 20-day MA
  - Action: Giu DCA $700/thang
  - Hold cho next halving cycle (2028)

TARGET CHECK:
  - If BNB reaches $1000 by 2029:
    Need ~200 BNB -> ~$700/thang DCA binh thuong
  - If BNB stays $550 (flat):
    Need ~364 BNB -> Can ~$1200/thang HOAC DCA nhieu hon khi bear
  - If BNB drops to $200 then recovers to $800:
    Bear accumulation = KEY -> $1000/thang khi BNB < $300
""")

    # Monte Carlo-ish simple scenarios
    print(f"\n### BACKTEST: Gia su bat dau DCA tu hom nay ###\n")

    for monthly in [500, 700, 1000]:
        total = monthly * months_to_target
        bnb_at_current = (total * 0.999) / current_price

        print(f"  ${monthly}/thang x {months_to_target} thang = ${total:,} invested")
        print(f"    BNB accumulated (at current price): {bnb_at_current:.1f} BNB")
        print(f"    If BNB = $700 by 2029: ${bnb_at_current * 700:,.0f}")
        print(f"    If BNB = $1000 by 2029: ${bnb_at_current * 1000:,.0f}")
        print(f"    If BNB = $1500 by 2029: ${bnb_at_current * 1500:,.0f}")
        print(f"    Need BNB = ${200000 / bnb_at_current:.0f} to hit $200K")
        print()


if __name__ == "__main__":
    # Fetch full history
    df = load_full_history()
    print(f"Full history: {len(df)} days, {df.index.min().date()} -> {df.index.max().date()}")
    print(f"BNB price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")

    # 1. Cycle phase analysis
    cycle_data = analyze_cycle_phases(df)

    # 2. Timing patterns
    predicted_peak, predicted_bottom = analyze_cycle_timing_patterns(df)

    # 3. Returns by cycle phase
    analyze_bnb_cycle_returns(df)

    # 4. Current position
    analyze_cycle_position_now(df)

    # 5. $200K plan
    plan_200k_target(df)
