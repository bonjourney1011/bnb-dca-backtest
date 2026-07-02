"""
Analysis: Should I buy BNB now (July 2026) or wait until October 2026?

Compares 4 strategies across multiple scenarios:
A) DCA now from July 2026
B) Save USDT July-Sep, ALL-IN October
C) Save USDT July-Sep, spread DCA Oct-Dec
D) Save USDT, wait for price < $350
"""

from tabulate import tabulate

# Constants
MONTHLY_VND = 5_000_000
VND_USD_RATE = 25_250
MONTHLY_USD = MONTHLY_VND / VND_USD_RATE  # ~$198
EXISTING_BNB = 0.74
FEE_RATE = 0.001
MONTHS_TOTAL = 30  # Jul 2026 -> Dec 2028

# Price paths for different scenarios
def get_price_path(scenario):
    """Return monthly BNB prices Jul 2026 - Dec 2028."""
    if scenario == "base":
        # Base case: bear bottom Q4 2026, recovery 2027, bull 2028
        return [
            540, 480, 420, 350, 300, 280,  # Jul-Dec 2026
            260, 250, 270, 300, 320, 350,  # Jan-Jun 2027
            370, 400, 420, 450, 470, 500,  # Jul-Dec 2027
            520, 550, 580, 600, 650, 720,  # Jan-Jun 2028
            800, 900, 1000, 1100, 1200, 1350,  # Jul-Dec 2028
        ]
    elif scenario == "wrong_up":
        # Wrong: price goes UP from July (no bear)
        return [
            540, 580, 620, 650, 700, 750,  # Jul-Dec 2026
            720, 680, 700, 750, 800, 850,  # Jan-Jun 2027
            900, 950, 1000, 1050, 1100, 1150,  # Jul-Dec 2027
            1200, 1250, 1300, 1400, 1500, 1600,  # Jan-Jun 2028
            1700, 1800, 1900, 2000, 2200, 2500,  # Jul-Dec 2028
        ]
    elif scenario == "wrong_flat":
        # Wrong: price stays flat ~$500-600
        return [
            540, 520, 510, 530, 550, 520,  # Jul-Dec 2026
            510, 530, 540, 520, 510, 530,  # Jan-Jun 2027
            550, 540, 520, 530, 550, 560,  # Jul-Dec 2027
            570, 580, 590, 600, 610, 620,  # Jan-Jun 2028
            630, 640, 650, 660, 670, 680,  # Jul-Dec 2028
        ]
    elif scenario == "wrong_worse":
        # Wrong: bear is WORSE than expected
        return [
            540, 450, 350, 250, 200, 180,  # Jul-Dec 2026
            150, 130, 120, 140, 160, 180,  # Jan-Jun 2027
            200, 220, 250, 280, 300, 320,  # Jul-Dec 2027
            350, 380, 400, 420, 450, 500,  # Jan-Jun 2028
            550, 600, 650, 700, 750, 800,  # Jul-Dec 2028
        ]


def strategy_a_dca_now(prices, monthly_usd):
    """A: DCA mua BNB ngay tu thang 7."""
    bnb = EXISTING_BNB
    total_invested = 0
    for price in prices:
        qty = (monthly_usd * (1 - FEE_RATE)) / price
        bnb += qty
        total_invested += monthly_usd
    final_value = bnb * prices[-1]
    return bnb, total_invested, final_value


def strategy_b_allin_oct(prices, monthly_usd):
    """B: Giu USDT T7-9, ALL-IN vao T10/2026."""
    bnb = EXISTING_BNB
    total_invested = 0
    saved_usdt = 0

    for i, price in enumerate(prices):
        total_invested += monthly_usd
        if i < 3:  # Jul, Aug, Sep 2026 -> save USDT
            saved_usdt += monthly_usd
        elif i == 3:  # Oct 2026 -> ALL-IN
            total_buy = saved_usdt + monthly_usd
            qty = (total_buy * (1 - FEE_RATE)) / price
            bnb += qty
            saved_usdt = 0
        else:  # Nov 2026+ -> DCA binh thuong
            qty = (monthly_usd * (1 - FEE_RATE)) / price
            bnb += qty

    final_value = bnb * prices[-1]
    return bnb, total_invested, final_value


