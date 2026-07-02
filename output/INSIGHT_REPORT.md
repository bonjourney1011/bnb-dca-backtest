# BNB Trading Strategy Backtest Report
## Data-Driven Insights from Real Binance Data (2020-2026)

**Date:** 2026-07-02
**Data:** 2,375 ngày BNB/USDT daily OHLCV từ Binance API
**Capital:** $500/tháng vào ngày 5 (tổng $39,000 trong 6.5 năm)
**Fee:** 0.1% per trade (Binance standard)

---

## 1. KẾT QUẢ TỔNG HỢP

| Strategy | Invested | Final Value | Return | CAGR | Sharpe | Max DD | Calmar |
|----------|----------|-------------|--------|------|--------|--------|--------|
| **Pure DCA** | $39,000 | **$231,118** | **492.6%** | **31.6%** | 1.14 | -69.4% | 0.45 |
| DCA + RSI | $39,000 | $228,298 | 485.4% | 31.3% | 1.14 | -69.4% | 0.45 |
| Hybrid 80/15/5 | $39,000 | $222,261 | 469.9% | 30.8% | 1.14 | -69.1% | 0.45 |
| Fear & Greed DCA | $39,000 | $206,496 | 429.5% | 29.3% | 1.14 | -69.0% | 0.42 |
| Value Averaging | $39,000 | $141,658 | 263.2% | 22.0% | 1.12 | -63.7% | 0.35 |
| Grid Trading | $39,000 | $39,943 | 2.4% | 0.4% | 1.19 | -11.1% | 0.03 |

---

## 2. INSIGHT CHÍNH TỪ DATA (KHÔNG PHẢI LÝ THUYẾT)

### Insight #1: Pure DCA THẮNG tuyệt đối — RSI/Hybrid/F&G KHÔNG cải thiện đáng kể

**Data chứng minh:** Pure DCA ($231,118) > DCA+RSI ($228,298) > Hybrid ($222,261) > F&G ($206,496)

- Các chiến lược "thông minh" thực tế **UNDERPERFORM** Pure DCA từ 1.2% đến 10.6%
- Lý do: Khi chờ RSI oversold hoặc F&G < 50, bạn **bỏ lỡ cơ hội mua ở giá thấp**
- RSI < 40 chỉ xuất hiện ~15% thời gian → phần tactical 15-20% capital bị trì hoãn
- **Kết luận:** Với BNB giai đoạn 2020-2026 (strong uptrend), time in market > timing the market

### Insight #2: Grid Trading THẢM HẠI cho accumulation — chỉ $39,943 từ $39,000

- Grid Trading có Sharpe cao nhất (1.19) và MaxDD thấp nhất (-11.1%) nhưng **gần như không sinh lời**
- Lý do: Grid sell tại +5% trong khi BNB tăng 4000%+ từ 2020 → bán quá sớm, quá nhiều
- **0.5449 BNB** cuối kỳ vs **410.2 BNB** của Pure DCA → Grid giữ lại <0.2% BNB
- **Kết luận:** Grid Trading KHÔNG phù hợp cho asset có strong long-term trend. Chỉ dùng cho sideways market.

### Insight #3: Max Drawdown -69% là UNAVOIDABLE cho DCA strategies

- Tất cả DCA-based strategies đều chịu MaxDD -69% đến -69.4%
- Drawdown xảy ra **cùng thời điểm** (May-Jun 2022, bear market crash)
- Recovery time: **634 ngày** (~1.7 năm) cho tất cả strategies
- **Kết luận:** Nếu không chịu được thấy portfolio giảm 70%, đừng DCA vào crypto. Không có chiến lược nào tránh được bear market.

### Insight #4: 2021 là OUTLIER cực lớn — skew toàn bộ data

- Pure DCA return 2021: **+1,409%** (BNB từ $37 → $600+)
- Nếu loại 2021, returns sẽ thấp hơn rất nhiều
- 2022: -49.3%, 2023: +34.7%, 2024: +132.5%, 2025: +25.7%, 2026 YTD: -34.1%
- **Kết luận:** CAGR 31.6% là unrealistic cho future. Realistic expectation: 15-25% CAGR

