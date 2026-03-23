from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path("DAN-P6-donnees/DAN-P6-donnees")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
    }
)

COLORS = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B"]

# ── 1. Chargement ─────────────────────────────────────────────────────────────

customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
transactions = pd.read_csv(DATA_DIR / "transactions.csv")

# ── 2. Nettoyage ──────────────────────────────────────────────────────────────

transactions = transactions[~transactions["client_id"].str.startswith("ct_")].copy()
transactions["date"] = pd.to_datetime(transactions["date"])

df = transactions.merge(products, on="id_prod").merge(customers, on="client_id")
df["categ"] = df["categ"].astype(str)
df["year_month"] = df["date"].dt.to_period("M")
df["age"] = 2023 - df["birth"]

print(f"Période        : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Transactions   : {len(df):,}")
print(f"Clients        : {df['client_id'].nunique():,}")
print(f"Références     : {df['id_prod'].nunique():,}")
print(f"Catégories     : {sorted(df['categ'].unique())}")
print(f"CA total       : {df['price'].sum():,.0f} €")

# ── 3. KPIs Ventes (Annabelle) ────────────────────────────────────────────────

# 3.1 CA mensuel + moyenne mobile 3 mois
monthly = df.groupby("year_month")["price"].sum().reset_index()
monthly["date"] = monthly["year_month"].dt.to_timestamp()
monthly["ma3"] = monthly["price"].rolling(3).mean()

fig, ax = plt.subplots(figsize=(13, 5))
ax.bar(monthly["date"], monthly["price"], width=25, alpha=0.55, color=COLORS[0], label="CA mensuel")
ax.plot(monthly["date"], monthly["ma3"], color=COLORS[3], linewidth=2.5, label="Moyenne mobile 3 mois")
ax.set_title("Chiffre d'affaires mensuel", fontsize=13, fontweight="bold")
ax.set_ylabel("CA (€)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k€"))
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "01_ca_mensuel.png")
plt.show()

# 3.2 CA mensuel par catégorie
ca_categ_time = df.groupby(["year_month", "categ"])["price"].sum().unstack("categ", fill_value=0)
ca_categ_time.index = ca_categ_time.index.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 5))
for i, col in enumerate(ca_categ_time.columns):
    ax.plot(ca_categ_time.index, ca_categ_time[col], label=f"Catégorie {col}", color=COLORS[i], linewidth=2)
ax.set_title("CA mensuel par catégorie", fontsize=13, fontweight="bold")
ax.set_ylabel("CA (€)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k€"))
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "02_ca_par_categorie.png")
plt.show()

# 3.3 Clients uniques par mois
clients_mois = df.groupby("year_month")["client_id"].nunique().reset_index()
clients_mois["date"] = clients_mois["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(clients_mois["date"], clients_mois["client_id"], marker="o", color=COLORS[1], linewidth=2)
ax.set_title("Clients uniques par mois", fontsize=13, fontweight="bold")
ax.set_ylabel("Nombre de clients")
plt.tight_layout()
plt.savefig(FIG_DIR / "03_clients_par_mois.png")
plt.show()

# 3.4 Transactions par mois
tx_mois = df.groupby("year_month").size().reset_index(name="n")
tx_mois["date"] = tx_mois["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 4))
ax.bar(tx_mois["date"], tx_mois["n"], width=25, alpha=0.7, color=COLORS[2])
ax.set_title("Nombre de transactions par mois", fontsize=13, fontweight="bold")
ax.set_ylabel("Transactions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig(FIG_DIR / "04_transactions_par_mois.png")
plt.show()

# 3.5 Références distinctes vendues par mois
refs_mois = df.groupby("year_month")["id_prod"].nunique().reset_index(name="n")
refs_mois["date"] = refs_mois["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(refs_mois["date"], refs_mois["n"], marker="o", color=COLORS[0], linewidth=2)
ax.set_title("Références distinctes vendues par mois", fontsize=13, fontweight="bold")
ax.set_ylabel("Références")
plt.tight_layout()
plt.savefig(FIG_DIR / "05_references_par_mois.png")
plt.show()

# 3.6 Top 10 / Flop 10 produits par CA
ca_prod = (
    df.groupby("id_prod")["price"]
    .agg(ca="sum", ventes="count")
    .sort_values("ca", ascending=False)
)
top10 = ca_prod.head(10)
flop10 = ca_prod.tail(10).sort_values("ca")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].barh(top10.index[::-1], top10["ca"][::-1], color=COLORS[0])
axes[0].set_title("Top 10 — CA", fontweight="bold")
axes[0].set_xlabel("CA (€)")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}€"))

axes[1].barh(flop10.index, flop10["ca"], color=COLORS[3])
axes[1].set_title("Flop 10 — CA", fontweight="bold")
axes[1].set_xlabel("CA (€)")

plt.tight_layout()
plt.savefig(FIG_DIR / "06_top_flop_produits.png")
plt.show()

# 3.7 Répartition CA par catégorie
ca_categ_total = df.groupby("categ")["price"].sum().sort_index()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].pie(
    ca_categ_total,
    labels=[f"Catégorie {c}" for c in ca_categ_total.index],
    autopct="%1.1f%%",
    colors=COLORS[: len(ca_categ_total)],
    startangle=90,
    wedgeprops={"edgecolor": "white"},
)
axes[0].set_title("Répartition CA par catégorie", fontweight="bold")

axes[1].bar(
    [f"Cat. {c}" for c in ca_categ_total.index],
    ca_categ_total.values,
    color=COLORS[: len(ca_categ_total)],
)
axes[1].set_title("CA total par catégorie", fontweight="bold")
axes[1].set_ylabel("CA (€)")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1_000_000:.1f}M€"))

