-- Monthly KPIs on valid orders (not cancelled/unavailable): GMV, orders, AOV, freight share,
-- cancel rate, on-time rate, reviews, and year-over-year GMV growth
WITH all_o AS (
  SELECT substr(purchase_ts, 1, 7) AS month, COUNT(*) AS orders_all,
         SUM(CASE WHEN status IN ('canceled', 'unavailable') THEN 1 ELSE 0 END) AS cancelled
  FROM orders_enriched GROUP BY 1
), v AS (
  SELECT substr(purchase_ts, 1, 7) AS month, COUNT(*) AS orders, SUM(gmv) AS gmv, SUM(freight) AS freight,
         COUNT(DISTINCT customer_unique_id) AS customers
  FROM orders_enriched WHERE is_valid = 1 GROUP BY 1
), d AS (
  SELECT substr(purchase_ts, 1, 7) AS month, AVG(review_score) AS avg_review,
         100.0 * AVG(1 - is_late) AS on_time_pct, AVG(delivery_days) AS avg_delivery_days
  FROM orders_enriched WHERE is_delivered = 1 GROUP BY 1
)
SELECT v.month, v.orders, ROUND(v.gmv, 0) AS gmv, ROUND(v.gmv / v.orders, 1) AS aov,
       ROUND(100.0 * v.freight / v.gmv, 1) AS freight_pct_of_gmv,
       ROUND(100.0 * a.cancelled / a.orders_all, 2) AS cancel_rate_pct,
       ROUND(d.on_time_pct, 1) AS on_time_pct, ROUND(d.avg_review, 2) AS avg_review,
       ROUND(100.0 * (v.gmv - LAG(v.gmv, 12) OVER (ORDER BY v.month)) / LAG(v.gmv, 12) OVER (ORDER BY v.month), 1) AS gmv_yoy_pct
FROM v JOIN all_o a USING (month) JOIN d USING (month)
ORDER BY v.month;