### Insight #5: Fee impact MINIMAL — chỉ $37-$76 trên $39,000 invested

- Pure DCA: $39 fees (78 trades)
- Grid Trading: $76 fees (443 trades) — nhiều trade hơn 5.7x
- Fee 0.1% Binance rất rẻ, KHÔNG phải yếu tố quyết định chiến lược

### Insight #6: Monthly win rate đồng đều ~60% cho tất cả DCA strategies

- 47/78 tháng positive cho Pure DCA
- Best month: +385% (Feb 2021), Worst month: -43% (May 2021)
- Cả 2 cực đoan đều ở 2021 → extreme volatility year
- Median monthly return ~3% → phần lớn tháng có return modest

---

## 3. YEARLY PERFORMANCE (thực tế)

| Strategy | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 YTD |
|----------|------|------|------|------|------|----------|
| Pure DCA | +1409% | -49.3% | +34.7% | +132.5% | +25.7% | -34.1% |
| DCA+RSI | +1400% | -49.2% | +34.8% | +132.5% | +25.7% | -34.0% |
| Hybrid | +1374% | -48.9% | +34.7% | +131.5% | +25.6% | -33.9% |
| F&G DCA | +1272% | -49.0% | +35.4% | +131.9% | +25.9% | -34.0% |
| Value Avg | +980% | -42.6% | +32.0% | +107.5% | +24.0% | -28.9% |
| Grid | +100% | +47.6% | +35.0% | +25.4% | +19.9% | +8.3% |

**Key observation:**
- Grid Trading là strategy DUY NHẤT không thua năm nào (kể cả 2022 bear market)
- Nhưng đánh đổi bằng việc bỏ lỡ gần như TOÀN BỘ upside

---

## 4. KHUYẾN NGHỊ DATA-DRIVEN

### Cho người MỚI hoặc RISK-AVERSE:
**→ Pure DCA. Không cần suy nghĩ.**

Lý do từ data:
- Outperform tất cả strategies phức tạp hơn
- 78 trades trong 6.5 năm = 1 trade/tháng (minimal effort)
- Fees thấp nhất nhóm ($39)
- Simple: mua $500 BNB vào ngày 5 hàng tháng, không bao giờ bán

### Cho người muốn OPTIMIZE nhẹ:
**→ Hybrid 80/15/5 (nếu chấp nhận underperform nhẹ so với Pure DCA)**

- Giữ 80% capital làm DCA cứng
- 15% tactical khi RSI dip
- 5% emergency reserve
- Underperform Pure DCA ~5% nhưng có psychological comfort khi "đã cố timing"

### Cho người muốn LOW VOLATILITY:
**→ Grid Trading — nhưng CHỈ NẾU chấp nhận gần như không lời**

- MaxDD chỉ -11.1% vs -69.4%
- Nhưng return gần 0% trong 6.5 năm
- Phù hợp nếu dùng crypto như savings account, không accumulate

### KHÔNG KHUYẾN NGHỊ:
- **Value Averaging:** Underperform Pure DCA 40%+, giữ $27,585 cash idle
- **Fear & Greed DCA:** Thêm complexity nhưng kết quả kém hơn Pure DCA 12%
- **DCA + RSI:** Gần bằng Pure DCA nhưng 2x trades, thêm complexity vô ích

---

## 5. RISK WARNINGS (từ data thực)

1. **Drawdown 69% là THỰC TẾ** — Portfolio $39k → $12k trong bear market 2022
2. **Recovery mất 634 ngày** — Gần 2 năm để break even
3. **2026 YTD đang lỗ -34%** — Thời điểm hiện tại KHÔNG phải đỉnh
4. **BNB price hiện tại $550** — Cách ATH $1307 (Nov 2024) khoảng -58%
5. **CAGR 31.6% KHÔNG BỀN VỮNG** — Bao gồm outlier 2021 (+1409%). Kỳ vọng realistic: 10-20%
6. **Crypto là HIGH RISK** — Volatility hàng năm 78.5%, gấp 5x S&P 500

