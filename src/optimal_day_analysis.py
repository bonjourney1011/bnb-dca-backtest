"""
Analyze optimal day-of-month to buy BNB.

User flow: Salary on 5th → Buy USDT (VND→USDT) → Buy BNB (USDT→BNB)
Question: Which day after the 5th gives the best average entry price?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from tabulate import tabulate
from src.data_fetcher import load_data


def analyze_optimal_buy_day(df: pd.DataFrame, monthly_capital: float = 500.0):
    """Test buying on each day of month (5th through 28th) and compare results."""
    print("=" * 90)
    print("PHÂN TÍCH NGÀY MUA TỐI ƯU TRONG THÁNG")
    print("Giả định: Có vốn từ ngày 5, có thể mua bất kỳ ngày nào từ 5-28")
    print("=" * 90)

    results = {}

    for buy_day in range(1, 29):
        total_bnb = 0.0
        total_invested = 0.0
        buy_prices = []
        months_bought = set()

        for date, row in df.iterrows():
            month_key = (date.year, date.month)
            if date.day >= buy_day and month_key not in months_bought:
                months_bought.add(month_key)
                price = row["close"]
                fee = monthly_capital * 0.001
                qty = (monthly_capital - fee) / price
                total_bnb += qty
                total_invested += monthly_capital
                buy_prices.append(price)

        if total_invested > 0:
            avg_price = total_invested / total_bnb
            final_value = total_bnb * df["close"].iloc[-1]
            total_return = (final_value / total_invested - 1) * 100

            results[buy_day] = {
                "buy_day": buy_day,
                "avg_buy_price": avg_price,
                "total_bnb": total_bnb,
                "total_invested": total_invested,
                "final_value": final_value,
                "total_return_pct": total_return,
                "num_buys": len(buy_prices),
                "median_price": np.median(buy_prices),
                "min_price": np.min(buy_prices),
                "max_price": np.max(buy_prices),
            }

    return results


def analyze_day_of_week_effect(df: pd.DataFrame):
    """Analyze if certain days of the week have consistently lower BNB prices."""
    print("\n" + "=" * 90)
    print("PHÂN TÍCH HIỆU ỨNG NGÀY TRONG TUẦN (Day-of-Week Effect)")
    print("Giá BNB trung bình theo thứ trong tuần, có ngày nào rẻ hơn không?")
    print("=" * 90)

    df_copy = df.copy()
    df_copy["weekday"] = df_copy.index.dayofweek  # 0=Mon, 6=Sun
    df_copy["daily_return"] = df_copy["close"].pct_change() * 100

    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    rows = []
    for wd in range(7):
        subset = df_copy[df_copy["weekday"] == wd]
        returns = subset["daily_return"].dropna()
        rows.append({
            "Day": weekday_names[wd],
            "Avg Return %": f"{returns.mean():.4f}%",
            "Median Return %": f"{returns.median():.4f}%",
            "Positive %": f"{(returns > 0).mean() * 100:.1f}%",
            "Avg Volume": f"{subset['volume'].mean():,.0f}",
            "Count": len(returns),
        })

    print(tabulate(rows, headers="keys", tablefmt="grid"))

    # Test: nếu chỉ mua vào ngày có avg return thấp nhất (giá giảm = mua rẻ)
    worst_day = min(range(7), key=lambda wd: df_copy[df_copy["weekday"] == wd]["daily_return"].dropna().mean())
    best_day = max(range(7), key=lambda wd: df_copy[df_copy["weekday"] == wd]["daily_return"].dropna().mean())
    print(f"\nNgày return thấp nhất (mua rẻ nhất): {weekday_names[worst_day]}")
    print(f"Ngày return cao nhất (mua đắt nhất): {weekday_names[best_day]}")

    return df_copy


def analyze_intramonth_pattern(df: pd.DataFrame):
    """Analyze price patterns within each month - early vs mid vs late month."""
    print("\n" + "=" * 90)
    print("PHÂN TÍCH GIÁ THEO GIAI ĐOẠN TRONG THÁNG")
    print("Giá BNB có xu hướng cao/thấp ở đầu/giữa/cuối tháng không?")
    print("=" * 90)

    df_copy = df.copy()
    # Normalize price within each month (% deviation from monthly average)
    df_copy["month_key"] = df_copy.index.to_period("M")
    monthly_avg = df_copy.groupby("month_key")["close"].transform("mean")
    df_copy["price_vs_avg"] = (df_copy["close"] / monthly_avg - 1) * 100
    df_copy["day_of_month"] = df_copy.index.day

    # Group by day of month
    rows = []
    for day in range(1, 29):
        subset = df_copy[df_copy["day_of_month"] == day]
        if len(subset) > 10:
            rows.append({
                "Day": day,
                "Avg vs Monthly Mean": f"{subset['price_vs_avg'].mean():.3f}%",
                "Median vs Monthly Mean": f"{subset['price_vs_avg'].median():.3f}%",
                "Cheaper than avg %": f"{(subset['price_vs_avg'] < 0).mean() * 100:.0f}%",
                "Samples": len(subset),
            })

    print(tabulate(rows, headers="keys", tablefmt="grid"))

    # Find cheapest days
    day_avg = {day: df_copy[df_copy["day_of_month"] == day]["price_vs_avg"].mean()
               for day in range(1, 29)
               if len(df_copy[df_copy["day_of_month"] == day]) > 10}

    cheapest_days = sorted(day_avg.items(), key=lambda x: x[1])[:5]
    most_expensive_days = sorted(day_avg.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\nTop 5 ngày RẺ nhất (so với giá trung bình tháng):")
    for day, pct in cheapest_days:
        print(f"  Ngày {day:2d}: {pct:+.3f}%")

    print(f"\nTop 5 ngày ĐẮT nhất:")
    for day, pct in most_expensive_days:
        print(f"  Ngày {day:2d}: {pct:+.3f}%")

    return day_avg


def analyze_delay_strategy(df: pd.DataFrame, monthly_capital: float = 500.0):
    """
    Test: salary on 5th, but delay buy by N days.
    Find optimal delay that maximizes returns.
    """
    print("\n" + "=" * 90)
    print("PHÂN TÍCH CHIẾN LƯỢC TRÌ HOÃN MUA")
    print("Có vốn ngày 5, nhưng chờ thêm N ngày mới mua BNB")
    print("=" * 90)

    results = []
    for delay in range(0, 24):  # delay 0 to 23 days after 5th
        target_day = 5 + delay
        if target_day > 28:
            target_day = 28

        total_bnb = 0.0
        total_invested = 0.0
        months_bought = set()

        for date, row in df.iterrows():
            month_key = (date.year, date.month)
            if date.day >= target_day and month_key not in months_bought:
                months_bought.add(month_key)
                price = row["close"]
                fee = monthly_capital * 0.001
                qty = (monthly_capital - fee) / price
                total_bnb += qty
                total_invested += monthly_capital

        if total_invested > 0:
            final_value = total_bnb * df["close"].iloc[-1]
            total_return = (final_value / total_invested - 1) * 100
            avg_price = total_invested / total_bnb

            results.append({
                "Delay (days)": delay,
                "Buy Day": f"~{target_day}",
                "Avg Price": f"${avg_price:.2f}",
                "Total BNB": f"{total_bnb:.2f}",
                "Final Value": f"${final_value:,.0f}",
                "Return %": f"{total_return:.1f}%",
                "vs Day5": "",
            })

    # Calculate difference vs day 5
    day5_return = float(results[0]["Return %"].replace("%", ""))
    for r in results:
        ret = float(r["Return %"].replace("%", ""))
        diff = ret - day5_return
        r["vs Day5"] = f"{diff:+.1f}%"

    print(tabulate(results, headers="keys", tablefmt="grid"))

    # Find optimal
    best = max(results, key=lambda x: float(x["Return %"].replace("%", "")))
    worst = min(results, key=lambda x: float(x["Return %"].replace("%", "")))
    print(f"\nNgày mua TỐI ƯU: delay {best['Delay (days)']} ngày (mua ~ngày {best['Buy Day']}) → {best['Return %']}")
    print(f"Ngày mua TỆ NHẤT: delay {worst['Delay (days)']} ngày (mua ~ngày {worst['Buy Day']}) → {worst['Return %']}")
    print(f"Chênh lệch max: {float(best['Return %'].replace('%','')) - float(worst['Return %'].replace('%','')):.1f}%")

    return results


def analyze_window_strategy(df: pd.DataFrame, monthly_capital: float = 500.0):
    """
    Test: salary on 5th, but find the LOWEST price within a window of N days after 5th.
    Simulates: "chờ giá rẻ nhất trong N ngày sau khi có lương"
    """
    print("\n" + "=" * 90)
    print("CHIẾN LƯỢC CHỜ GIÁ TỐT NHẤT TRONG CỬA SỔ N NGÀY")
    print("Có vốn ngày 5, chờ tối đa N ngày để mua giá thấp nhất")
    print("=" * 90)

    results = []
    for window in [0, 1, 2, 3, 5, 7, 10, 14, 20]:
        total_bnb = 0.0
        total_invested = 0.0
        months_processed = set()
        buy_prices = []

        # Build monthly windows
        months = df.index.to_period("M").unique()
        for month in months:
            month_key = (month.year, month.month)
            if month_key in months_processed:
                continue
            months_processed.add(month_key)

            # Get data for this month starting from day 5
            month_data = df[(df.index.year == month.year) &
                           (df.index.month == month.month) &
                           (df.index.day >= 5)]

            if len(month_data) == 0:
                continue

            if window == 0:
                # Buy on first available day >= 5
                buy_row = month_data.iloc[0]
            else:
                # Find lowest close within window days from day 5
                window_data = month_data.iloc[:min(window + 1, len(month_data))]
                buy_idx = window_data["close"].idxmin()
                buy_row = df.loc[buy_idx]

            price = buy_row["close"]
            fee = monthly_capital * 0.001
            qty = (monthly_capital - fee) / price
            total_bnb += qty
            total_invested += monthly_capital
            buy_prices.append(price)

        if total_invested > 0:
            final_value = total_bnb * df["close"].iloc[-1]
            total_return = (final_value / total_invested - 1) * 100
            avg_price = total_invested / total_bnb

            results.append({
                "Window": f"{window} days",
                "Avg Price": f"${avg_price:.2f}",
                "Total BNB": f"{total_bnb:.2f}",
                "Final Value": f"${final_value:,.0f}",
                "Return %": f"{total_return:.1f}%",
            })

    print(tabulate(results, headers="keys", tablefmt="grid"))

    print("\n⚠️  LƯU Ý: Window strategy giả định bạn BIẾT TRƯỚC giá thấp nhất trong window.")
    print("Trong thực tế, bạn KHÔNG biết khi nào giá thấp nhất cho đến khi window kết thúc.")
    print("→ Cần dùng limit order hoặc trailing buy để xấp xỉ strategy này.")


if __name__ == "__main__":
    df = load_data()
    print(f"Data: {len(df)} days, {df.index.min().date()} -> {df.index.max().date()}")
    print(f"BNB price: ${df['close'].iloc[0]:.2f} -> ${df['close'].iloc[-1]:.2f}\n")

    # 1. Optimal buy day
    day_results = analyze_optimal_buy_day(df)

    # Summary table for key days
    key_days = [5, 7, 10, 14, 15, 20, 25, 1]
    rows = []
    for d in sorted(day_results.keys()):
        r = day_results[d]
        rows.append({
            "Buy Day": r["buy_day"],
            "Avg Price": f"${r['avg_buy_price']:.2f}",
            "Total BNB": f"{r['total_bnb']:.2f}",
            "Final Value": f"${r['final_value']:,.0f}",
            "Return %": f"{r['total_return_pct']:.1f}%",
        })
    print(tabulate(rows, headers="keys", tablefmt="grid"))

    best_day = max(day_results.values(), key=lambda x: x["total_return_pct"])
    worst_day = min(day_results.values(), key=lambda x: x["total_return_pct"])
    day5 = day_results[5]
    print(f"\nNgày 5 (baseline): Return {day5['total_return_pct']:.1f}%, avg price ${day5['avg_buy_price']:.2f}")
    print(f"Ngày TỐI ƯU (ngày {best_day['buy_day']}): Return {best_day['total_return_pct']:.1f}%, avg price ${best_day['avg_buy_price']:.2f}")
    print(f"Ngày TỆ NHẤT (ngày {worst_day['buy_day']}): Return {worst_day['total_return_pct']:.1f}%, avg price ${worst_day['avg_buy_price']:.2f}")
    print(f"Chênh lệch ngày tốt vs tệ: {best_day['total_return_pct'] - worst_day['total_return_pct']:.1f}%")
    print(f"Chênh lệch ngày tốt vs ngày 5: {best_day['total_return_pct'] - day5['total_return_pct']:.1f}%")

    # 2. Day of week effect
    analyze_day_of_week_effect(df)

    # 3. Intra-month pattern
    analyze_intramonth_pattern(df)

    # 4. Delay strategy
    analyze_delay_strategy(df)

    # 5. Window strategy
    analyze_window_strategy(df)