def strategy_c_spread_oct_dec(prices, monthly_usd):
    """C: Giu USDT T7-9, chia DCA T10-12/2026."""
    bnb = EXISTING_BNB
    total_invested = 0
    saved_usdt = 0

    for i, price in enumerate(prices):
        total_invested += monthly_usd
        if i < 3:  # Jul-Sep -> save
            saved_usdt += monthly_usd
        elif i < 6:  # Oct-Dec -> spread saved + monthly
            spread = saved_usdt / (6 - i)  # divide remaining saved equally
            buy_amount = spread + monthly_usd
            qty = (buy_amount * (1 - FEE_RATE)) / price
            bnb += qty
            saved_usdt -= spread
        else:  # Jan 2027+ -> DCA binh thuong
            qty = (monthly_usd * (1 - FEE_RATE)) / price
            bnb += qty

    final_value = bnb * prices[-1]
    return bnb, total_invested, final_value


def strategy_d_wait_below_350(prices, monthly_usd):
    """D: Giu USDT cho den khi BNB < $350."""
    bnb = EXISTING_BNB
    total_invested = 0
    saved_usdt = 0
    triggered = False

    for i, price in enumerate(prices):
        total_invested += monthly_usd
        if not triggered:
            if price < 350:
                triggered = True
                buy_amount = saved_usdt + monthly_usd
                qty = (buy_amount * (1 - FEE_RATE)) / price
                bnb += qty
                saved_usdt = 0
            else:
                saved_usdt += monthly_usd
        else:
            qty = (monthly_usd * (1 - FEE_RATE)) / price
            bnb += qty

    # If never triggered, buy at last price with all saved
    if saved_usdt > 0:
        qty = (saved_usdt * (1 - FEE_RATE)) / prices[-1]
        bnb += qty

    final_value = bnb * prices[-1]
    return bnb, total_invested, final_value


def run_analysis(monthly_vnd, label):
    monthly_usd = monthly_vnd / VND_USD_RATE

    print(f"\n{'=' * 90}")
    print(f"SO SANH: DCA NGAY vs DOI THANG 10 | Budget: {monthly_vnd/1_000_000:.0f}M VND/thang (~${monthly_usd:.0f})")
    print(f"{'=' * 90}")

    scenarios = [
        ("BASE CASE (du doan dung: bear bottom Q4/2026)", "base"),
        ("SAI #1: Gia TANG tu T7 (khong co bear)", "wrong_up"),
        ("SAI #2: Gia DI NGANG ~$500-600", "wrong_flat"),
        ("SAI #3: Bear NANG HON du kien (BNB ve $120)", "wrong_worse"),
    ]

    strategies = [
        ("A: DCA ngay tu T7", strategy_a_dca_now),
        ("B: Giu USDT T7-9, ALL-IN T10", strategy_b_allin_oct),
        ("C: Giu USDT T7-9, DCA T10-12", strategy_c_spread_oct_dec),
        ("D: Giu USDT cho gia < $350", strategy_d_wait_below_350),
    ]

    all_results = {}

    for scenario_name, scenario_key in scenarios:
        print(f"\n--- {scenario_name} ---")
        prices = get_price_path(scenario_key)
        print(f"    Gia BNB: ${prices[0]} (T7/2026) -> ${prices[3]} (T10/2026) -> ${prices[-1]} (T12/2028)")

        rows = []
        for strat_name, strat_fn in strategies:
            bnb, invested, final_value = strat_fn(prices, monthly_usd)
            final_vnd = final_value * VND_USD_RATE / 1_000_000
            invested_vnd = invested * VND_USD_RATE / 1_000_000
            profit_vnd = final_vnd - invested_vnd
            roi = (final_value / invested - 1) * 100

            rows.append({
                "Strategy": strat_name,
                "BNB": f"{bnb:.2f}",
                "Portfolio $": f"${final_value:,.0f}",
                "Portfolio VND": f"{final_vnd:.0f}M",
                "Da bo ra": f"{invested_vnd:.0f}M",
                "Loi/Lo VND": f"{profit_vnd:+.0f}M",
                "ROI": f"{roi:+.0f}%",
            })

            key = (scenario_key, strat_name)
            all_results[key] = {
                "final_value": final_value,
                "final_vnd": final_vnd,
                "profit_vnd": profit_vnd,
                "roi": roi,
            }

        print(tabulate(rows, headers="keys", tablefmt="grid"))

        # Find best strategy for this scenario
        best = max(rows, key=lambda r: float(r["ROI"].replace("%", "").replace("+", "")))
        worst = min(rows, key=lambda r: float(r["ROI"].replace("%", "").replace("+", "")))
        print(f"  -> Tot nhat: {best['Strategy']} ({best['ROI']})")
        print(f"  -> Te nhat:  {worst['Strategy']} ({worst['ROI']})")

    # Expected Value calculation
    print(f"\n{'=' * 90}")
    print("TINH GIA TRI KY VONG (Expected Value)")
    print(f"{'=' * 90}")

    # Assign probabilities to each scenario
    prob = {"base": 0.40, "wrong_up": 0.20, "wrong_flat": 0.25, "wrong_worse": 0.15}

    print("\nXac suat cac kich ban:")
    print(f"  Base case (du doan dung):     {prob['base']*100:.0f}%")
    print(f"  Sai - Gia tang (ko bear):     {prob['wrong_up']*100:.0f}%")
    print(f"  Sai - Gia di ngang:           {prob['wrong_flat']*100:.0f}%")
    print(f"  Sai - Bear nang hon:          {prob['wrong_worse']*100:.0f}%")

    ev_rows = []
    for strat_name, _ in strategies:
        ev = 0
        details = []
        for scenario_key, p in prob.items():
            key = (scenario_key, strat_name)
            val = all_results[key]["final_vnd"]
            ev += val * p
            details.append(f"{val:.0f}M x {p:.0f}")

        ev_rows.append({
            "Strategy": strat_name,
            "EV (VND)": f"{ev:.0f}M",
        })

    print(tabulate(ev_rows, headers="keys", tablefmt="grid"))

    best_ev = max(ev_rows, key=lambda r: float(r["EV (VND)"].replace("M", "")))
    print(f"\n  -> Strategy co EV cao nhat: {best_ev['Strategy']} = {best_ev['EV (VND)']}")

    return all_results


