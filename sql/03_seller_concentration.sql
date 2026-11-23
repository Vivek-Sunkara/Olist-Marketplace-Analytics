-- Seller concentration: share of GMV by seller decile (NTILE window function)
WITH s AS (
  SELECT seller_id, SUM(price) AS gmv, COUNT(DISTINCT order_id) AS orders
  FROM items_enriched WHERE is_valid = 1 GROUP BY seller_id
), ranked AS (
  SELECT *, NTILE(10) OVER (ORDER BY gmv DESC) AS decile FROM s
)
SELECT decile, COUNT(*) AS sellers, ROUND(SUM(gmv), 0) AS gmv,
       ROUND(100.0 * SUM(gmv) / (SELECT SUM(gmv) FROM s), 1) AS share_of_gmv_pct,
       ROUND(AVG(orders), 1) AS avg_orders_per_seller
FROM ranked GROUP BY decile ORDER BY decile;
