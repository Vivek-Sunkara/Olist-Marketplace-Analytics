# Data dictionary

## Source
Olist Brazilian E-Commerce Public Dataset (Kaggle: https://www.kaggle.com/olistbr/brazilian-ecommerce).
Real, anonymised orders from a Brazilian online marketplace, 2016-2018. Check the dataset's licence on its
Kaggle page before reusing or republishing the data. This repository does not include the raw files.

## Raw files used
| File | Used for |
|---|---|
| olist_orders_dataset.csv | Order status and timestamps |
| olist_order_items_dataset.csv | Items, price, freight, seller |
| olist_products_dataset.csv + product_category_name_translation.csv | Category (translated to English) |
| olist_customers_dataset.csv | customer_unique_id (a real person; customer_id is per order) and state |
| olist_order_payments_dataset.csv | Payment type and instalments |
| olist_order_reviews_dataset.csv | Review score (1-5) |

## Prepared tables (data/processed/)
**orders_enriched.csv** (one row per order): order_id, customer_unique_id, customer_state, status, purchase_ts, month,
delivered_ts, estimated_ts, is_valid, is_delivered, delivery_days, is_late, review_score, payment_value,
max_installments, main_payment_type, gmv, freight, n_items.

**items_enriched.csv** (one row per order item): order_id, order_item_id, product_id, seller_id, price, freight_value,
category, plus the order fields above.

## Definitions
- **Analysis window:** 2017-01-01 to 2018-08-31 (other months have very few orders).
- **Valid order:** status not canceled/unavailable and at least one item.
- **GMV:** sum of item prices of valid orders (excludes freight). **AOV** = GMV / valid orders.
- **Delivered order:** status = delivered with a delivery date. **Late:** delivered after the estimated date.
- **Review score:** average if an order has several reviews.
- **Fashion & accessories group:** fashion_bags_accessories, fashion_shoes, fashion_male_clothing, fashion_underwear_beach,
  fashion_sport, fashion_childrens_clothes, luggage_accessories.
- **Repeat customer:** a customer_unique_id with 2+ valid orders in the window.
- **Cohort retention:** % of a first-purchase-month cohort that places an order k months later.
- **Class A categories:** the categories that together make up the first 80% of GMV.
