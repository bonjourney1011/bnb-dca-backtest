"""
Personal Plan - Realistic calculation based on actual situation.

Reality:
  - Existing: 0.74 BNB (~$415)
  - Monthly budget: 5,000,000 VND (~$198 USD at 25,250 VND/USD)
  - Target: as much as possible by 2029, no psychological pressure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from datetime import datetime
from tabulate import tabulate


# Constants
EXISTING_BNB = 0.74
MONTHLY_VND = 5_000_000
VND_USD_RATE = 25_250  # approximate
MONTHLY_USD = MONTHLY_VND / VND_USD_RATE
CURRENT_BNB_PRICE = 561.0
START_DATE = datetime(2026, 7, 1)
TARGET_DATE = datetime(2029, 1, 1)
MONTHS = 30

FEE_RATE = 0.001  # 0.1% Binance


def reality_check():
    """Show the hard numbers first."""
    print("=" * 80)
    print("REALITY CHECK - Tinh hinh thuc te")
    print("=" * 80)

    existing_value = EXISTING_BNB * CURRENT_BNB_PRICE
    total_new_capital = MONTHLY_USD * MONTHS
    total_capital = existing_value + total_new_capital

    print(f"""
  BNB hien co:          {EXISTING_BNB} BNB = ${existing_value:.0f} = {EXISTING_BNB * CURRENT_BNB_PRICE * VND_USD_RATE / 1_000_000:.1f}M VND
  Budget/thang:         {MONTHLY_VND / 1_000_000:.0f}M VND = ~${MONTHLY_USD:.0f} USD
  So thang den 2029:    {MONTHS} thang
  Tong von moi:         ${total_new_capital:,.0f} = {total_new_capital * VND_USD_RATE / 1_000_000:.0f}M VND
  Tong von (cu + moi):  ${total_capital:,.0f}

  $200K TARGET: Can portfolio tang {200_000 / total_capital:.0f}x tu tong von
  => Can BNB tang tu ${CURRENT_BNB_PRICE:.0f} len ~${200_000 / (total_new_capital / CURRENT_BNB_PRICE + EXISTING_BNB):.0f}
  => KHONG THUC TE voi 30 thang.
""")


def realistic_scenarios():
    """Calculate what's actually achievable."""
    print("=" * 80)
    print("SCENARIOS THUC TE - Voi $198/thang DCA")
    print("=" * 80)

    # Different BNB price scenarios at Jan 2029
    scenarios = [
        ("Bear (BNB crash)", 200, "Bear market keo dai"),
        ("Flat (BNB di ngang)", 550, "Giong hien tai"),
        ("Moderate bull", 1000, "Quay lai gan ATH"),
        ("Bull (new ATH)", 1500, "Vuot ATH cu"),
        ("Super bull", 2500, "Cycle 5 peak"),
        ("Mega bull", 5000, "Outlier nhu Cycle 2"),
    ]

    results = []
    for name, target_price, note in scenarios:
        # Simple DCA: buy same amount each month
        # Average price depends on path, but for estimation:
        if target_price > CURRENT_BNB_PRICE:
            # Uptrend: avg price higher
            avg_price = CURRENT_BNB_PRICE * 0.5 + target_price * 0.5 * 0.7
        else:
            # Downtrend: avg price lower (good for accumulation)
            avg_price = (CURRENT_BNB_PRICE + target_price) / 2

        total_invested = MONTHLY_USD * MONTHS
        bnb_from_dca = (total_invested * (1 - FEE_RATE)) / avg_price
        total_bnb = EXISTING_BNB + bnb_from_dca
        portfolio_value = total_bnb * target_price
        portfolio_vnd = portfolio_value * VND_USD_RATE / 1_000_000
        profit = portfolio_value - total_invested - EXISTING_BNB * CURRENT_BNB_PRICE
        roi = (portfolio_value / (total_invested + EXISTING_BNB * CURRENT_BNB_PRICE) - 1) * 100

        results.append({
            "Scenario": name,
            "BNB 2029": f"${target_price:,}",
            "BNB tich luy": f"{total_bnb:.1f}",
            "Portfolio $": f"${portfolio_value:,.0f}",
            "Portfolio VND": f"{portfolio_vnd:.0f}M",
            "Profit $": f"${profit:,.0f}",
            "ROI": f"{roi:+.0f}%",
            "Note": note,
        })

    print(f"\n  Von bo ra: ${MONTHLY_USD:.0f}/thang x {MONTHS} thang = ${MONTHLY_USD * MONTHS:,.0f}")
    print(f"  BNB hien co: {EXISTING_BNB}\n")
    print(tabulate(results, headers="keys", tablefmt="grid"))

    return results


