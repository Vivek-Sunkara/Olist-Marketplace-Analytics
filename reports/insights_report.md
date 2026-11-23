# Olist Marketplace Analytics: Insights Report

**Data:** Olist Brazilian E-Commerce Public Dataset (real orders from a Brazilian online marketplace, Kaggle).
**Window:** Jan 2017 - Aug 2018 (97,905 valid orders, 94,703 customers, 3,029 sellers, 74 categories). Currency: Brazilian real (R$).

> **Scope note:** Olist is a general marketplace, not a fashion retailer, and the data has no discount, traffic or
> advertising fields. The analysis therefore focuses on category performance, seller (partner) management, delivery
> experience, payment behaviour, customer retention and forecasting. A "fashion & accessories" group is analysed separately.

## 1. Headline
- GMV (item value of valid orders) was **R$13.45M** across **97,905** orders; AOV **R$137**; freight adds **16.6%** on top of item value.
- Jan-Aug 2018 GMV was **+138.3%** vs. Jan-Aug 2017 (R$7.34M vs. R$3.08M). Nov 2017 (Black Friday month) GMV was R$1.00M, **+52%** vs. Oct 2017.
- 1.2% of orders were cancelled or unavailable; average delivered-order review is **4.16/5**.

## 2. Categories
- **18 of 74** categories make up 80% of GMV (class A); the top 5 categories hold **40%**.
- Top 3: **health_beauty** (R$1.25M, 9.3%, review 4.19); **watches_gifts** (R$1.19M, 8.9%, review 4.07); **bed_bath_table** (R$1.04M, 7.7%, review 3.97).
- Fastest-growing large categories (Jan-Aug 2018 vs 2017, base of R$20K+): baby (+264%), stationery (+263%), watches_gifts (+243%).
- Slowest-growing: home_confort (-4%), cool_stuff (+9%), luggage_accessories (+25%).

### Fashion & accessories group (7 categories)
- GMV **R$337.6K** (2.5% of total), 3,380 orders, average item price R$92 (vs. R$121 for other categories).
- Average review 4.22, late-delivery rate 5.2%, Jan-Aug GMV growth +38% year on year.

| Category | GMV | Orders | Avg price (R$) | Avg review | Late % | Growth % |
|---|---|---|---|---|---|---|
| fashion_bags_accessories | R$151.2K | 1,850 | 75 | 4.20 | 5.6 | +84 |
| luggage_accessories | R$140.1K | 1,030 | 129 | 4.34 | 4.3 | +25 |
| fashion_shoes | R$23.3K | 237 | 90 | 4.24 | 4.7 | n/a |
| fashion_male_clothing | R$10.7K | 110 | 82 | 3.75 | 4.8 | n/a |
| fashion_underwear_beach | R$9.5K | 121 | 73 | 3.93 | 9.4 | n/a |
| fashion_sport | R$2.1K | 27 | 71 | 4.26 | 3.8 | n/a |
| fashion_childrens_clothes | R$570 | 8 | 71 | 4.50 | 0.0 | n/a |

## 3. Seller (partner) concentration and risk
- The top 10% of sellers generate **67%** of GMV and the top 20% generate **82%**; **537** sellers (18%) make up 80%.
- 58% of sellers have fewer than 10 orders: a long tail that adds selection but little revenue.
- **Watch list:** among the top 200 sellers, **12** combine high volume with weak experience (review at least 0.5 below average, or late rate above 2x average). They hold **3.4%** of GMV. `outputs/tableau/seller_scorecard.csv` has the full list.

## 4. Delivery experience drives reviews
| | Orders | Avg review | 1-2 star % | 5 star % | Avg delivery days |
|---|---|---|---|---|---|
| On time | 89,182 | 4.29 | 9.2 | 62.2 | 11.0 |
| Late | 6,378 | 2.27 | 62.4 | 16.5 | 33.8 |

- Late orders average **2.27** vs **4.29** on time, and 62% of late orders get 1-2 stars vs. 9%.
- **6.8%** of delivered orders arrive after the promised date; they carry 7.5% of delivered GMV.
- Slowest large states: AL (25 days, 21% late), PA (24 days, 11% late), MA (22 days, 18% late); fastest: SP (9 days).
- Late-delivery rate peaked at **19%** in Mar 2018; the peaks coincide with high-demand periods (Black Friday and the following months).
- This is an association from observational data. Late orders may differ in other ways (distance, category), but the gap is large, and average reviews also fall steadily as delivery time rises (see `delivery_days_vs_review.csv`).

