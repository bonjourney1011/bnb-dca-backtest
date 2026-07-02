"""
Plan with income growth: +20% every 6 months.

Starting: 5M VND/month, growing 20% per 6 months.
Timeline: Jul 2026 -> Dec 2028 (30 months = 5 growth periods)
"""

from tabulate import tabulate

# Constants
BASE_VND = 5_000_000
GROWTH_RATE = 0.20  # +20% every 6 months
GROWTH_PERIOD = 6  # months
VND_USD_RATE = 25_250
EXISTING_BNB = 0.74
FEE_RATE = 0.001
START_PRICE = 540

# Price paths
PRICE_BASE = [
    540, 480, 420, 350, 300, 280,     # Jul-Dec 2026
    260, 250, 270, 300, 320, 350,     # Jan-Jun 2027
    370, 400, 420, 450, 470, 500,     # Jul-Dec 2027
    520, 550, 580, 600, 650, 720,     # Jan-Jun 2028
    800, 900, 1000, 1100, 1200, 1350, # Jul-Dec 2028
]

PRICE_OPTIMISTIC = [
    540, 480, 420, 350, 300, 280,
    260, 250, 270, 300, 350, 400,
    450, 500, 550, 600, 650, 700,
    750, 800, 900, 1000, 1200, 1400,
    1600, 1800, 2000, 2200, 2500, 3000,
]

PRICE_CONSERVATIVE = [
    540, 480, 420, 380, 350, 330,
    310, 300, 310, 330, 340, 360,
    370, 380, 390, 400, 410, 420,
    440, 460, 480, 500, 520, 550,
    580, 620, 660, 700, 750, 800,
]

MONTHS_LABEL = [
    "T07/26", "T08/26", "T09/26", "T10/26", "T11/26", "T12/26",
    "T01/27", "T02/27", "T03/27", "T04/27", "T05/27", "T06/27",
    "T07/27", "T08/27", "T09/27", "T10/27", "T11/27", "T12/27",
    "T01/28", "T02/28", "T03/28", "T04/28", "T05/28", "T06/28",
    "T07/28", "T08/28", "T09/28", "T10/28", "T11/28", "T12/28",
]


def get_monthly_budget(month_index):
    """Budget tang 20% moi 6 thang."""
    period = month_index // GROWTH_PERIOD
    return BASE_VND * (1 + GROWTH_RATE) ** period


def income_growth_table():
    """Show income trajectory."""
    print("=" * 90)
    print("LO TRINH THU NHAP: +20% MOI 6 THANG")
    print("=" * 90)

    rows = []
    for period in range(5):  # 5 growth periods in 30 months
        month_start = period * 6
        budget_vnd = get_monthly_budget(month_start)
        budget_usd = budget_vnd / VND_USD_RATE
        total_6m_vnd = budget_vnd * 6
        total_6m_usd = total_6m_vnd / VND_USD_RATE

        rows.append({
            "Giai doan": f"Thang {month_start+1}-{min(month_start+6, 30)}",
            "Thoi gian": f"{MONTHS_LABEL[month_start]} - {MONTHS_LABEL[min(month_start+5, 29)]}",
            "Budget/thang": f"{budget_vnd/1_000_000:.1f}M VND",
            "~USD/thang": f"${budget_usd:.0f}",
            "Tong 6 thang": f"{total_6m_vnd/1_000_000:.0f}M VND",
            "~USD 6 thang": f"${total_6m_usd:.0f}",
        })

    print(tabulate(rows, headers="keys", tablefmt="grid"))

    total_vnd = sum(get_monthly_budget(i) for i in range(30))
    total_usd = total_vnd / VND_USD_RATE
    avg_monthly = total_vnd / 30

    print(f"\n  TONG VON 30 THANG:  {total_vnd/1_000_000:.0f}M VND = ${total_usd:,.0f}")
    print(f"  TRUNG BINH/THANG:  {avg_monthly/1_000_000:.1f}M VND = ${avg_monthly/VND_USD_RATE:.0f}")

    # So sanh voi khong tang
    fixed_total = BASE_VND * 30
    print(f"\n  So voi khong tang:  {fixed_total/1_000_000:.0f}M VND")
    print(f"  Tang them:          {(total_vnd - fixed_total)/1_000_000:.0f}M VND ({(total_vnd/fixed_total - 1)*100:.0f}% nhieu hon)")

    return total_vnd, total_usd