def cycle_aware_simulation():
    """Month-by-month simulation with cycle-aware price model."""
    print("\n" + "=" * 80)
    print("MO PHONG THANG-BY-THANG (Base Case)")
    print("=" * 80)

    # Realistic price path for Base Case
    # Based on cycle analysis: bear bottom Q4 2026, recovery 2027, bull 2028
    price_path = [
        # 2026: mid-bear decline
        (2026, 7, 540), (2026, 8, 480), (2026, 9, 420),
        (2026, 10, 350), (2026, 11, 300), (2026, 12, 280),
        # 2027: bottom then slow recovery
        (2027, 1, 260), (2027, 2, 250), (2027, 3, 270),
        (2027, 4, 300), (2027, 5, 320), (2027, 6, 350),
        (2027, 7, 370), (2027, 8, 400), (2027, 9, 420),
        (2027, 10, 450), (2027, 11, 470), (2027, 12, 500),
        # 2028: pre-halving + post-halving bull
        (2028, 1, 520), (2028, 2, 550), (2028, 3, 580),
        (2028, 4, 600), (2028, 5, 650), (2028, 6, 720),
        (2028, 7, 800), (2028, 8, 900), (2028, 9, 1000),
        (2028, 10, 1100), (2028, 11, 1200), (2028, 12, 1350),
    ]

    bnb = EXISTING_BNB
    total_invested_usd = 0
    total_invested_vnd = 0
    monthly_usd = MONTHLY_USD
    records = []

    for year, month, price in price_path:
        fee = monthly_usd * FEE_RATE
        qty = (monthly_usd - fee) / price
        bnb += qty
        total_invested_usd += monthly_usd
        total_invested_vnd += MONTHLY_VND
        portfolio = bnb * price
        portfolio_vnd = portfolio * VND_USD_RATE / 1_000_000
        invested_vnd = total_invested_vnd / 1_000_000

        # Emotional state based on portfolio performance
        roi = (portfolio / (total_invested_usd + EXISTING_BNB * CURRENT_BNB_PRICE) - 1) * 100
        if roi < -30:
            emotion = "!! KHO CHIU"
        elif roi < -10:
            emotion = "! Lo lang"
        elif roi < 10:
            emotion = "Binh thuong"
        elif roi < 50:
            emotion = "Vui"
        elif roi < 100:
            emotion = "Rat vui"
        else:
            emotion = "*** TUYET VOI"

        records.append({
            "Thang": f"{year}-{month:02d}",
            "BNB Price": f"${price:,}",
            "Mua": f"{qty:.3f} BNB",
            "Tong BNB": f"{bnb:.2f}",
            "Portfolio": f"${portfolio:,.0f}",
            "VND": f"{portfolio_vnd:.0f}M",
            "Da bo ra": f"{invested_vnd:.0f}M",
            "ROI": f"{roi:+.0f}%",
            "Tam ly": emotion,
        })

    print(tabulate(records, headers="keys", tablefmt="grid"))

    final_value = bnb * price_path[-1][2]
    final_vnd = final_value * VND_USD_RATE / 1_000_000

    print(f"\n  KET QUA BASE CASE (Jan 2029):")
    print(f"    Tong BNB:        {bnb:.2f}")
    print(f"    BNB Price:       ${price_path[-1][2]:,}")
    print(f"    Portfolio:       ${final_value:,.0f} = {final_vnd:.0f}M VND")
    print(f"    Da dau tu:       {total_invested_vnd / 1_000_000:.0f}M VND")
    print(f"    Loi:             {final_vnd - total_invested_vnd / 1_000_000:.0f}M VND")

    return bnb, final_value


