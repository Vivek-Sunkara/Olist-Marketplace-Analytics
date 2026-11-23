-- Instalments vs basket size, and payment-type mix
SELECT 'instalments' AS view,
       CASE WHEN max_installments <= 1 THEN '1 (upfront)' WHEN max_installments <= 3 THEN '2-3'
            WHEN max_installments <= 6 THEN '4-6' WHEN max_installments <= 10 THEN '7-10' ELSE '11+' END AS grp,
       COUNT(*) AS orders, ROUND(AVG(gmv), 1) AS aov,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM orders_enriched WHERE is_valid = 1 AND max_installments IS NOT NULL GROUP BY 2
UNION ALL
SELECT 'payment type', main_payment_type, COUNT(*), ROUND(AVG(gmv), 1),
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)
FROM orders_enriched WHERE is_valid = 1 AND main_payment_type IS NOT NULL GROUP BY 2
ORDER BY 1, 3 DESC;