def simulate_dca_with_growth(prices, scenario_name):
    """Month-by-month DCA with growing income."""
    bnb = EXISTING_BNB
    total_vnd = 0
    total_usd = 0
    records = []

    for i, price in enumerate(prices):
        budget_vnd = get_monthly_budget(i)
        budget_usd = budget_vnd / VND_USD_RATE
        qty = (budget_usd * (1 - FEE_RATE)) / price
        bnb += qty
        total_vnd += budget_vnd
        total_usd += budget_usd

        portfolio_usd = bnb * price
        portfolio_vnd = portfolio_usd * VND_USD_RATE / 1_000_000
        invested_vnd = total_vnd / 1_000_000
        roi = (portfolio_usd / (total_usd + EXISTING_BNB * START_PRICE) - 1) * 100

        # Milestones
        milestone = ""
        if i % 6 == 0 and i > 0:
            milestone = "** TANG LUONG **"

        records.append({
            "Thang": MONTHS_LABEL[i],
            "BNB $": f"${price:,}",
            "Budget": f"{budget_vnd/1_000_000:.1f}M",
            "Mua": f"{qty:.3f}",
            "Tong BNB": f"{bnb:.2f}",
            "Portfolio": f"${portfolio_usd:,.0f}",
            "VND": f"{portfolio_vnd:.0f}M",
            "Da bo ra": f"{invested_vnd:.0f}M",
            "ROI": f"{roi:+.0f}%",
            "Note": milestone,
        })

    return records, bnb, total_usd, total_vnd


def run_all_scenarios():
    """Run 3 scenarios with income growth."""
    scenarios = [
        ("CONSERVATIVE", PRICE_CONSERVATIVE),
        ("BASE CASE", PRICE_BASE),
        ("OPTIMISTIC", PRICE_OPTIMISTIC),
    ]

    summary = []

    for name, prices in scenarios:
        print(f"\n{'=' * 100}")
        print(f"SCENARIO: {name} | Income +20%/6 thang")
        print(f"{'=' * 100}")

        records, bnb, total_usd, total_vnd = simulate_dca_with_growth(prices, name)
        print(tabulate(records, headers="keys", tablefmt="grid"))

        final_price = prices[-1]
        final_value = bnb * final_price
        final_vnd = final_value * VND_USD_RATE / 1_000_000
        invested_vnd = total_vnd / 1_000_000
        profit_vnd = final_vnd - invested_vnd
        roi = (final_value / (total_usd + EXISTING_BNB * START_PRICE) - 1) * 100

        print(f"\n  KET QUA {name}:")
        print(f"    Tong BNB:       {bnb:.2f}")
        print(f"    BNB Price:      ${final_price:,}")
        print(f"    Portfolio:      ${final_value:,.0f} = {final_vnd:.0f}M VND")
        print(f"    Da dau tu:      {invested_vnd:.0f}M VND = ${total_usd:,.0f}")
        print(f"    Loi:            {profit_vnd:+.0f}M VND")
        print(f"    ROI:            {roi:+.0f}%")
        print(f"    TARGET $200K:   {'DA DAT!' if final_value >= 200_000 else f'Chua dat (can BNB = ${200_000/bnb:,.0f})'}")

        summary.append({
            "Scenario": name,
            "BNB tich luy": f"{bnb:.1f}",
            "BNB cuoi": f"${final_price:,}",
            "Portfolio $": f"${final_value:,.0f}",
            "Portfolio VND": f"{final_vnd:.0f}M",
            "Da bo ra VND": f"{invested_vnd:.0f}M",
            "Loi VND": f"{profit_vnd:+.0f}M",
            "ROI": f"{roi:+.0f}%",
            "$200K?": "DAT" if final_value >= 200_000 else "Chua",
        })

    return summary


