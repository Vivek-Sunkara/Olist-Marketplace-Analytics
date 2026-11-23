# Tableau dashboard guide (Tableau Public is free)

Connect to the CSV files in `outputs/tableau/`. They are already aggregated, so no joins are needed.

## Dashboard 1: Business overview  (monthly_kpis.csv, category_performance.csv)
1. KPI tiles: SUM(gmv), AVG(aov), AVG(cancel_rate_pct), AVG(avg_review).
2. GMV trend: month (continuous) vs gmv (bars) with orders as a line on a dual axis.
3. Top 15 categories: bar of gmv sorted descending, colour by avg_review (diverging at 4.1).
4. Filter action: clicking a category filters the trend (use `is_fashion_group` as a filter to isolate fashion).

## Dashboard 2: Sellers and partners  (seller_scorecard.csv)
1. Pareto: rank vs cum_share_pct.
2. Scatter: gmv (log axis) vs avg_review, colour = late_rate_pct, filter orders >= 30, highlight needs_attention = TRUE.
3. Table of watch-list sellers.

## Dashboard 3: Delivery experience  (delivery_late_vs_ontime.csv, delivery_days_vs_review.csv, state_delivery_performance.csv, monthly_kpis.csv)
1. Bar: average review, on time vs late.
2. Bar: average review by delivery-time bucket.
3. Line: late_rate_pct by month.
4. Map or bar by state: avg_delivery_days and late_rate_pct.

## Dashboard 4: Customers and demand levers  (cohort_retention.csv, customer_segments.csv, installments_vs_aov.csv, price_band_performance.csv)
1. Cohort heat map (pivot the month columns 1-6).
2. Segment bars: customer_share_pct vs revenue_share_pct.
3. Instalments vs AOV; price-band GMV share.

## Dashboard 5: Forecast  (gmv_forecast.csv)
Actual vs forecast with the lower/upper band, plus the Black Friday scenario point (label it as a scenario).

## Tips
- Put the insight in each sheet title ("Late orders average 2.3 stars vs 4.3 on time").
- One colour per metric across sheets.
- Publish to Tableau Public and add the link to your resume.
