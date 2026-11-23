"""
02_analyze.py
-------------
Runs the marketplace analysis on the prepared Olist tables, draws charts, exports Tableau-ready CSVs
and writes reports/insights_report.md (every number in the report is computed here).

Run:  python src/02_analyze.py     (after 01_prepare_data.py)
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PROC, CH, TB, REP = ROOT / "data" / "processed", ROOT / "outputs" / "charts", ROOT / "outputs" / "tableau", ROOT / "reports"
for p in (CH, TB, REP):
    p.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "font.size": 9})
C1, C2, C3, C4, GREY = "#2B6CB0", "#DD6B20", "#2F855A", "#C53030", "#718096"

orders = pd.read_csv(PROC / "orders_enriched.csv", parse_dates=["purchase_ts", "month", "delivered_ts", "estimated_ts"])
items = pd.read_csv(PROC / "items_enriched.csv", parse_dates=["purchase_ts", "month"])
ov = orders[orders["is_valid"] == 1].copy()          # valid orders (not cancelled/unavailable, has items)
iv = items[items["is_valid"] == 1].copy()
od = orders[orders["is_delivered"] == 1].copy()      # delivered orders (for delivery/review analysis)
od_r = od[od["review_score"].notna()]

BRL = lambda v: f"R${v/1e6:,.2f}M" if abs(v) >= 1e6 else (f"R${v/1e3:,.1f}K" if abs(v) >= 1e3 else f"R${v:,.0f}")
PCT = lambda v: f"{v:.1f}%"
R = {}   # numbers used by the report


# =====================================================================
# 1. MONTHLY KPIs
# =====================================================================
all_m = orders.groupby("month").agg(orders_all=("order_id", "count"), cancelled=("status", lambda s: s.isin(["canceled", "unavailable"]).sum()))
v_m = ov.groupby("month").agg(orders=("order_id", "count"), gmv=("gmv", "sum"), freight=("freight", "sum"),
                              items=("n_items", "sum"), customers=("customer_unique_id", "nunique"))
d_m = od.groupby("month").agg(avg_review=("review_score", "mean"), late_rate_pct=("is_late", lambda s: s.mean() * 100),
                              avg_delivery_days=("delivery_days", "mean"))
first = ov.groupby("customer_unique_id")["month"].min().value_counts().rename("new_customers")
kpi = all_m.join(v_m).join(d_m).join(first)
kpi["new_customers"] = kpi["new_customers"].fillna(0)
kpi["aov"] = kpi["gmv"] / kpi["orders"]
kpi["items_per_order"] = kpi["items"] / kpi["orders"]
kpi["freight_pct_of_gmv"] = kpi["freight"] / kpi["gmv"] * 100
kpi["cancel_rate_pct"] = kpi["cancelled"] / kpi["orders_all"] * 100
kpi["gmv_mom_pct"] = kpi["gmv"].pct_change() * 100
kpi["gmv_yoy_pct"] = kpi["gmv"].pct_change(12) * 100
kpi = kpi.reset_index()
kpi.to_csv(TB / "monthly_kpis.csv", index=False, float_format="%.2f")

R["gmv_total"] = ov["gmv"].sum()
R["orders_total"] = len(ov)
R["aov"] = ov["gmv"].sum() / len(ov)
R["cancel_rate"] = orders["status"].isin(["canceled", "unavailable"]).mean() * 100
R["freight_pct"] = ov["freight"].sum() / ov["gmv"].sum() * 100
ytd17 = kpi[(kpi["month"] >= "2017-01-01") & (kpi["month"] <= "2017-08-01")]["gmv"].sum()
ytd18 = kpi[(kpi["month"] >= "2018-01-01") & (kpi["month"] <= "2018-08-01")]["gmv"].sum()
R["gmv_ytd_growth"] = (ytd18 / ytd17 - 1) * 100
R["ytd17"], R["ytd18"] = ytd17, ytd18
nov = kpi[kpi["month"] == "2017-11-01"].iloc[0]
oct_ = kpi[kpi["month"] == "2017-10-01"].iloc[0]
R["nov17_gmv"], R["nov17_vs_oct_pct"] = nov["gmv"], (nov["gmv"] / oct_["gmv"] - 1) * 100
R["avg_review_all"] = od_r["review_score"].mean()

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.bar(kpi["month"], kpi["gmv"] / 1e6, width=22, color=C1, label="GMV (R$ M)")
ax.set_ylabel("GMV (R$ million)")
ax2 = ax.twinx(); ax2.grid(False)
ax2.plot(kpi["month"], kpi["orders"], color=C2, marker="o", ms=3, label="Orders")
ax2.set_ylabel("Orders")
ax.set_title("Monthly GMV and orders (valid orders, Jan 2017 - Aug 2018)")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
fig.tight_layout(); fig.savefig(CH / "01_monthly_gmv_orders.png"); plt.close(fig)


# =====================================================================
# 2. CATEGORY PERFORMANCE (+ fashion group)
# =====================================================================
FASHION = ["fashion_bags_accessories", "fashion_shoes", "fashion_male_clothing", "fashion_underwear_beach",
           "fashion_sport", "fashion_childrens_clothes", "luggage_accessories"]
co = iv.drop_duplicates(["category", "order_id"])                       # order-level view per category
cat = iv.groupby("category").agg(gmv=("price", "sum"), items=("order_item_id", "count"), avg_price=("price", "mean"),
                                 freight=("freight_value", "sum"), orders=("order_id", "nunique"))
cat["freight_pct_of_gmv"] = cat["freight"] / cat["gmv"] * 100
cat["avg_review"] = co.groupby("category")["review_score"].mean()
cat["late_rate_pct"] = co[co["is_delivered"] == 1].groupby("category")["is_late"].mean() * 100
g17 = iv[(iv["month"] >= "2017-01-01") & (iv["month"] <= "2017-08-01")].groupby("category")["price"].sum()
g18 = iv[(iv["month"] >= "2018-01-01") & (iv["month"] <= "2018-08-01")].groupby("category")["price"].sum()
cat["gmv_jan_aug_2017"], cat["gmv_jan_aug_2018"] = g17, g18
cat["growth_pct"] = np.where(cat["gmv_jan_aug_2017"] >= 20000, (cat["gmv_jan_aug_2018"] / cat["gmv_jan_aug_2017"] - 1) * 100, np.nan)
cat = cat.sort_values("gmv", ascending=False)
cat["share_pct"] = cat["gmv"] / cat["gmv"].sum() * 100
cat["cum_share_pct"] = cat["share_pct"].cumsum()
cat["abc_class"] = np.where(cat["cum_share_pct"] - cat["share_pct"] < 80, "A", np.where(cat["cum_share_pct"] - cat["share_pct"] < 95, "B", "C"))
cat["is_fashion_group"] = cat.index.isin(FASHION)
cat = cat.reset_index()
cat.to_csv(TB / "category_performance.csv", index=False, float_format="%.2f")

R["n_cat"] = len(cat)
R["n_A"] = int((cat["abc_class"] == "A").sum())
R["top3"] = cat.head(3)
R["top5_share"] = cat.head(5)["share_pct"].sum()
big = cat[cat["gmv_jan_aug_2017"] >= 20000]
R["fast"] = big.sort_values("growth_pct", ascending=False).head(3)
R["slow"] = big.sort_values("growth_pct").head(3)

top = cat.head(15).iloc[::-1]
fig, ax = plt.subplots(figsize=(8.5, 4.6))
cols = [C3 if r >= 4.1 else (C2 if r >= 3.9 else C4) for r in top["avg_review"]]
ax.barh(top["category"], top["gmv"] / 1e6, color=cols)
for i, (g, r) in enumerate(zip(top["gmv"] / 1e6, top["avg_review"])):
    ax.text(g, i, f"  {r:.2f}★", va="center", fontsize=7.5)
ax.set_xlabel("GMV (R$ million)"); ax.set_xlim(0, top["gmv"].max() / 1e6 * 1.12)
ax.set_title("Top 15 categories by GMV (label = avg review; green >=4.1, orange 3.9-4.1, red <3.9)")
fig.tight_layout(); fig.savefig(CH / "02_top_categories.png"); plt.close(fig)

# fashion group vs rest
fz = iv[iv["category"].isin(FASHION)]
fz_orders = fz["order_id"].nunique()
R["fashion_gmv"], R["fashion_share"] = fz["price"].sum(), fz["price"].sum() / iv["price"].sum() * 100
R["fashion_orders"], R["fashion_avg_price"], R["rest_avg_price"] = fz_orders, fz["price"].mean(), iv[~iv["category"].isin(FASHION)]["price"].mean()
fzo = fz.drop_duplicates("order_id")
R["fashion_review"] = fzo["review_score"].mean()
R["fashion_late"] = fzo[fzo["is_delivered"] == 1]["is_late"].mean() * 100
f17, f18 = fz[(fz["month"] >= "2017-01-01") & (fz["month"] <= "2017-08-01")]["price"].sum(), fz[(fz["month"] >= "2018-01-01") & (fz["month"] <= "2018-08-01")]["price"].sum()
R["fashion_growth"] = (f18 / f17 - 1) * 100
fash = cat[cat["is_fashion_group"]][["category", "gmv", "orders", "avg_price", "avg_review", "late_rate_pct", "growth_pct"]]
fash.to_csv(TB / "fashion_group_performance.csv", index=False, float_format="%.2f")
R["fashion_tbl"] = fash.sort_values("gmv", ascending=False)

fm = fz.groupby("month")["price"].sum()
fig, ax = plt.subplots(figsize=(8.5, 3.4))
ax.bar(fm.index, fm.values / 1e3, width=22, color=C1)
ax.set_ylabel("GMV (R$ thousand)"); ax.set_title("Fashion & accessories group: monthly GMV")
fig.tight_layout(); fig.savefig(CH / "03_fashion_group_gmv.png"); plt.close(fig)


# =====================================================================
# 3. SELLER ANALYSIS (partner management view)
# =====================================================================
so = iv.drop_duplicates(["seller_id", "order_id"])
sel = iv.groupby("seller_id").agg(gmv=("price", "sum"), items=("order_item_id", "count"), categories=("category", "nunique"))
sel["orders"] = so.groupby("seller_id").size()
sel["avg_review"] = so.groupby("seller_id")["review_score"].mean()
sel["late_rate_pct"] = so[so["is_delivered"] == 1].groupby("seller_id")["is_late"].mean() * 100
sel = sel.sort_values("gmv", ascending=False)
sel["rank"] = np.arange(1, len(sel) + 1)
sel["cum_share_pct"] = sel["gmv"].cumsum() / sel["gmv"].sum() * 100
n = len(sel)
R["n_sellers"] = n
R["top1_share"] = sel.head(max(int(n * 0.01), 1))["gmv"].sum() / sel["gmv"].sum() * 100
R["top10_share"] = sel.head(int(n * 0.10))["gmv"].sum() / sel["gmv"].sum() * 100
R["top20_share"] = sel.head(int(n * 0.20))["gmv"].sum() / sel["gmv"].sum() * 100
R["sellers_for_80"] = int((sel["cum_share_pct"] < 80).sum() + 1)
R["median_seller_orders"] = float(sel["orders"].median())
R["sellers_lt10_orders_pct"] = (sel["orders"] < 10).mean() * 100
avg_rev, avg_late = so["review_score"].mean(), so[so["is_delivered"] == 1]["is_late"].mean() * 100
sel["needs_attention"] = (sel["orders"] >= 30) & ((sel["avg_review"] < avg_rev - 0.5) | (sel["late_rate_pct"] > max(avg_late * 2, 15)))
sel.reset_index().to_csv(TB / "seller_scorecard.csv", index=False, float_format="%.2f")
watch = sel[(sel["needs_attention"]) & (sel["rank"] <= 200)]
R["watch_n"] = len(watch)
R["watch_gmv_share"] = watch["gmv"].sum() / sel["gmv"].sum() * 100
R["watch_top"] = watch.head(5).reset_index()[["seller_id", "gmv", "orders", "avg_review", "late_rate_pct"]]
R["attn_total"] = int(sel["needs_attention"].sum())

fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(sel["rank"] / n * 100, sel["cum_share_pct"], color=C1)
ax.axhline(80, color=GREY, ls="--", lw=0.8); ax.axvline(20, color=GREY, ls="--", lw=0.8)
ax.set_xlabel("% of sellers (ranked by GMV)"); ax.set_ylabel("Cumulative % of GMV")
ax.set_title(f"Seller concentration: top 10% of sellers = {R['top10_share']:.0f}% of GMV")
fig.tight_layout(); fig.savefig(CH / "04_seller_pareto.png"); plt.close(fig)


# =====================================================================
# 4. DELIVERY EXPERIENCE vs REVIEWS
# =====================================================================
grp = od_r.groupby("is_late").agg(orders=("order_id", "count"), avg_review=("review_score", "mean"),
                                  pct_1_2_star=("review_score", lambda s: (s <= 2).mean() * 100),
                                  pct_5_star=("review_score", lambda s: (s >= 5).mean() * 100), avg_days=("delivery_days", "mean"))
grp.index = ["On time", "Late"]
grp.to_csv(TB / "delivery_late_vs_ontime.csv", float_format="%.2f")
R["ontime"], R["late"] = grp.loc["On time"], grp.loc["Late"]
R["late_rate"] = od["is_late"].mean() * 100
R["late_gmv_share"] = od[od["is_late"] == 1]["gmv"].sum() / od["gmv"].sum() * 100

od_r = od_r.assign(days_bucket=pd.cut(od_r["delivery_days"], [0, 7, 14, 21, 30, 1000], labels=["0-7", "8-14", "15-21", "22-30", "30+"]))
db = od_r.groupby("days_bucket", observed=True).agg(orders=("order_id", "count"), avg_review=("review_score", "mean"),
                                                   pct_1_2_star=("review_score", lambda s: (s <= 2).mean() * 100)).reset_index()
db.to_csv(TB / "delivery_days_vs_review.csv", index=False, float_format="%.2f")
R["db"] = db

st = od.groupby("customer_state").agg(orders=("order_id", "count"), avg_delivery_days=("delivery_days", "mean"),
                                      late_rate_pct=("is_late", lambda s: s.mean() * 100), avg_review=("review_score", "mean")).reset_index()
st = st[st["orders"] >= 300].sort_values("avg_delivery_days", ascending=False)
st.to_csv(TB / "state_delivery_performance.csv", index=False, float_format="%.2f")
R["slow_states"] = st.head(3)
R["fast_state"] = st.tail(1)
sp = ov.groupby("customer_state")["gmv"].sum().sort_values(ascending=False)
pk = kpi.loc[kpi["late_rate_pct"].idxmax()]
R["late_peak_month"], R["late_peak"] = pk["month"].strftime("%b %Y"), pk["late_rate_pct"]
R["sp_share"] = sp.iloc[0] / sp.sum() * 100 if sp.index[0] == "SP" else np.nan

fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
axes[0].bar(grp.index, grp["avg_review"], color=[C3, C4]); axes[0].set_ylim(1, 5); axes[0].set_title("Average review: on time vs late")
for i, v in enumerate(grp["avg_review"]): axes[0].text(i, v + 0.05, f"{v:.2f}", ha="center")
axes[1].bar(db["days_bucket"].astype(str), db["avg_review"], color=C1); axes[1].set_ylim(1, 5)
axes[1].set_xlabel("Delivery time (days)"); axes[1].set_title("Average review by delivery time")
axes[2].plot(kpi["month"], kpi["late_rate_pct"], color=C4, marker="o", ms=3); axes[2].set_title("Late-delivery rate by month (%)")
axes[2].tick_params(axis="x", rotation=30)
fig.tight_layout(); fig.savefig(CH / "05_delivery_vs_reviews.png"); plt.close(fig)


# =====================================================================
# 5. PAYMENTS, INSTALLMENTS AND PRICE BANDS (demand levers)
# =====================================================================
ov["inst_bucket"] = pd.cut(ov["max_installments"], [0, 1, 3, 6, 10, 100], labels=["1 (upfront)", "2-3", "4-6", "7-10", "11+"])
ins = ov.groupby("inst_bucket", observed=True).agg(orders=("order_id", "count"), aov=("gmv", "mean"), avg_payment=("payment_value", "mean")).reset_index()
ins["share_of_orders_pct"] = ins["orders"] / ins["orders"].sum() * 100
ins.to_csv(TB / "installments_vs_aov.csv", index=False, float_format="%.2f")
R["ins"] = ins
ptype = ov.groupby("main_payment_type").agg(orders=("order_id", "count"), aov=("gmv", "mean")).reset_index()
ptype["share_pct"] = ptype["orders"] / ptype["orders"].sum() * 100
ptype = ptype.sort_values("orders", ascending=False)
ptype.to_csv(TB / "payment_type_mix.csv", index=False, float_format="%.2f")
R["ptype"] = ptype
R["multi_inst_share"] = (ov["max_installments"] > 1).mean() * 100
R["aov_1"] = ov[ov["max_installments"] <= 1]["gmv"].mean()
R["aov_multi"] = ov[ov["max_installments"] > 1]["gmv"].mean()

iv["price_band"] = pd.cut(iv["price"], [0, 50, 100, 200, 500, 1e9], labels=["<R$50", "R$50-100", "R$100-200", "R$200-500", "R$500+"])
iv["freight_ratio"] = iv["freight_value"] / iv["price"]
pb = iv.groupby("price_band", observed=True).agg(items=("order_item_id", "count"), gmv=("price", "sum"),
                                                  freight_pct=("freight_value", "sum")).reset_index()
pb["freight_pct"] = pb["freight_pct"] / pb["gmv"] * 100
pb["items_share_pct"] = pb["items"] / pb["items"].sum() * 100
pb["gmv_share_pct"] = pb["gmv"] / pb["gmv"].sum() * 100
pb["avg_review"] = iv.groupby("price_band", observed=True).apply(lambda g: g.drop_duplicates("order_id")["review_score"].mean(), include_groups=False).values
pb.to_csv(TB / "price_band_performance.csv", index=False, float_format="%.2f")
R["pb"] = pb
iv["freight_bucket"] = pd.cut(iv["freight_ratio"], [0, 0.1, 0.25, 0.5, 1, 1e9], labels=["<10%", "10-25%", "25-50%", "50-100%", ">100%"])
fb = iv.groupby("freight_bucket", observed=True).apply(
    lambda g: pd.Series({"items": len(g), "avg_review": g.drop_duplicates("order_id")["review_score"].mean()}), include_groups=False).reset_index()
fb.to_csv(TB / "freight_ratio_vs_review.csv", index=False, float_format="%.2f")
R["fb"] = fb

fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
axes[0].bar(ins["inst_bucket"].astype(str), ins["aov"], color=C1)
for i, v in enumerate(ins["aov"]): axes[0].text(i, v + 2, f"R${v:,.0f}", ha="center", fontsize=8)
axes[0].set_title("Average order value by number of instalments"); axes[0].set_ylabel("AOV (R$)")
axes[1].bar(fb["freight_bucket"].astype(str), fb["avg_review"], color=C2); axes[1].set_ylim(3, 5)
axes[1].set_title("Avg review by freight as % of item price"); axes[1].set_xlabel("Freight / price")
fig.tight_layout(); fig.savefig(CH / "06_installments_and_freight.png"); plt.close(fig)


# =====================================================================
# 6. CUSTOMERS: REPEAT RATE, COHORTS, RFM
# =====================================================================
cu = ov.groupby("customer_unique_id").agg(first=("purchase_ts", "min"), last=("purchase_ts", "max"),
                                          frequency=("order_id", "count"), monetary=("gmv", "sum"))
R["n_customers"] = len(cu)
R["repeat_rate"] = (cu["frequency"] > 1).mean() * 100
R["repeat_rev_share"] = cu[cu["frequency"] > 1]["monetary"].sum() / cu["monetary"].sum() * 100
gaps = ov.sort_values("purchase_ts").groupby("customer_unique_id")["purchase_ts"].apply(lambda s: s.diff().dt.days.dropna())
R["median_gap_days"] = float(gaps.median()) if len(gaps) else np.nan
R["repeat_within_30"] = float((gaps <= 30).mean() * 100) if len(gaps) else np.nan

act = ov[["customer_unique_id", "month"]].drop_duplicates()
cm = cu["first"].dt.to_period("M").dt.to_timestamp()
act["cohort"] = act["customer_unique_id"].map(cm)
act["k"] = (act["month"].dt.year - act["cohort"].dt.year) * 12 + act["month"].dt.month - act["cohort"].dt.month
sizes = cm.value_counts()
ret = act[act["k"].between(0, 6)].groupby(["cohort", "k"])["customer_unique_id"].nunique().unstack(fill_value=0)
ret_pct = ret.div(sizes.reindex(ret.index), axis=0) * 100
ret_pct = ret_pct[ret_pct.index <= pd.Timestamp("2018-02-01")]          # only cohorts with 6 full months observed
ret_pct.reset_index().to_csv(TB / "cohort_retention.csv", index=False, float_format="%.3f")
R["ret_m1"], R["ret_m3"], R["ret_m6"] = ret_pct[1].mean(), ret_pct[3].mean(), ret_pct[6].mean()

fig, ax = plt.subplots(figsize=(7.5, 4.4))
im = ax.imshow(ret_pct.iloc[:, 1:].values, cmap="Blues", aspect="auto")
ax.set_xticks(range(6), range(1, 7)); ax.set_yticks(range(len(ret_pct)), [d.strftime("%Y-%m") for d in ret_pct.index]); ax.grid(False)
for i in range(ret_pct.shape[0]):
    for j in range(6):
        ax.text(j, i, f"{ret_pct.iloc[i, j + 1]:.2f}", ha="center", va="center", fontsize=6.5)
ax.set_xlabel("Months since first purchase"); ax.set_ylabel("First-purchase month")
ax.set_title("Cohort retention (% of cohort who buy again in month k)")
fig.colorbar(im, ax=ax, shrink=0.8); fig.tight_layout(); fig.savefig(CH / "07_cohort_retention.png"); plt.close(fig)

snap = ov["purchase_ts"].max().normalize() + pd.Timedelta(days=1)
cu["recency_days"] = (snap - cu["last"]).dt.days
cu["R"] = pd.qcut(cu["recency_days"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
cu["M"] = pd.qcut(cu["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

def seg(r):
    if r.frequency >= 2: return "Repeat buyers (2+ orders)"
    if r.M >= 5: return "High-value one-timers (top 20% by spend)"
    if r.R >= 4: return "Recent one-timers"
    if r.R <= 2: return "Lapsed one-timers"
    return "Mid one-timers"
cu["segment"] = cu.apply(seg, axis=1)
rs = cu.groupby("segment").agg(customers=("frequency", "size"), revenue=("monetary", "sum"), avg_order_value=("monetary", "mean")).reset_index()
rs["customer_share_pct"] = rs["customers"] / rs["customers"].sum() * 100
rs["revenue_share_pct"] = rs["revenue"] / rs["revenue"].sum() * 100
rs = rs.sort_values("revenue", ascending=False)
rs.to_csv(TB / "customer_segments.csv", index=False, float_format="%.2f")
R["rfm"] = rs

fig, ax = plt.subplots(figsize=(8, 3.6))
w = 0.38; xs = np.arange(len(rs))
ax.bar(xs - w / 2, rs["customer_share_pct"], w, color=GREY, label="% of customers")
ax.bar(xs + w / 2, rs["revenue_share_pct"], w, color=C1, label="% of GMV")
ax.set_xticks(xs, rs["segment"], rotation=18, ha="right"); ax.legend(frameon=False)
ax.set_title("Customer segments: share of customers vs. share of GMV")
fig.tight_layout(); fig.savefig(CH / "08_customer_segments.png"); plt.close(fig)


# =====================================================================
# 7. SHORT-TERM FORECAST (only 20 months of history: trend/level models, validated on a holdout)
# =====================================================================
ts = kpi.set_index("month")["gmv"]
H = 3
def fit_predict(y, kind, horizon):
    if kind == "level":
        base = y.iloc[-3:].mean()
        pred = np.repeat(base, horizon)
        sd = float(np.std(y.iloc[-6:] - base, ddof=1))
    else:
        yy = y.iloc[-8:]; t = np.arange(len(yy))
        b1, b0 = np.polyfit(t, yy.values, 1)
        pred = b0 + b1 * np.arange(len(yy), len(yy) + horizon)
        sd = float(np.std(yy.values - (b0 + b1 * t), ddof=2))
    idx = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    return idx, np.asarray(pred, dtype=float), sd

train, test = ts.iloc[:-H], ts.iloc[-H:]
mape = {}
for k in ("level", "trend"):
    _, p, _ = fit_predict(train, k, H)
    mape[k] = float(np.mean(np.abs(p - test.values) / test.values) * 100)
best = min(mape, key=mape.get)
fidx, f_mid, f_sd = fit_predict(ts, best, H)
f_lo, f_hi = f_mid - 1.28 * f_sd, f_mid + 1.28 * f_sd
bf_uplift = ts["2017-11-01"] / ts["2017-08-01":"2017-10-01"].mean()
bf_scn = f_mid[:2].mean() * bf_uplift
fc = pd.DataFrame({"month": fidx, "forecast_gmv": f_mid, "lower_80": f_lo, "upper_80": f_hi})
fc["black_friday_scenario_gmv"] = [np.nan, np.nan, bf_scn]
out = pd.concat([pd.DataFrame({"month": ts.index, "actual_gmv": ts.values}), fc])
out.to_csv(TB / "gmv_forecast.csv", index=False, float_format="%.0f")
R["mape"], R["best_model"], R["fc"], R["bf_uplift"], R["bf_scn"] = mape, best, fc, bf_uplift, bf_scn

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(ts.index, ts.values / 1e6, color=C1, marker="o", ms=3, label="Actual")
ax.plot(fidx, f_mid / 1e6, color=C2, marker="o", ms=3, label=f"Forecast ({best} model)")
ax.fill_between(fidx, f_lo / 1e6, f_hi / 1e6, color=C2, alpha=0.2, label="~80% band")
ax.scatter([fidx[2]], [bf_scn / 1e6], color=C4, marker="D", zorder=5, label="Black Friday scenario (Nov)")
ax.axvspan(test.index[0], test.index[-1], color=GREY, alpha=0.12, label="Holdout period")
ax.set_ylabel("GMV (R$ million)"); ax.set_title("3-month GMV forecast (only 20 months of history, low confidence)")
ax.legend(frameon=False, loc="upper left", fontsize=7.5); fig.tight_layout(); fig.savefig(CH / "09_gmv_forecast.png"); plt.close(fig)


# =====================================================================
# 8. REPORT
# =====================================================================
dq = json.loads((ROOT / "outputs" / "data_quality_log.json").read_text())
T = lambda df, f: "\n".join(f(r) for r in df.itertuples())
late, ont = R["late"], R["ontime"]
report = f"""# Olist Marketplace Analytics: Insights Report