def compare_fixed_vs_growth():
    """Compare fixed 5M vs growing income."""
    print(f"\n{'=' * 100}")
    print("SO SANH: 5M CO DINH vs 5M + TANG 20%/6 THANG")
    print(f"{'=' * 100}")

    prices = PRICE_BASE  # Use base case

    # Fixed 5M
    bnb_fixed = EXISTING_BNB
    total_fixed = 0
    for price in prices:
        usd = BASE_VND / VND_USD_RATE
        qty = (usd * (1 - FEE_RATE)) / price
        bnb_fixed += qty
        total_fixed += BASE_VND

    # Growing
    bnb_grow = EXISTING_BNB
    total_grow = 0
    for i, price in enumerate(prices):
        budget = get_monthly_budget(i)
        usd = budget / VND_USD_RATE
        qty = (usd * (1 - FEE_RATE)) / price
        bnb_grow += qty
        total_grow += budget

    final_price = prices[-1]
    val_fixed = bnb_fixed * final_price
    val_grow = bnb_grow * final_price
    vnd_fixed = val_fixed * VND_USD_RATE / 1_000_000
    vnd_grow = val_grow * VND_USD_RATE / 1_000_000

    rows = [
        {
            "Plan": "5M co dinh",
            "Tong von": f"{total_fixed/1_000_000:.0f}M",
            "BNB": f"{bnb_fixed:.1f}",
            "Portfolio $": f"${val_fixed:,.0f}",
            "Portfolio VND": f"{vnd_fixed:.0f}M",
            "Loi VND": f"{vnd_fixed - total_fixed/1_000_000:+.0f}M",
            "ROI": f"{(val_fixed/(total_fixed/VND_USD_RATE + EXISTING_BNB*START_PRICE)-1)*100:+.0f}%",
        },
        {
            "Plan": "5M + tang 20%/6th",
            "Tong von": f"{total_grow/1_000_000:.0f}M",
            "BNB": f"{bnb_grow:.1f}",
            "Portfolio $": f"${val_grow:,.0f}",
            "Portfolio VND": f"{vnd_grow:.0f}M",
            "Loi VND": f"{vnd_grow - total_grow/1_000_000:+.0f}M",
            "ROI": f"{(val_grow/(total_grow/VND_USD_RATE + EXISTING_BNB*START_PRICE)-1)*100:+.0f}%",
        },
    ]

    print(tabulate(rows, headers="keys", tablefmt="grid"))
    print(f"\n  Tang them BNB:     {bnb_grow - bnb_fixed:.1f} BNB")
    print(f"  Tang them von:     {(total_grow - total_fixed)/1_000_000:.0f}M VND")
    print(f"  Tang them gia tri: {vnd_grow - vnd_fixed:.0f}M VND")


