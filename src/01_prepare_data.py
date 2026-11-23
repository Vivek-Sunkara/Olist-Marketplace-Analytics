"""
01_prepare_data.py
------------------
Cleans and joins the Olist Brazilian E-Commerce public dataset (Kaggle) into two analysis tables:
    data/processed/orders_enriched.csv   one row per order
    data/processed/items_enriched.csv    one row per order item

Raw files must be in data/raw/ (download from Kaggle: "Brazilian E-Commerce Public Dataset by Olist").
Analysis window: 2017-01-01 to 2018-08-31 (months before/after contain only a handful of orders).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
WIN_START, WIN_END = pd.Timestamp("2017-01-01"), pd.Timestamp("2018-09-01")  # end exclusive
log = {}

orders = pd.read_csv(RAW / "olist_orders_dataset.csv",
                     parse_dates=["order_purchase_timestamp", "order_delivered_customer_date",
                                  "order_estimated_delivery_date"])
items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
products = pd.read_csv(RAW / "olist_products_dataset.csv")
trans = pd.read_csv(RAW / "product_category_name_translation.csv", encoding="utf-8-sig")
customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")

log["raw_orders"] = len(orders)
log["raw_order_items"] = len(items)
log["duplicate_order_ids"] = int(orders["order_id"].duplicated().sum())

# ---- category names: translate Portuguese -> English; fix 2 untranslated names; fill missing ----
cat_map = dict(zip(trans["product_category_name"], trans["product_category_name_english"]))
cat_map.update({"pc_gamer": "pc_gamer", "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_food_preparers"})
products["category"] = products["product_category_name"].map(cat_map)
log["products_missing_category_set_to_unknown"] = int(products["category"].isna().sum())
products["category"] = products["category"].fillna("unknown")

# ---- reviews: some orders have several reviews -> average per order ----
log["orders_with_multiple_reviews"] = int(reviews["order_id"].duplicated().sum())
rev = reviews.groupby("order_id")["review_score"].mean().rename("review_score")

# ---- payments: aggregate to one row per order ----
log["orders_with_multiple_payment_rows"] = int(payments["order_id"].duplicated().sum())
pay = payments.groupby("order_id").agg(payment_value=("payment_value", "sum"),
                                       max_installments=("payment_installments", "max"))
main_type = (payments.sort_values("payment_value", ascending=False)
             .drop_duplicates("order_id").set_index("order_id")["payment_type"].rename("main_payment_type"))

# ---- order-level money from items ----
agg = items.groupby("order_id").agg(gmv=("price", "sum"), freight=("freight_value", "sum"), n_items=("order_item_id", "count"))

o = (orders.rename(columns={"order_purchase_timestamp": "purchase_ts", "order_delivered_customer_date": "delivered_ts",
                            "order_estimated_delivery_date": "estimated_ts", "order_status": "status"})
     .merge(customers[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id", how="left")
     .merge(agg, on="order_id", how="left").merge(rev, on="order_id", how="left")
     .merge(pay, on="order_id", how="left").merge(main_type, on="order_id", how="left"))

log["orders_before_window_filter"] = len(o)
o = o[(o["purchase_ts"] >= WIN_START) & (o["purchase_ts"] < WIN_END)].copy()
log["orders_in_window_2017-01_to_2018-08"] = len(o)

o[["gmv", "freight", "n_items"]] = o[["gmv", "freight", "n_items"]].fillna(0)
log["window_orders_without_items"] = int((o["n_items"] == 0).sum())
o["is_valid"] = (~o["status"].isin(["canceled", "unavailable"]) & (o["n_items"] > 0)).astype(int)
o["is_delivered"] = ((o["status"] == "delivered") & o["delivered_ts"].notna()).astype(int)
log["delivered_status_but_no_delivery_date"] = int(((o["status"] == "delivered") & o["delivered_ts"].isna()).sum())
o["delivery_days"] = (o["delivered_ts"] - o["purchase_ts"]).dt.total_seconds() / 86400
o.loc[o["is_delivered"] == 0, "delivery_days"] = np.nan
o["is_late"] = ((o["delivered_ts"].dt.normalize() > o["estimated_ts"]) & (o["is_delivered"] == 1)).astype(int)
o["month"] = o["purchase_ts"].dt.to_period("M").dt.to_timestamp()
log["delivered_orders_missing_review"] = int(((o["is_delivered"] == 1) & o["review_score"].isna()).sum())

keep_o = ["order_id", "customer_unique_id", "customer_state", "status", "purchase_ts", "month", "delivered_ts", "estimated_ts",
          "is_valid", "is_delivered", "delivery_days", "is_late", "review_score", "payment_value", "max_installments",
          "main_payment_type", "gmv", "freight", "n_items"]
o = o[keep_o]

it = (items.merge(products[["product_id", "category"]], on="product_id", how="left")
      .merge(o[["order_id", "customer_unique_id", "customer_state", "status", "purchase_ts", "month", "is_valid",
                "is_delivered", "is_late", "delivery_days", "review_score", "max_installments"]], on="order_id", how="inner"))
it["category"] = it["category"].fillna("unknown")
log["items_in_window"] = len(it)
log["distinct_categories"] = int(it["category"].nunique())
log["distinct_sellers"] = int(it["seller_id"].nunique())
log["distinct_customers_unique"] = int(o["customer_unique_id"].nunique())

o.to_csv(PROC / "orders_enriched.csv", index=False)
it.drop(columns=["shipping_limit_date"]).to_csv(PROC / "items_enriched.csv", index=False)
(ROOT / "outputs" / "data_quality_log.json").write_text(json.dumps(log, indent=2))
print(json.dumps(log, indent=2))
