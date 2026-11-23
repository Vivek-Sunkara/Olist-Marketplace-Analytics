-- Category scorecard with share of GMV, cumulative share (ABC / Pareto) and rank
WITH c AS (
  SELECT category, COUNT(DISTINCT order_id) AS orders, SUM(price) AS gmv, AVG(price) AS avg_price,
         SUM(freight_value) / SUM(price) AS freight_ratio
  FROM items_enriched WHERE is_valid = 1 GROUP BY category
), r AS (
  SELECT category, AVG(review_score) AS avg_review
  FROM (SELECT DISTINCT category, order_id, review_score FROM items_enriched WHERE is_valid = 1)
  GROUP BY category
)
SELECT RANK() OVER (ORDER BY c.gmv DESC) AS rnk, c.category, c.orders, ROUND(c.gmv, 0) AS gmv,
       ROUND(100.0 * c.gmv / SUM(c.gmv) OVER (), 1) AS share_pct,
       ROUND(100.0 * SUM(c.gmv) OVER (ORDER BY c.gmv DESC ROWS UNBOUNDED PRECEDING) / SUM(c.gmv) OVER (), 1) AS cum_share_pct,
       ROUND(c.avg_price, 0) AS avg_price, ROUND(100 * c.freight_ratio, 1) AS freight_pct_of_gmv,
       ROUND(r.avg_review, 2) AS avg_review
FROM c JOIN r USING (category)
ORDER BY c.gmv DESC;