**Data:** Olist Brazilian E-Commerce Public Dataset (real orders from a Brazilian online marketplace, Kaggle).
**Window:** Jan 2017 - Aug 2018 ({R['orders_total']:,} valid orders, {R['n_customers']:,} customers, {R['n_sellers']:,} sellers, {R['n_cat']} categories). Currency: Brazilian real (R$).

> **Scope note:** Olist is a general marketplace, not a fashion retailer, and the data has no discount, traffic or
> advertising fields. The analysis therefore focuses on category performance, seller (partner) management, delivery
> experience, payment behaviour, customer retention and forecasting. A "fashion & accessories" group is analysed separately.

## 1. Headline
- GMV (item value of valid orders) was **{BRL(R['gmv_total'])}** across **{R['orders_total']:,}** orders; AOV **R${R['aov']:,.0f}**; freight adds **{R['freight_pct']:.1f}%** on top of item value.
- Jan-Aug 2018 GMV was **{R['gmv_ytd_growth']:+.1f}%** vs. Jan-Aug 2017 ({BRL(R['ytd18'])} vs. {BRL(R['ytd17'])}). Nov 2017 (Black Friday month) GMV was {BRL(R['nov17_gmv'])}, **{R['nov17_vs_oct_pct']:+.0f}%** vs. Oct 2017.
- {R['cancel_rate']:.1f}% of orders were cancelled or unavailable; average delivered-order review is **{R['avg_review_all']:.2f}/5**.