plt.tight_layout()
plt.savefig(FIG_DIR / "07_repartition_categorie.png")
plt.show()

# 3.8 Répartition CA — clients à fort volume (proxy BtoB)
# Pas de flag BtoB explicite dans les données.
# Proxy : clients dont le CA dépasse moyenne + 2 écarts-types.
ca_client = df.groupby("client_id")["price"].sum()
seuil_btob = ca_client.mean() + 2 * ca_client.std()
btob_ids = ca_client[ca_client >= seuil_btob].index
print(f"\nProxy BtoB : {len(btob_ids)} clients (CA ≥ {seuil_btob:,.0f} €)")
print(f"Représentent {len(btob_ids)/len(ca_client):.1%} des clients")

df["is_btob"] = df["client_id"].isin(btob_ids)
ca_segments = df.groupby("is_btob")["price"].sum()
ca_segments.index = ["BtoC", "BtoB (fort volume)"]

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    ca_segments,
    labels=[f"{label}\n{val/ca_segments.sum():.1%}" for label, val in ca_segments.items()],
    colors=["#2E86AB", "#F18F01"],
    startangle=90,
    wedgeprops={"edgecolor": "white"},
)
ax.set_title(
    "Part du CA : BtoC vs clients à fort volume\n(proxy BtoB, seuil = moy. + 2σ)",
    fontweight="bold",
)
plt.tight_layout()
plt.savefig(FIG_DIR / "08_ca_btob.png")
plt.show()

# 3.9 Courbe de Lorenz
ca_sorted = ca_client.sort_values()
x = np.linspace(0, 1, len(ca_sorted))
y = ca_sorted.cumsum() / ca_sorted.sum()
gini = float(1 - 2 * np.trapezoid(y, x))

fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(x, y.values, color=COLORS[0], linewidth=2, label="Courbe de Lorenz")
ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1.5, label="Égalité parfaite")
ax.fill_between(x, y.values, x, alpha=0.15, color=COLORS[0])
ax.set_xlabel("Part cumulée des clients (du moins au plus dépensier)")
ax.set_ylabel("Part cumulée du CA")
ax.set_title("Courbe de Lorenz — concentration du CA", fontsize=13, fontweight="bold")
ax.text(0.05, 0.82, f"Indice de Gini : {gini:.3f}", transform=ax.transAxes, fontsize=12)
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "09_lorenz.png")
plt.show()
print(f"Indice de Gini : {gini:.3f}")

# ── 4. Corrélations comportementales (Julie) ──────────────────────────────────

client_stats = (
    df.groupby("client_id")
    .agg(
        ca_total=("price", "sum"),
        nb_transactions=("id_prod", "count"),
        panier_moyen=("price", "mean"),
        age=("age", "first"),
        sex=("sex", "first"),
    )
    .reset_index()
)

# 4.1 Genre ↔ catégorie achetée
genre_categ = df.groupby(["sex", "categ"]).size().unstack("categ", fill_value=0)
genre_categ_pct = genre_categ.div(genre_categ.sum(axis=1), axis=0) * 100
chi2, p_val, dof, _ = stats.chi2_contingency(genre_categ)