## 5. Payments, instalments and price
- **51%** of orders are paid in instalments. AOV is **R$172** for instalment orders vs. **R$100** for single payments. Instalments are associated with larger baskets; it is plausible that financing enables bigger purchases, but this analysis does not prove it.
- Payment mix: credit_card 75%, boleto 20%, voucher 3%, debit_card 2%.

| Price band | Items share % | GMV share % | Freight as % of price | Avg review |
|---|---|---|---|---|
| <R$50 | 34.9 | 9.1 | 47.0 | 4.12 |
| R$50-100 | 29.3 | 18.3 | 23.8 | 4.09 |
| R$100-200 | 23.9 | 28.6 | 16.1 | 4.12 |
| R$200-500 | 9.0 | 22.2 | 10.1 | 4.08 |
| R$500+ | 2.8 | 21.8 | 5.1 | 4.05 |

- Freight is a large share of the price for cheap items; review scores by freight-to-price bucket: <10%: 4.11, 10-25%: 4.12, 25-50%: 4.09, 50-100%: 4.06, >100%: 3.95.

## 6. Customers and retention
- Only **3.0%** of customers bought more than once in the window; repeat buyers account for 5.6% of GMV.
- Share of a cohort that purchases again: **0.48%** in month 1, 0.26% in month 3, 0.26% in month 6. Among customers who did return, the median gap between orders was 28 days.
- Segments: High-value one-timers (top 20% by spend) 18% of customers / 52% of GMV; Recent one-timers 31% of customers / 17% of GMV; Lapsed one-timers 31% of customers / 17% of GMV; Mid one-timers 16% of customers / 9% of GMV; Repeat buyers (2+ orders) 3% of customers / 6% of GMV.

## 7. Forecast (next 3 months)
| Month | Forecast GMV | ~80% band |
|---|---|---|
| Sep 2018 | R$863.4K | R$774.2K to R$952.5K |
| Oct 2018 | R$863.4K | R$774.2K to R$952.5K |
| Nov 2018 | R$863.4K | R$774.2K to R$952.5K |

- Two simple models were compared on a 3-month holdout: level (avg of last 3 months) MAPE **14.6%**, linear trend MAPE **25.6%**. The better one (level) is used.
- **Black Friday scenario for Nov 2018:** Nov 2017 ran 1.63x the Aug-Oct 2017 average, which implies about **R$1.41M** if the same uplift repeated. This rests on a single observation, so treat it as a scenario, not a forecast.
- Limits: only 20 months of history, so seasonality cannot be estimated; the bands are rough. The dataset ends in Aug 2018 (Sep-Oct 2018 have almost no orders because the extract stops there, not because demand fell).

## 8. Recommendations
1. **Fix delivery promises first.** Late orders are associated with reviews about 2.0 points lower; target late-rate reductions in the slowest states and set realistic delivery estimates.
2. **Manage the seller portfolio.** Run quarterly scorecards on the top 10% of sellers (they drive 67% of GMV); put the 12 watch-list sellers on improvement plans.
3. **Focus assortment on class-A categories** and test growth bets in the fastest-growing categories listed above; review the long tail of low-volume sellers and categories.
4. **Promote instalment offers on higher-priced items** and A/B test them, since instalment orders show larger baskets.
5. **Build retention.** With about 3% repeat, even small gains in second-purchase rate are large; test post-delivery nudges within 30-60 days, especially for high-value one-time buyers.

## 9. Data quality log
```
{
  "raw_orders": 99441,
  "raw_order_items": 112650,
  "duplicate_order_ids": 0,
  "products_missing_category_set_to_unknown": 610,
  "orders_with_multiple_reviews": 551,
  "orders_with_multiple_payment_rows": 4446,
  "orders_before_window_filter": 99441,
  "orders_in_window_2017-01_to_2018-08": 99092,
  "window_orders_without_items": 739,
  "delivered_status_but_no_delivery_date": 8,
  "delivered_orders_missing_review": 643,
  "items_in_window": 112279,
  "distinct_categories": 74,
  "distinct_sellers": 3068,
  "distinct_customers_unique": 95774
}
```