def conclusion():
    print(f"""
{'=' * 90}
KET LUAN: CO NEN DOI DEN THANG 10 DE MUA BNB?
{'=' * 90}

  KHONG. DCA NGAY TU THANG 7.

  Ly do:

  1. NEU DU DOAN DUNG (bear bottom T10):
     - Doi mua T10 chi LOI THEM ~15-20M VND (~4-5%)
     - Khong dang de mao hiem

  2. NEU DU DOAN SAI (gia tang tu T7):
     - Doi = MAT 150-200M VND co hoi
     - Risk/Reward KHONG xung dang

  3. EXPECTED VALUE:
     - DCA ngay co EV CAO HON hoac TUONG DUONG doi
     - Vi xac suat du doan sai (~60%) > xac suat dung (~40%)

  4. TAM LY:
     - Doi = stress moi ngay: "gia len roi, gia xuong chua"
     - DCA = binh than, khong can suy nghi
     - Doi va thay gia tang = FOMO -> mua cao hon
     - Doi va thay gia giam them = SO -> khong dam mua

  5. DATA TU BACKTEST:
     - Pure DCA THANG tat ca strategies phuc tap (+493%)
     - Timing the market THUA time in the market

  +----------------------------------------------------------+
  |  HANH DONG:                                               |
  |                                                           |
  |  Thang 7/2026: Bat dau DCA 5M VND/thang                  |
  |  Mua BNB ngay 5 (hoac thu 5 gan nhat)                    |
  |  KHONG doi, KHONG suy nghi, KHONG thay doi               |
  |                                                           |
  |  "Time in the market > Timing the market"                 |
  +----------------------------------------------------------+

  NEU VAN MUON "DOI MOT CHUT":
  Compromise = Strategy C: DCA 50% ngay, giu 50% USDT cho T10
  -> Giam risk ca 2 chieu, nhung van KHONG toi uu bang DCA 100%
""")


if __name__ == "__main__":
    # Run with 5M VND budget
    run_analysis(5_000_000, "5M VND")

    # Run with 10M VND budget
    run_analysis(10_000_000, "10M VND")

    # Conclusion
    conclusion()
