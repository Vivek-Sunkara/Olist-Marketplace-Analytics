-- Repeat purchase rate and monthly cohort retention (months 0-6)
WITH c AS (
  SELECT customer_unique_id, COUNT(*) AS orders, MIN(substr(purchase_ts, 1, 7)) AS cohort
  FROM orders_enriched WHERE is_valid = 1 GROUP BY customer_unique_id
), act AS (
  SELECT DISTINCT customer_unique_id, substr(purchase_ts, 1, 7) AS active_month
  FROM orders_enriched WHERE is_valid = 1
), sizes AS (
  SELECT cohort, COUNT(*) AS cohort_size FROM c GROUP BY cohort
), x AS (
  SELECT c.cohort,
         (CAST(substr(a.active_month, 1, 4) AS INT) - CAST(substr(c.cohort, 1, 4) AS INT)) * 12
         + CAST(substr(a.active_month, 6, 2) AS INT) - CAST(substr(c.cohort, 6, 2) AS INT) AS months_since,
         COUNT(DISTINCT a.customer_unique_id) AS active_customers
  FROM c JOIN act a USING (customer_unique_id) GROUP BY c.cohort, months_since
)
SELECT x.cohort, s.cohort_size, x.months_since, x.active_customers,
       ROUND(100.0 * x.active_customers / s.cohort_size, 2) AS retention_pct,
       ROUND((SELECT 100.0 * AVG(CASE WHEN orders > 1 THEN 1.0 ELSE 0 END) FROM c), 2) AS overall_repeat_rate_pct
FROM x JOIN sizes s USING (cohort)
WHERE x.months_since BETWEEN 0 AND 6 AND x.cohort <= '2018-02'
ORDER BY x.cohort, x.months_since;
