import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

df = pd.read_csv("data_clean/transactions_clean.csv", parse_dates=["date"])
df = df[df["is_duplicate"] == False].copy()

# Une commande = une session (dédupliquée)
sessions = df.drop_duplicates(subset="session_id")[["session_id", "client_id", "date"]].copy()

# --- Première commande par client ---
first_order = sessions.groupby("client_id")["date"].min().rename("first_date").reset_index()

# --- Graphique 1 : Nouveaux clients par mois ---
first_order["month"] = first_order["first_date"].dt.to_period("M")
new_per_month = first_order.groupby("month").size().reset_index(name="new_clients")
new_per_month["month_dt"] = new_per_month["month"].dt.to_timestamp()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax1 = axes[0]
ax1.bar(
    new_per_month["month_dt"],
    new_per_month["new_clients"],
    width=20,
    color="#1E8A44",
    edgecolor="white",
    linewidth=0.5,
)
ax1.set_title("Nouveaux clients par mois", fontsize=13, fontweight="bold", pad=12)
ax1.set_xlabel("Mois", fontsize=11)
ax1.set_ylabel("Nombre de nouveaux clients", fontsize=11)
ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
ax1.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=3))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax1.grid(axis="y", alpha=0.3, linestyle="--")
ax1.spines[["top", "right"]].set_visible(False)

# --- Graphique 2 : Nb de commandes dans les 30j après la 1ère ---
sessions_merged = sessions.merge(first_order, on="client_id")
sessions_merged["days_since_first"] = (sessions_merged["date"] - sessions_merged["first_date"]).dt.days
sessions_30d = sessions_merged[sessions_merged["days_since_first"] <= 30]

orders_30d = sessions_30d.groupby("client_id")["session_id"].nunique().reset_index(name="nb_orders")
all_new = first_order[["client_id"]].copy()
orders_30d = all_new.merge(orders_30d, on="client_id", how="left")
orders_30d["nb_orders"] = orders_30d["nb_orders"].fillna(1).astype(int)

dist = orders_30d["nb_orders"].value_counts().sort_index()
dist = dist[dist.index <= 10]

ax2 = axes[1]
ax2.bar(
    dist.index,
    dist.values,
    color="#2E86AB",
    edgecolor="white",
    linewidth=0.5,
)
ax2.set_title(
    "Nb de commandes dans les 30j après la 1ère",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
ax2.set_xlabel("Nombre de commandes (30 premiers jours)", fontsize=11)
ax2.set_ylabel("Nombre de clients", fontsize=11)
ax2.set_xticks(dist.index)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax2.grid(axis="y", alpha=0.3, linestyle="--")
ax2.spines[["top", "right"]].set_visible(False)

total = len(orders_30d)
reachat = (orders_30d["nb_orders"] > 1).sum()
rate = reachat / total * 100
ax2.annotate(
    f"Taux de réachat 30j : {rate:.1f}%",
    xy=(0.97, 0.95),
    xycoords="axes fraction",
    ha="right",
    va="top",
    fontsize=11,
    color="#C0392B",
    fontweight="bold",
)

plt.tight_layout(pad=2.5)
plt.savefig("figures/nouveaux_clients.png", dpi=150, bbox_inches="tight")
print("Sauvegardé : figures/nouveaux_clients.png")

# --- Stats résumé ---
print(f"\nTotal clients uniques       : {len(first_order):,}")
print(f"Sessions uniques            : {sessions['session_id'].nunique():,}")
print(f"Sessions/client (moy)       : {sessions['session_id'].nunique() / len(first_order):.1f}")
print(f"Taux de réachat 30j         : {rate:.1f}%")
print(f"\nDistribution commandes 30j :")
print(orders_30d["nb_orders"].describe().round(2))
print(f"\nNouveaux clients/mois :")
print(new_per_month[["month", "new_clients"]].to_string(index=False))