## 2. Categories
- **{R['n_A']} of {R['n_cat']}** categories make up 80% of GMV (class A); the top 5 categories hold **{R['top5_share']:.0f}%**.
- Top 3: """ + "; ".join(f"**{r.category}** ({BRL(r.gmv)}, {r.share_pct:.1f}%, review {r.avg_review:.2f})" for r in R["top3"].itertuples()) + f""".
- Fastest-growing large categories (Jan-Aug 2018 vs 2017, base of R$20K+): """ + ", ".join(f"{r.category} ({r.growth_pct:+.0f}%)" for r in R["fast"].itertuples()) + f""".
- Slowest-growing: """ + ", ".join(f"{r.category} ({r.growth_pct:+.0f}%)" for r in R["slow"].itertuples()) + f""".

### Fashion & accessories group (7 categories)
- GMV **{BRL(R['fashion_gmv'])}** ({R['fashion_share']:.1f}% of total), {R['fashion_orders']:,} orders, average item price R${R['fashion_avg_price']:,.0f} (vs. R${R['rest_avg_price']:,.0f} for other categories).
- Average review {R['fashion_review']:.2f}, late-delivery rate {R['fashion_late']:.1f}%, Jan-Aug GMV growth {R['fashion_growth']:+.0f}% year on year.