fig, ax = plt.subplots(figsize=(8, 5))
x_pos = np.arange(len(genre_categ_pct.index))
width = 0.25
for i, col in enumerate(genre_categ_pct.columns):
    ax.bar(x_pos + i * width, genre_categ_pct[col], width, label=f"Catégorie {col}", color=COLORS[i])
ax.set_xticks(x_pos + width)
ax.set_xticklabels(["Femme (f)", "Homme (m)"])
ax.set_title(
    f"Catégorie achetée selon le genre\nχ²={chi2:.1f}, p={p_val:.2e}, ddl={dof}",
    fontsize=12,
    fontweight="bold",
)
ax.set_ylabel("% des achats")
ax.legend(title="Catégorie")
plt.tight_layout()
plt.savefig(FIG_DIR / "10_genre_categorie.png")
plt.show()
print(f"\n[4.1] χ²={chi2:.2f}, p={p_val:.4f} — {'lien significatif' if p_val < 0.05 else 'pas de lien significatif'}")


def scatter_age(ax, y_col, ylabel, title):
    x = client_stats["age"]
    y = client_stats[y_col]
    r, p = stats.pearsonr(x, y)
    ax.scatter(x, y, alpha=0.25, s=8, color=COLORS[0])
    m, b = np.polyfit(x, y, 1)
    x_line = np.array([x.min(), x.max()])
    ax.plot(x_line, m * x_line + b, color=COLORS[3], linewidth=2)
    ax.set_title(f"{title}\nr de Pearson = {r:.3f}, p = {p:.2e}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Âge")
    ax.set_ylabel(ylabel)
    return r, p


# 4.2 Âge ↔ CA total
fig, ax = plt.subplots(figsize=(8, 5))
r, p_val = scatter_age(ax, "ca_total", "CA total (€)", "Âge ↔ CA total par client")
plt.tight_layout()
plt.savefig(FIG_DIR / "11_age_ca_total.png")
plt.show()
print(f"[4.2] r={r:.3f}, p={p_val:.4f}")

# 4.3 Âge ↔ Fréquence d'achat
fig, ax = plt.subplots(figsize=(8, 5))
r, p_val = scatter_age(ax, "nb_transactions", "Nombre de transactions", "Âge ↔ Fréquence d'achat")
plt.tight_layout()
plt.savefig(FIG_DIR / "12_age_frequence.png")
plt.show()
print(f"[4.3] r={r:.3f}, p={p_val:.4f}")

# 4.4 Âge ↔ Panier moyen
fig, ax = plt.subplots(figsize=(8, 5))
r, p_val = scatter_age(ax, "panier_moyen", "Panier moyen (€)", "Âge ↔ Panier moyen")
plt.tight_layout()
plt.savefig(FIG_DIR / "13_age_panier_moyen.png")
plt.show()
print(f"[4.4] r={r:.3f}, p={p_val:.4f}")

# 4.5 Âge ↔ Catégorie (tranches d'âge)
age_bins = [0, 25, 35, 50, 65, 110]
age_labels = ["<25", "25–34", "35–49", "50–64", "65+"]
df["tranche_age"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, right=False)

age_categ = (
    df.groupby(["tranche_age", "categ"], observed=True)
    .size()
    .unstack("categ", fill_value=0)
)
age_categ_pct = age_categ.div(age_categ.sum(axis=1), axis=0) * 100
chi2, p_val, dof, _ = stats.chi2_contingency(age_categ)

fig, ax = plt.subplots(figsize=(10, 5))
x_pos = np.arange(len(age_categ_pct.index))
width = 0.25
for i, col in enumerate(age_categ_pct.columns):
    ax.bar(x_pos + i * width, age_categ_pct[col], width, label=f"Catégorie {col}", color=COLORS[i])
ax.set_xticks(x_pos + width)
ax.set_xticklabels(age_labels)
ax.set_title(
    f"Catégorie achetée selon la tranche d'âge\nχ²={chi2:.1f}, p={p_val:.2e}, ddl={dof}",
    fontsize=12,
    fontweight="bold",
)
ax.set_ylabel("% des achats")
ax.set_xlabel("Tranche d'âge")
ax.legend(title="Catégorie")
plt.tight_layout()
plt.savefig(FIG_DIR / "14_age_categorie.png")
plt.show()
print(f"\n[4.5] χ²={chi2:.2f}, p={p_val:.4f} — {'lien significatif' if p_val < 0.05 else 'pas de lien significatif'}")

print(f"\nAnalyse terminée — {len(list(FIG_DIR.glob('*.png')))} figures dans {FIG_DIR}/")