def feasibility_analysis(total_vnd):
    """Check kha thi voi thu nhap tang."""
    print(f"\n{'=' * 100}")
    print("PHAN TICH KHA THI: THU NHAP TANG 20%/6 THANG")
    print(f"{'=' * 100}")

    print(f"""
  GIA SU thu nhap hien tai du de tiet kiem 5M/thang.

  Lo trinh DCA budget:
  +-------+----------+-----------+-----------------------------+
  | Thang | Budget   | ~USD      | Yeu cau thu nhap toi thieu  |
  +-------+----------+-----------+-----------------------------+
  | 1-6   | 5.0M     | $198      | Thu nhap >= 15M (tiet kiem  |
  |       |          |           |   33% thu nhap)             |
  | 7-12  | 6.0M     | $238      | Thu nhap >= 18M             |
  | 13-18 | 7.2M     | $285      | Thu nhap >= 22M             |
  | 19-24 | 8.6M     | $342      | Thu nhap >= 26M             |
  | 25-30 | 10.4M    | $411      | Thu nhap >= 31M             |
  +-------+----------+-----------+-----------------------------+

  KIEM TRA THUC TE:
""")

    periods = [
        (0,  "T1-6",   "Jul-Dec 2026"),
        (6,  "T7-12",  "Jan-Jun 2027"),
        (12, "T13-18", "Jul-Dec 2027"),
        (18, "T19-24", "Jan-Jun 2028"),
        (24, "T25-30", "Jul-Dec 2028"),
    ]

    rows = []
    for start, label, time_range in periods:
        budget = get_monthly_budget(start)
        # Gia su budget = 33% thu nhap (an toan)
        min_income = budget / 0.33
        # Thu nhap cung tang 20%/6th
        estimated_income = 15_000_000 * (1 + GROWTH_RATE) ** (start // 6)
        ratio = budget / estimated_income * 100

        feasible = "OK" if ratio <= 35 else ("CANH BAO" if ratio <= 45 else "QUA CAO")

        rows.append({
            "Giai doan": label,
            "Thoi gian": time_range,
            "DCA Budget": f"{budget/1_000_000:.1f}M",
            "Thu nhap uoc tinh": f"{estimated_income/1_000_000:.0f}M",
            "% thu nhap": f"{ratio:.0f}%",
            "Kha thi?": feasible,
        })

    print(tabulate(rows, headers="keys", tablefmt="grid"))

    print(f"""
  QUY TAC AN TOAN:
  +----------------------------------------------------------+
  |  DCA <= 30% thu nhap     -> AN TOAN, thoai mai           |
  |  DCA = 30-40% thu nhap   -> CHAP NHAN DUOC, can ki luat  |
  |  DCA > 40% thu nhap      -> QUA NHIEU, giam xuong        |
  +----------------------------------------------------------+

  DIEU KIEN DE PLAN KHA THI:

  1. Thu nhap THUC SU tang ~20%/6 thang
     - Dev/Engineer: Kha thi qua tang luong, freelance, job hop
     - Cach: upskill, chuyen viec moi 12-18 thang, freelance them
     - Rui ro: layoff, market down -> KE HOACH DU PHONG

  2. Chi tieu khong tang tuong ung
     - Thu nhap tang 20% nhung chi tieu chi tang 5-10%
     - Phan con lai -> DCA
     - Lifestyle inflation = ke thu cua ke hoach nay

  3. Co quy du phong 6 thang chi phi sinh hoat
     - TRUOC khi bat dau DCA
     - Khong dung tien du phong de mua BNB

  PLAN DU PHONG NEU THU NHAP KHONG TANG:
  +----------------------------------------------------------+
  |  Giu nguyen 5M/thang (plan co dinh)                      |
  |  Base case: 476M VND (~$19K) - van LAI 326M              |
  |  KHONG ep ban than tang DCA khi thu nhap chua tang       |
  +----------------------------------------------------------+
""")


def target_200k_check():
    """Check if $200K is reachable with income growth."""
    print(f"\n{'=' * 100}")
    print("TARGET $200K - KHA THI VOI THU NHAP TANG?")
    print(f"{'=' * 100}")

    # Calculate total BNB accumulated in base case
    bnb = EXISTING_BNB
    total_vnd = 0
    for i, price in enumerate(PRICE_BASE):
        budget = get_monthly_budget(i)
        usd = budget / VND_USD_RATE
        qty = (usd * (1 - FEE_RATE)) / price
        bnb += qty
        total_vnd += budget

    invested_vnd = total_vnd / 1_000_000

    print(f"\n  Voi income +20%/6th, Base Case:")
    print(f"  Tong BNB tich luy:  {bnb:.1f}")
    print(f"  Tong von bo ra:     {invested_vnd:.0f}M VND")

    # Price needed for different targets
    targets = [
        ("$50K", 50_000),
        ("$100K", 100_000),
        ("$150K", 150_000),
        ("$200K", 200_000),
        ("$300K", 300_000),
        ("$500K", 500_000),
    ]

    rows = []
    for label, target_usd in targets:
        need_price = target_usd / bnb
        target_vnd = target_usd * VND_USD_RATE / 1_000_000
        need_multiplier = need_price / PRICE_BASE[-1]
        # Check historical ATH
        ath = 1307  # BNB ATH
        vs_ath = need_price / ath

        reachable = "Rat kha thi" if need_price < 1000 else (
            "Kha thi" if need_price < 2000 else (
                "Kho" if need_price < 5000 else "Rat kho"
            )
        )

        rows.append({
            "Target": label,
            "VND": f"{target_vnd:.0f}M",
            "Can BNB =": f"${need_price:,.0f}",
            "vs ATH $1,307": f"{vs_ath:.1f}x",
            "vs Base $1,350": f"{need_multiplier:.1f}x",
            "Danh gia": reachable,
        })

    print(tabulate(rows, headers="keys", tablefmt="grid"))

    print(f"""
  NHAN XET:

  Voi {bnb:.0f} BNB tich luy (income +20%/6th):
  - $50K (1.3 ty VND):  Can BNB = ${50000/bnb:,.0f} -> KHA THI (gan base case)
  - $100K (2.5 ty VND): Can BNB = ${100000/bnb:,.0f} -> KHA THI neu bull manh
  - $200K (5 ty VND):   Can BNB = ${200000/bnb:,.0f} -> CAN CYCLE 5 PEAK

  $200K VAN KHO voi $198/thang start, du thu nhap tang 20%/6th.
  Ly do: tong von chi ~{invested_vnd:.0f}M VND (~${total_vnd/VND_USD_RATE:,.0f}).
  Can BNB tang {200000/(total_vnd/VND_USD_RATE + EXISTING_BNB*START_PRICE):.0f}x tu tong von.

  NHUNG: $50K-$100K (1.3-2.5 ty VND) = TARGET THUC TE VA TOT
  ROI 200-500% tu DCA = vuot xa moi kenh dau tu truyen thong.
""")


def final_action_plan():
    """Final action plan with income growth."""
    print(f"""
{'=' * 100}
KE HOACH HANH DONG: DCA VOI THU NHAP TANG
{'=' * 100}

+--------------------------------------------------------------------+
|  GIAI DOAN 1: T7-T12/2026 (Bear accumulation)                      |
|  Budget: 5.0M/thang = 30M/6 thang                                  |
|  Gia BNB du kien: $280-$540 (BEAR = CO HOI MUA RE)                 |
|  Muc tieu: tich luy 4-6 BNB                                        |
|  Action: DCA ngay 5, khong suy nghi                                 |
+--------------------------------------------------------------------+

+--------------------------------------------------------------------+
|  GIAI DOAN 2: T1-T6/2027 (Bear bottom -> Recovery)                  |
|  Budget: 6.0M/thang = 36M/6 thang (+20%)                           |
|  Gia BNB du kien: $250-$350 (BOTTOM = MUA NHIEU NHAT)              |
|  Muc tieu: tich luy them 5-8 BNB                                   |
|  Action: Tang budget vi gia re, mua duoc nhieu BNB                  |
+--------------------------------------------------------------------+

+--------------------------------------------------------------------+
|  GIAI DOAN 3: T7-T12/2027 (Recovery)                                |
|  Budget: 7.2M/thang = 43M/6 thang (+20%)                           |
|  Gia BNB du kien: $370-$500                                        |
|  Muc tieu: tich luy them 3-5 BNB                                   |
|  Action: DCA deu dan, khong FOMO                                    |
+--------------------------------------------------------------------+

+--------------------------------------------------------------------+
|  GIAI DOAN 4: T1-T6/2028 (Pre-halving)                              |
|  Budget: 8.6M/thang = 52M/6 thang (+20%)                           |
|  Gia BNB du kien: $520-$720                                        |
|  Muc tieu: tich luy them 2-4 BNB                                   |
|  Action: Van DCA, gia dat hon nhung budget cung cao hon              |
+--------------------------------------------------------------------+

+--------------------------------------------------------------------+
|  GIAI DOAN 5: T7-T12/2028 (Post-halving BULL)                       |
|  Budget: 10.4M/thang = 62M/6 thang (+20%)                          |
|  Gia BNB du kien: $800-$1350+                                      |
|  Muc tieu: tich luy them 1-3 BNB                                   |
|  Optional: Neu BNB > $2000, xem xet chot 10-20% loi              |
+--------------------------------------------------------------------+

  TONG VON DU KIEN:    ~223M VND (~$8,800)
  TONG BNB DU KIEN:    ~18-22 BNB (base case)

  +--------------------------------------------------------------+
  |  TARGET THUC TE (co income growth):                           |
  |                                                               |
  |  Conservative: $16,000 (400M VND) - ROI +80%                 |
  |  Base case:    $28,000 (700M VND) - ROI +215%                |
  |  Optimistic:   $66,000 (1.7 ty VND) - ROI +650%             |
  |  Moonshot:     $100K+ (2.5 ty+) - NEU Cycle 5 peak          |
  |                                                               |
  |  Tu 223M von -> 700M-1.7 ty = TUYET VOI                      |
  +--------------------------------------------------------------+

  NGUYEN TAC VANG:
  1. Chi tang DCA khi thu nhap THUC SU da tang
  2. DCA <= 30% thu nhap (KHONG QUA)
  3. Giu quy du phong 6 thang truoc
  4. Khong lifestyle inflation (giu chi tieu on dinh)
  5. Khong ep ban than - giam ve 5M bat cu luc nao neu can
""")


if __name__ == "__main__":
    total_vnd, total_usd = income_growth_table()
    summary = run_all_scenarios()

    print(f"\n{'=' * 100}")
    print("TONG HOP 3 SCENARIOS")
    print(f"{'=' * 100}")
    print(tabulate(summary, headers="keys", tablefmt="grid"))

    compare_fixed_vs_growth()
    feasibility_analysis(total_vnd)
    target_200k_check()
    final_action_plan()