| Category | GMV | Orders | Avg price (R$) | Avg review | Late % | Growth % |
|---|---|---|---|---|---|---|
""" + T(R["fashion_tbl"], lambda r: f"| {r.category} | {BRL(r.gmv)} | {r.orders:,} | {r.avg_price:,.0f} | {r.avg_review:.2f} | {r.late_rate_pct:.1f} | {'n/a' if pd.isna(r.growth_pct) else format(r.growth_pct, '+.0f')} |") + f"""

## 3. Seller (partner) concentration and risk
- The top 10% of sellers generate **{R['top10_share']:.0f}%** of GMV and the top 20% generate **{R['top20_share']:.0f}%**; **{R['sellers_for_80']:,}** sellers ({R['sellers_for_80']/R['n_sellers']*100:.0f}%) make up 80%.
- {R['sellers_lt10_orders_pct']:.0f}% of sellers have fewer than 10 orders: a long tail that adds selection but little revenue.
- **Watch list:** among the top 200 sellers, **{R['watch_n']}** combine high volume with weak experience (review at least 0.5 below average, or late rate above 2x average). They hold **{R['watch_gmv_share']:.1f}%** of GMV. `outputs/tableau/seller_scorecard.csv` has the full list.

## 4. Delivery experience drives reviews
| | Orders | Avg review | 1-2 star % | 5 star % | Avg delivery days |
|---|---|---|---|---|---|
| On time | {int(ont.orders):,} | {ont.avg_review:.2f} | {ont.pct_1_2_star:.1f} | {ont.pct_5_star:.1f} | {ont.avg_days:.1f} |
| Late | {int(late.orders):,} | {late.avg_review:.2f} | {late.pct_1_2_star:.1f} | {late.pct_5_star:.1f} | {late.avg_days:.1f} |

