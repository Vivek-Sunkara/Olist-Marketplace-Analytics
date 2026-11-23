-- How do late deliveries and long delivery times relate to review scores?
SELECT 'on-time vs late' AS view,
       CASE WHEN is_late = 1 THEN 'Late' ELSE 'On time' END AS grp,
       COUNT(*) AS orders, ROUND(AVG(review_score), 2) AS avg_review,
       ROUND(100.0 * AVG(CASE WHEN review_score <= 2 THEN 1.0 ELSE 0 END), 1) AS pct_1_2_star
FROM orders_enriched WHERE is_delivered = 1 AND review_score IS NOT NULL GROUP BY 2
UNION ALL
SELECT 'delivery days',
       CASE WHEN delivery_days <= 7 THEN '0-7' WHEN delivery_days <= 14 THEN '08-14'
            WHEN delivery_days <= 21 THEN '15-21' WHEN delivery_days <= 30 THEN '22-30' ELSE '30+' END,
       COUNT(*), ROUND(AVG(review_score), 2),
       ROUND(100.0 * AVG(CASE WHEN review_score <= 2 THEN 1.0 ELSE 0 END), 1)
FROM orders_enriched WHERE is_delivered = 1 AND review_score IS NOT NULL AND delivery_days > 0 GROUP BY 2
ORDER BY 1, 2;
