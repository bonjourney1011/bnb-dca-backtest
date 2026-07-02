"""
Realistic $200K Plan Builder.

Combines:
- Existing BNB holdings (from previous DCA)
- New monthly DCA from Jul 2026
- Cycle-aware accumulation strategy
- Multiple price scenarios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate


def simulate_cycle_aware_dca(
    existing_bnb: float,
    monthly_base: float,
    start_date: datetime = datetime(2026, 7, 1),
    end_date: datetime = datetime(2029, 1, 1),
):
    """
    Simulate cycle-aware DCA from start to end.

    Price model based on Cycle 3 pattern:
    - Jul 2026: $560 (current, -57% from peak, mid-bear)
    - Oct 2026: $350-400 (predicted bear bottom, ~370 days from peak)
    - Q1-Q2 2027: $250-350 (deep bear, accumulation zone)
    - Q3 2027: $300-400 (early recovery)
    - Q1 2028: $400-500 (pre-halving)
    - Apr 2028: Halving #5
    - Q4 2028: $800-1200 (post-halving bull)
    - Q1 2029: $1000-2000 (early Cycle 5 bull)
    """

    # Build monthly price scenarios (conservative, base, optimistic)
    months = []
    current = start_date
    while current < end_date:
        months.append(current)
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

    # Price paths based on cycle analysis
    price_paths = {
        "Conservative": [],
        "Base Case": [],
        "Optimistic": [],
    }

    for m in months:
        # Phase determination
        if m < datetime(2026, 10, 1):
            # Mid-bear decline
            conservative = 400 + (560 - 400) * max(0, 1 - (m - datetime(2026, 7, 1)).days / 90)
            base = 450 + (560 - 450) * max(0, 1 - (m - datetime(2026, 7, 1)).days / 90)
            optimistic = 500 + (560 - 500) * max(0, 1 - (m - datetime(2026, 7, 1)).days / 90)
        elif m < datetime(2027, 4, 1):
            # Deep bear / bottom zone
            conservative = 200 + np.random.RandomState(m.month + m.year).uniform(-30, 30)
            base = 300 + np.random.RandomState(m.month + m.year).uniform(-40, 40)
            optimistic = 400 + np.random.RandomState(m.month + m.year).uniform(-50, 50)
        elif m < datetime(2027, 10, 1):
            # Early recovery
            progress = (m - datetime(2027, 4, 1)).days / 180
            conservative = 220 + progress * 80
            base = 320 + progress * 130
            optimistic = 420 + progress * 180
        elif m < datetime(2028, 4, 1):
            # Pre-halving accumulation
            progress = (m - datetime(2027, 10, 1)).days / 180
            conservative = 300 + progress * 100
            base = 450 + progress * 150
            optimistic = 600 + progress * 200
        elif m < datetime(2028, 10, 1):
            # Post-halving (Halving #5 Apr 2028)
            progress = (m - datetime(2028, 4, 1)).days / 180
            conservative = 400 + progress * 200
            base = 600 + progress * 400
            optimistic = 800 + progress * 700
        else:
            # Early Cycle 5 bull
            progress = (m - datetime(2028, 10, 1)).days / 90
            conservative = 600 + progress * 200
            base = 1000 + progress * 500
            optimistic = 1500 + progress * 1000

        price_paths["Conservative"].append(max(150, conservative))
        price_paths["Base Case"].append(max(200, base))
        price_paths["Optimistic"].append(max(300, optimistic))

    return months, price_paths


def run_plan(existing_bnb, monthly_base, months, price_path, scenario_name):
    """Run DCA plan with cycle-aware adjustments."""
    bnb = existing_bnb
    total_invested = 0.0
    total_new_invested = 0.0
    records = []

    for i, (month, price) in enumerate(zip(months, price_path)):
        # Cycle-aware capital adjustment
        if price < 250:
            # Deep bear: max accumulation
            monthly = monthly_base * 2.0
            phase = "BEAR MAX"
        elif price < 400:
            # Bear recovery: increase
            monthly = monthly_base * 1.5
            phase = "BEAR+"
        elif price < 600:
            # Normal
            monthly = monthly_base * 1.0
            phase = "NORMAL"
        elif price < 1000:
            # Getting expensive
            monthly = monthly_base * 0.8
            phase = "CAUTION"
        else:
            # Expensive: reduce
            monthly = monthly_base * 0.5
            phase = "REDUCE"

        fee = monthly * 0.001
        qty = (monthly - fee) / price
        bnb += qty
        total_invested += monthly
        total_new_invested += monthly
        portfolio_value = bnb * price

        records.append({
            "Month": month.strftime("%Y-%m"),
            "Phase": phase,
            "BNB Price": f"${price:.0f}",
            "Monthly $": f"${monthly:.0f}",
            "BNB Bought": f"{qty:.2f}",
            "Total BNB": f"{bnb:.1f}",
            "Portfolio $": f"${portfolio_value:,.0f}",
            "Invested $": f"${total_new_invested:,.0f}",
        })

    return records, bnb, total_new_invested


def main():
    print("=" * 110)
    print("PLAN $200K BY 2029 - CYCLE-AWARE DCA STRATEGY")
    print("=" * 110)

    # Assumptions
    print("""
ASSUMPTIONS:
  - Start: Jul 2026
  - Target: $200,000 by Jan 2029 (30 months)
  - Current BNB: $561
  - BTC Halving #5: ~Apr 2028
  - Cycle pattern: Bear bottom Q4 2026 -> Recovery 2027 -> Bull 2028-2029