- Late orders average **{late.avg_review:.2f}** vs **{ont.avg_review:.2f}** on time, and {late.pct_1_2_star:.0f}% of late orders get 1-2 stars vs. {ont.pct_1_2_star:.0f}%.
- **{R['late_rate']:.1f}%** of delivered orders arrive after the promised date; they carry {R['late_gmv_share']:.1f}% of delivered GMV.
- Slowest large states: """ + ", ".join(f"{r.customer_state} ({r.avg_delivery_days:.0f} days, {r.late_rate_pct:.0f}% late)" for r in R["slow_states"].itertuples()) + f"""; fastest: {R['fast_state'].iloc[0]['customer_state']} ({R['fast_state'].iloc[0]['avg_delivery_days']:.0f} days).
- Late-delivery rate peaked at **{R['late_peak']:.0f}%** in {R['late_peak_month']}; the peaks coincide with high-demand periods (Black Friday and the following months).
- This is an association from observational data. Late orders may differ in other ways (distance, category), but the gap is large, and average reviews also fall steadily as delivery time rises (see `delivery_days_vs_review.csv`).

## 5. Payments, instalments and price
- **{R['multi_inst_share']:.0f}%** of orders are paid in instalments. AOV is **R${R['aov_multi']:,.0f}** for instalment orders vs. **R${R['aov_1']:,.0f}** for single payments. Instalments are associated with larger baskets; it is plausible that financing enables bigger purchases, but this analysis does not prove it.
- Payment mix: """ + ", ".join(f"{r.main_payment_type} {r.share_pct:.0f}%" for r in R["ptype"].itertuples()) + f""".