---

## 6. PLAYBOOK HÀNG THÁNG (NẾU CHỌN PURE DCA)

```
Ngày 5 hàng tháng:
1. Mở Binance
2. Market buy $500 BNB/USDT
3. Ghi lại: ngày, giá, số BNB
4. KHÔNG nhìn portfolio đến tháng sau
(Crypto hoạt động 24/7, mua được cả thứ 7/CN, không cần chờ ngày làm việc)
```

### Circuit Breakers:
- Portfolio DD > 50%: Vẫn DCA bình thường (đây là lúc mua rẻ nhất)
- Portfolio DD > 70%: Review lại allocation nhưng KHÔNG panic sell
- Cần tiền gấp: DỪNG DCA, KHÔNG bán BNB đã mua

---

## 7. FILES & CHARTS

- `output/equity_curves.png` — Equity curves tất cả strategies
- `output/risk_return_scatter.png` — Risk-return scatter plot
- `output/monthly_returns_heatmap.png` — Monthly return heatmap
- `output/bnb_accumulation.png` — BNB accumulation over time
- `output/strategy_comparison_bars.png` — Bar chart comparison
- `output/strategy_comparison.csv` — Raw comparison data
- `output/*_daily.csv` — Daily portfolio data per strategy

---

---

## 8. PHÂN TÍCH NGÀY MUA TỐI ƯU (VND → USDT → BNB)

### Flow thực tế: Lương ngày 5 → Mua USDT → Mua BNB

Data phân tích: Giá BNB theo từng ngày trong tháng, so với giá trung bình tháng đó.

### 8.1 Ngày nào trong tháng giá BNB RẺ NHẤT?

| Ngày | So với giá TB tháng | Rẻ hơn TB bao nhiêu % tháng |
|------|---------------------|------------------------------|
| **Ngày 2** | **-1.529%** | 59% tháng rẻ hơn TB |
| **Ngày 5** | **-1.483%** | 54% tháng rẻ hơn TB |
| Ngày 1 | -1.374% | 57% |
| Ngày 4 | -1.287% | 53% |
| Ngày 3 | -1.285% | 59% |
| ... | ... | ... |
| Ngày 28 | **+1.142%** | Chỉ 41% tháng rẻ hơn TB (ĐẮT NHẤT!) |

**Insight:** Đầu tháng (ngày 1-5) giá BNB có xu hướng RẺ hơn giá TB tháng ~1.3-1.5%. Cuối tháng (ngày 24-28) giá ĐẮT hơn ~0.5-1.1%.

### 8.2 Ngày trong tuần nào tốt nhất?

| Thứ | Avg Return | Positive % |
|-----|-----------|------------|
| **Thu** | **-0.095%** | **47.6%** ← NGÀY MUA TỐT NHẤT (giá hay giảm) |
| Mon | +0.166% | 51.3% |
| Sun | +0.201% | 51.3% |
| Sat | +0.241% | 57.8% |
| Tue | +0.324% | 50.4% |
| Fri | +0.436% | 55.8% |
| **Wed** | **+0.487%** | **53.7%** ← NGÀY MUA ĐẮT NHẤT |

**Insight:** Thứ 5 (Thursday) là ngày duy nhất có avg return ÂM → giá hay giảm vào thứ 5 → cơ hội mua rẻ.

### 8.3 Có nên chờ thêm N ngày sau ngày 5?

| Delay | Mua ngày | Return | So với ngày 5 |
|-------|----------|--------|---------------|
| 0 ngày | ~5 | 492.6% | baseline |
| **7 ngày** | **~12** | **504.0%** | **+11.4%** ← TỐI ƯU |
| 6 ngày | ~11 | 484.4% | -8.2% |
| 11 ngày | ~16 | 493.1% | +0.5% |
| 23 ngày | ~28 | 467.5% | -25.1% ← TỆ NHẤT |