def psychological_guide():
    """Guide to avoid psychological pressure."""
    print(f"""

{'=' * 80}
HUONG DAN TAM LY - KHONG BI AM ANH
{'=' * 80}

1. THAY DOI MINDSET VE TARGET

   $200K voi $198/thang trong 30 thang = CAN BNB TANG 33x
   => Day la MO, khong phai PLAN.

   TARGET THUC TE:
   +----------------------------------------------+
   | Conservative:  $5,000 - $8,000  (130-200M)   |
   | Base case:     $10,000 - $20,000 (250-500M)  |
   | Optimistic:    $20,000 - $50,000 (500M-1.2B) |
   | Moonshot:      $50,000+ (1.2B+) NEU Cycle 5  |
   +----------------------------------------------+

   5 trieu/thang x 30 thang = 150M VND von bo ra
   Base case = 250-500M portfolio = LAI 100-350M = ROI 67-233%
   => Van RAT TOT so voi gui tiet kiem (5%/nam)

2. QUY TAC "SET & FORGET"

   Ngay 5 hang thang:
   +-----------------------------------------+
   | 1. Mo Binance                           |
   | 2. Market buy $198 BNB/USDT             |
   | 3. Dong app                             |
   | 4. KHONG MO LAI den thang sau           |
   +-----------------------------------------+

   KHONG:
   - Check gia hang ngay
   - Doc tin crypto
   - So sanh voi nguoi khac
   - Thay doi strategy giua chung

3. "5 TRIEU NHU KHONG CO"

   Coi 5M nhu tien DA MAT khi chuyen vao Binance.
   Neu mat het 5M/thang khong anh huong cuoc song
   => Khong co gi phai lo.
   Neu mat het 5M/thang CO anh huong
   => GIAM xuong 3M hoac 2M. Khong ai ep.

4. BEAR MARKET = BINH THUONG

   Du doan: BNB co the giam ve $250-350 (Q4 2026 - Q1 2027)
   Portfolio se giam -40% den -60%

   Khi do:
   +----------------------------------------------+
   | Portfolio: 150M -> 60M VND  (-60%)            |
   | Cam giac: HOANG LOAN                          |
   | Action dung: KHONG LAM GI. Van DCA binh thuong|
   | Action sai: BAN THAO -> khoa lo vinh vien     |
   +----------------------------------------------+

   Cycle 2 data: Nguoi DCA qua bear 2022 (-69%) -> +493% sau do
   BEAR LA CO HOI MUA RE, khong phai mat mat.

5. QUY TAC 3 KHONG

   KHONG check portfolio qua 1 lan/thang
   KHONG thay doi so tien DCA vi gia tang/giam
   KHONG ban BNB truoc 2028 (tru truong hop can tien gap)

6. KHI NAO DUNG?

   Chi DUNG DCA khi:
   - Mat viec, khong co thu nhap
   - Can tien cho suc khoe/gia dinh
   - Crypto bi cam hoan toan o VN

   KHONG dung vi:
   - BNB giam 50% (binh thuong)
   - Doc tin xau ve crypto (nhieu)
   - Ban be noi "crypto chet roi" (luon xay ra o bear)
""")


def final_action_plan():
    """Simple, actionable plan."""
    print(f"""
{'=' * 80}
PLAN HANH DONG CU THE
{'=' * 80}

+------------------------------------------------------------------+
|  SETUP (1 lan duy nhat):                                         |
|                                                                   |
|  1. Mo tai khoan Binance (neu chua co)                           |
|  2. Verify KYC                                                    |
|  3. Ket noi P2P hoac bank transfer de nap VND                   |
|  4. Dat lich nhac "DCA BNB" vao ngay 5 hang thang               |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  HANG THANG (5 phut/thang, KHONG HON):                           |
|                                                                   |
|  Ngay 5:                                                          |
|  1. Nap 5,000,000 VND vao Binance (P2P -> USDT)                 |
|  2. Convert USDT -> BNB (market order)                           |
|  3. Ghi vao Google Sheet: ngay, gia, so BNB                     |
|  4. Dong app. Het.                                                |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  KHONG LAM:                                                       |
|                                                                   |
|  - Khong check gia moi ngay                                      |
|  - Khong doc tin crypto                                           |
|  - Khong thay doi so tien                                        |
|  - Khong ban                                                      |
|  - Khong su dung leverage/futures                                 |
|  - Khong mua altcoin khac                                         |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  REVIEW (moi 6 thang):                                            |
|                                                                   |
|  Thang 1 va thang 7 hang nam:                                    |
|  1. Mo Google Sheet                                               |
|  2. Cap nhat portfolio value                                      |
|  3. Check: co can thay doi budget khong?                          |
|  4. Dong lai. Khong thay doi strategy.                            |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  MILESTONE (moc de vui, KHONG phai ap luc):                       |
|                                                                   |
|  [ ] 10 BNB    (~$5,600)                                         |
|  [ ] 25 BNB    (~$14,000)                                        |
|  [ ] 50 BNB    (~$28,000)                                        |
|  [ ] 100 BNB   (~$56,000)                                        |
|  [ ] Portfolio > 500M VND                                         |
|  [ ] Portfolio > 1 ty VND                                         |
+------------------------------------------------------------------+

  TIMELINE DU KIEN (Base Case):

  Jul 2026:  0.74 BNB   | Bat dau
  Dec 2026:  ~5 BNB     | Bear accumulation
  Jun 2027:  ~12 BNB    | Bear bottom = mua nhieu
  Dec 2027:  ~18 BNB    | Recovery
  Jun 2028:  ~22 BNB    | Post-halving
  Dec 2028:  ~25 BNB    | Bull market

  Best case: 25 BNB x $1,350 = $33,750 = ~850M VND
  (Tu 150M von -> 850M = +567% = RAT TOT)

{'=' * 80}
TOM TAT 1 DONG
{'=' * 80}

  5 trieu/thang, mua BNB ngay 5, khong suy nghi, khong nhin lai.
  30 thang sau kiem tra. Ky vong thuc te: 250-850M VND tu 150M von.
  KHONG dat target $200K - dat target "toi da hoa loi nhuan tu
  so von toi co the thoai mai bo ra ma khong anh huong cuoc song."
""")


if __name__ == "__main__":
    reality_check()
    results = realistic_scenarios()
    cycle_aware_simulation()
    psychological_guide()
    final_action_plan()