""")

    months, price_paths = simulate_cycle_aware_dca(
        existing_bnb=0,
        monthly_base=500,
    )

    # Test different starting positions
    existing_bnb_options = [0, 50, 100, 200, 300]
    monthly_options = [500, 700, 1000, 1500]

    print("\n### SCENARIO MATRIX: Existing BNB x Monthly DCA ###")
    print("    (Portfolio value at Jan 2029, Base Case scenario)\n")

    header = ["Existing BNB"] + [f"${m}/mo" for m in monthly_options]
    rows = []

    for existing in existing_bnb_options:
        row = [f"{existing} BNB (${existing * 561:,.0f} now)"]
        for monthly in monthly_options:
            _, price_path_base = simulate_cycle_aware_dca(existing, monthly)
            records, final_bnb, total_inv = run_plan(
                existing, monthly, months, price_paths["Base Case"], "Base"
            )
            final_price = price_paths["Base Case"][-1]
            final_value = final_bnb * final_price
            marker = " **" if final_value >= 200000 else ""
            row.append(f"${final_value:,.0f}{marker}")
        rows.append(row)

    print(tabulate(rows, headers=header, tablefmt="grid"))
    print("  ** = TARGET $200K ACHIEVED\n")

    # Detailed plan for realistic scenario
    print("\n" + "=" * 110)
    print("DETAILED PLAN: 100 BNB existing + $700/month cycle-aware DCA")
    print("=" * 110)

    for scenario_name in ["Conservative", "Base Case", "Optimistic"]:
        print(f"\n### {scenario_name} Scenario ###\n")
        records, final_bnb, total_inv = run_plan(
            100, 700, months, price_paths[scenario_name], scenario_name
        )
        print(tabulate(records, headers="keys", tablefmt="grid"))

        final_price = price_paths[scenario_name][-1]
        final_value = final_bnb * final_price
        print(f"\n  Final BNB: {final_bnb:.1f}")
        print(f"  Final Price: ${final_price:.0f}")
        print(f"  Portfolio Value: ${final_value:,.0f}")
        print(f"  New Capital Invested: ${total_inv:,.0f}")
        print(f"  Target $200K: {'ACHIEVED' if final_value >= 200000 else 'NOT REACHED'}")
        if final_value < 200000:
            need_price = 200000 / final_bnb
            print(f"  Need BNB = ${need_price:.0f} to reach $200K")

    # What existing BNB is needed?
    print("\n" + "=" * 110)
    print("MINIMUM REQUIREMENTS TO HIT $200K BY 2029")
    print("=" * 110)

    for scenario_name in ["Conservative", "Base Case", "Optimistic"]:
        final_price = price_paths[scenario_name][-1]
        print(f"\n{scenario_name} (BNB = ${final_price:.0f} by Jan 2029):")

        for monthly in [500, 700, 1000, 1500]:
            records, final_bnb_no_existing, total_inv = run_plan(
                0, monthly, months, price_paths[scenario_name], scenario_name
            )
            bnb_from_dca = final_bnb_no_existing
            bnb_needed_total = 200000 / final_price
            existing_needed = max(0, bnb_needed_total - bnb_from_dca)

            print(f"  ${monthly}/mo -> DCA gets {bnb_from_dca:.0f} BNB | Need total {bnb_needed_total:.0f} BNB | Need existing: {existing_needed:.0f} BNB (${existing_needed * 561:,.0f} now)")

    # Action plan
    print(f"""

{'=' * 110}
CYCLE-AWARE ACTION PLAN
{'=' * 110}

PHASE 1: BEAR ACCUMULATION (Jul 2026 - Mar 2027) *** GIAI DOAN QUAN TRONG NHAT ***
  Duration:  ~9 months
  BNB Expected: $200-$450 (bear bottom zone)
  Action:    DCA $1000-1500/month (TANG GAP DOI khi gia re)
  Why:       $1000 khi BNB=$250 = 4 BNB/thang
             $1000 khi BNB=$1000 = 1 BNB/thang
             => Mua 4x nhieu BNB khi bear!
  Monthly limit order: Dat limit -5% tu gia hien tai
  Target accumulation: 80-120 BNB trong 9 thang

PHASE 2: EARLY RECOVERY (Apr 2027 - Mar 2028)
  Duration:  ~12 months
  BNB Expected: $300-$600
  Action:    DCA $700/month (binh thuong)
  Why:       Gia dang hoi phuc, van con co hoi mua
  Target accumulation: 20-40 BNB them

PHASE 3: POST-HALVING BULL (Apr 2028 - Dec 2028)
  Duration:  ~9 months
  BNB Expected: $600-$1500+
  Action:    GIAM DCA xuong $300-500/month
  Why:       Gia dat, moi dollar mua it BNB
  Optional:  Neu BNB > $1500, consider taking 10-20% profit

PHASE 4: TARGET CHECK (Jan 2029)
  Action:    Danh gia portfolio
  If > $200K: Mission accomplished
  If < $200K: Hold va cho Cycle 5 bull peak (Q3-Q4 2029)

RISK MANAGEMENT:
  - NEVER invest > 50% of monthly salary vao crypto
  - Keep 6-month emergency fund TRUOC khi DCA
  - Bear market = co hoi, KHONG PHAI threat
  - Max portfolio allocation for crypto: 30% of net worth
""")


if __name__ == "__main__":
    main()