| Price band | Items share % | GMV share % | Freight as % of price | Avg review |
|---|---|---|---|---|
""" + T(R["pb"], lambda r: f"| {r.price_band} | {r.items_share_pct:.1f} | {r.gmv_share_pct:.1f} | {r.freight_pct:.1f} | {r.avg_review:.2f} |") + f"""

- Freight is a large share of the price for cheap items; review scores by freight-to-price bucket: """ + ", ".join(f"{r.freight_bucket}: {r.avg_review:.2f}" for r in R["fb"].itertuples()) + f""".

## 6. Customers and retention
- Only **{R['repeat_rate']:.1f}%** of customers bought more than once in the window; repeat buyers account for {R['repeat_rev_share']:.1f}% of GMV.
- Share of a cohort that purchases again: **{R['ret_m1']:.2f}%** in month 1, {R['ret_m3']:.2f}% in month 3, {R['ret_m6']:.2f}% in month 6. Among customers who did return, the median gap between orders was {R['median_gap_days']:.0f} days.
- Segments: """ + "; ".join(f"{r.segment} {r.customer_share_pct:.0f}% of customers / {r.revenue_share_pct:.0f}% of GMV" for r in R["rfm"].itertuples()) + f""".

## 7. Forecast (next 3 months)
| Month | Forecast GMV | ~80% band |
|---|---|---|
""" + T(R["fc"], lambda r: f"| {r.month:%b %Y} | {BRL(r.forecast_gmv)} | {BRL(r.lower_80)} to {BRL(r.upper_80)} |") + f"""