**NGHỊCH LÝ:** Ngày 5 nằm trong top "giá rẻ nhất tháng" (-1.483%), nhưng delay 7 ngày (mua ngày 12) lại cho kết quả tốt hơn +11.4%. Lý do: ngày 12 cũng có avg price thấp ($93.29 vs $95.08 ngày 5), và trong vài tháng critical, ngày 12 rơi đúng đáy ngắn hạn.

### 8.4 Nếu có thể chờ giá tốt nhất trong cửa sổ N ngày?

| Cửa sổ | Avg Price | Return | So với mua ngay |
|--------|-----------|--------|-----------------|
| Mua ngay ngày 5 | $95.08 | 492.6% | baseline |
| Chờ 3 ngày (5-8) | $92.51 | 509.1% | +16.5% |
| Chờ 5 ngày (5-10) | $91.62 | 515.0% | +22.4% |
| Chờ 7 ngày (5-12) | $85.61 | 558.2% | +65.6% |
| Chờ 14 ngày (5-19) | $85.00 | 562.9% | +70.3% |

⚠️ **CẢNH BÁO:** Đây là giả định biết trước giá thấp nhất (oracle). Thực tế KHÔNG thể biết. Nhưng gợi ý: **đặt limit order thấp hơn giá hiện tại 2-3%** trong 5 ngày sau ngày 5.

### 8.5 KHUYẾN NGHỊ THỰC HÀNH

```
Ngày 5: Nhận lương → Mua USDT ngay (VND/USDT ít biến động, mua ngày nào cũng được)

Mua BNB: 2 cách

Cách 1 (Đơn giản, 95% hiệu quả):
  → Mua BNB ngay ngày 5 bằng market order
  → Return kỳ vọng: 492.6%

Cách 2 (Tối ưu nhẹ, cần theo dõi):
  → Ngày 5: Đặt limit order mua BNB tại giá hiện tại -2%
  → Nếu khớp trong 5 ngày: tuyệt vời
  → Nếu KHÔNG khớp đến ngày 10: mua market order ngay (đừng chờ thêm!)
  → Return kỳ vọng: ~500-515% (tùy khớp lệnh)
```

---

## 9. HOLD FOREVER vs CÁC CHIẾN LƯỢC BÁN

### 9.1 So sánh tổng quát

| Strategy | Final Value | Return | vs Hold | Max DD | Realized Profit | BNB còn lại |
|----------|-------------|--------|---------|--------|-----------------|-------------|
| **Hold Forever** | **$231,118** | **493%** | **baseline** | -69.4% | $0 | 410.2 BNB |
| Take Profit +200% (sell 25%) | $165,178 | 324% | -28.5% | -56.6% | $119,708 | 37.3 BNB |
| Sell 25% mỗi 12 tháng | $174,306 | 347% | -24.6% | -60.5% | $98,748 | 96.5 BNB |
| Milestone Sell (2x/3x/5x) | $165,419 | 324% | -28.4% | -56.6% | $29,198 | 235.3 BNB |
| Trailing Stop -40% | $207,412 | 432% | -10.3% | -69.1% | -$354 | 367.4 BNB |
| Trailing Stop -30% | $151,283 | 288% | -34.5% | -72.7% | $133,869 | 234.7 BNB |
| Sell 25% mỗi 6 tháng | $138,604 | 255% | -40.0% | -60.2% | $93,685 | 26.1 BNB |
| Take Profit +100% (sell 30%) | $108,564 | 178% | -53.0% | -56.6% | $69,899 | 12.0 BNB |
| Take Profit +50% (sell 50%) | $63,569 | 63% | **-72.5%** | -34.1% | $25,660 | 7.1 BNB |

### 9.2 Insight từ data

**Insight #7: Hold Forever THẮNG MỌI chiến lược bán**

Không có chiến lược sell nào beat Hold Forever. Strategy gần nhất là Trailing Stop -40% (kém 10.3%).

**Insight #8: Bán càng nhiều & càng sớm = LOSS càng lớn**

- Take Profit +50%, sell 50%: **MẤT 72.5%** so với Hold → $63K vs $231K
- Take Profit +200%, sell 25%: Mất 28.5% → vẫn mất $66K
- Bán 25% mỗi 6 tháng: Mất 40% → cuối chỉ còn 26 BNB

Lý do: Mỗi lần bán, bạn giảm position size. Khi BNB tăng tiếp, bạn lời ít hơn trên phần đã bán.

**Insight #9: Sell strategies CHỈ CÓ LỢI cho 1 thứ: GIẢM DRAWDOWN**

| Strategy | Max DD | Đánh đổi |
|----------|--------|----------|
| Hold Forever | -69.4% | Chịu full drawdown |
| Take Profit +50% | **-34.1%** | Nhưng mất 72.5% upside |
| Take Profit +200% | -56.6% | Nhưng mất 28.5% upside |
| Milestone Sell | -56.6% | Nhưng mất 28.4% upside |

Trade-off rõ ràng: **giảm 1% drawdown = mất ~2% return.**

**Insight #10: Nếu PHẢI bán, Milestone Sell là ít tệ nhất**

- Bán 10% khi portfolio = 2x vốn, 10% ở 3x, 15% ở 5x, 15% ở 8x, 20% ở 10x
- Giữ lại 235 BNB (57% so với Hold) + $32,869 cash + $29,198 realized
- Drawdown giảm từ -69.4% → -56.6% (cải thiện có ý nghĩa)
- Return vẫn 324% (chấp nhận được)

### 9.3 Khi nào NÊN bán?

Từ data, câu trả lời là: **KHÔNG NÊN BÁN nếu mục tiêu là tối đa return.**

Nhưng nếu bạn CẦN bán vì lý do thực tế (cần tiền, giảm rủi ro):

```
Scenario A: Cần tiền gấp
  → Bán tối đa 25% holdings mỗi lần
  → Giữ lại ít nhất 50% position cho long-term

Scenario B: Muốn giảm stress khi bear market
  → Milestone Sell: bán dần khi portfolio đạt 2x, 3x, 5x vốn
  → Chấp nhận mất ~28% return nhưng giảm DD từ -69% → -57%

Scenario C: Crypto chiếm quá nhiều % tổng tài sản
  → Bán 25% mỗi 12 tháng để rebalance
  → Realized $98K profit + giữ 96 BNB

KHÔNG NÊN:
  → Take profit +50% sell 50%: Bán quá sớm, quá nhiều → mất gần hết upside
  → Bán mỗi 6 tháng: Quá aggressive, cuối chỉ còn 26 BNB
```

---

## 10. TÓM TẮT CUỐI CÙNG

### Chiến lược tối ưu cho bạn (DCA BNB từ lương ngày 5):

```
┌─────────────────────────────────────────────────────┐
│  NGÀY 5: Nhận lương                                │
│  → Mua USDT ngay (VND→USDT không cần timing)       │
│                                                     │
│  CÁCH MUA BNB:                                      │
│  Option A: Market buy ngay ngày 5 (đơn giản nhất)   │
│  Option B: Limit order -2% trong 5 ngày             │
│            Không khớp → market buy ngày 10           │
│                                                     │
│  SAU KHI MUA:                                       │
│  → HOLD. KHÔNG BÁN.                                 │
│  → Mọi chiến lược bán đều kém hơn hold 10-72%      │
│                                                     │
│  NẾU BUỘC PHẢI BÁN:                                │
│  → Milestone Sell (bán dần khi 2x/3x/5x)           │
│  → Tối đa 25% mỗi lần                              │
│                                                     │
│  CHUẨN BỊ TINH THẦN:                               │
│  → Drawdown -69%, recovery 2 năm là BÌNH THƯỜNG    │
│  → ĐỪNG panic sell khi bear market                  │
└─────────────────────────────────────────────────────┘
```

**1 dòng: Mua BNB ngay ngày 5 bằng market order, hold forever. $39K → $231K (+493%) trong 6.5 năm. Không bán, không timing, không overthink.**