- Two simple models were compared on a 3-month holdout: level (avg of last 3 months) MAPE **{R['mape']['level']:.1f}%**, linear trend MAPE **{R['mape']['trend']:.1f}%**. The better one ({R['best_model']}) is used.
- **Black Friday scenario for Nov 2018:** Nov 2017 ran {R['bf_uplift']:.2f}x the Aug-Oct 2017 average, which implies about **{BRL(R['bf_scn'])}** if the same uplift repeated. This rests on a single observation, so treat it as a scenario, not a forecast.
- Limits: only 20 months of history, so seasonality cannot be estimated; the bands are rough. The dataset ends in Aug 2018 (Sep-Oct 2018 have almost no orders because the extract stops there, not because demand fell).

## 8. Recommendations
1. **Fix delivery promises first.** Late orders are associated with reviews about {ont.avg_review - late.avg_review:.1f} points lower; target late-rate reductions in the slowest states and set realistic delivery estimates.
2. **Manage the seller portfolio.** Run quarterly scorecards on the top 10% of sellers (they drive {R['top10_share']:.0f}% of GMV); put the {R['watch_n']} watch-list sellers on improvement plans.
3. **Focus assortment on class-A categories** and test growth bets in the fastest-growing categories listed above; review the long tail of low-volume sellers and categories.
4. **Promote instalment offers on higher-priced items** and A/B test them, since instalment orders show larger baskets.
5. **Build retention.** With about {R['repeat_rate']:.0f}% repeat, even small gains in second-purchase rate are large; test post-delivery nudges within 30-60 days, especially for high-value one-time buyers.

## 9. Data quality log
```
{json.dumps(dq, indent=2)}
```
"""
(REP / "insights_report.md").write_text(report, encoding="utf-8")
print("Report written. best model:", best, mape)
