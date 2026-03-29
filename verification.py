from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path("data_clean")

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
products = pd.read_csv(DATA_DIR / "products_clean.csv")
customers = pd.read_csv(DATA_DIR / "customers_clean.csv")

transactions = transactions[transactions["is_duplicate"] == False]
df = transactions.merge(products, on="id_prod").merge(customers, on="client_id")
df["age"] = 2023 - df["birth"]
df["categ"] = df["categ"].astype(str)

SEP = "=" * 55

# ── Slide 2 — Chiffres clés ───────────────────────────────
print(SEP)
print("SLIDE 2 — Chiffres clés")
print(SEP)
ca_total = df["price"].sum()
nb_tx = len(df)
nb_clients = df["client_id"].nunique()
ca_mensuel = df.groupby(df["date"].dt.to_period("M"))["price"].sum().mean()
panier_moyen = df.groupby("session_id")["price"].sum().mean()

print(f"CA total          : {ca_total:,.0f} € → présentation : 11,8 M€  {'✓' if 11_700_000 < ca_total < 11_900_000 else '✗'}")
print(f"Nb transactions   : {nb_tx:,}       → présentation : 678 284  {'✓' if nb_tx == 678_284 else '✗'}")
print(f"Clients actifs    : {nb_clients:,}       → présentation : 8 600    {'✓' if nb_clients == 8_600 else '✗'}")
print(f"CA moyen/mois     : {ca_mensuel:,.0f} €   → présentation : 493 k€   {'✓' if 490_000 < ca_mensuel < 496_000 else '✗'}")
print(f"Panier moyen      : {panier_moyen:.2f} €      → présentation : 34,58 €  {'✓' if 34 < panier_moyen < 35 else '✗'}")

# ── Slide 3 — CA mensuel ──────────────────────────────────
print(f"\n{SEP}")
print("SLIDE 3 — CA mensuel")
print(SEP)
monthly = df.groupby(df["date"].dt.to_period("M"))["price"].sum()
print(f"Mois record       : {monthly.idxmax()}  → présentation : 2022-02  {'✓' if str(monthly.idxmax()) == '2022-02' else '✗'}")
print(f"Mois creux        : {monthly.idxmin()}  → présentation : 2021-10  {'✓' if str(monthly.idxmin()) == '2021-10' else '✗'}")

# ── Slide 4 — CA par catégorie ────────────────────────────
print(f"\n{SEP}")
print("SLIDE 4 — CA par catégorie")
print(SEP)
ca_categ = df.groupby("categ")["price"].sum()
for c, v in ca_categ.items():
    pct = v / ca_categ.sum()
    print(f"Catégorie {c}       : {v:,.0f} € ({pct:.1%})")

# ── Slide 5 — Activité clients ────────────────────────────
print(f"\n{SEP}")
print("SLIDE 5 — Activité clients & transactions")
print(SEP)
clients_mois = df.groupby(df["date"].dt.to_period("M"))["client_id"].nunique()
tx_mois = df.groupby(df["date"].dt.to_period("M")).size()
refs_mois = df.groupby(df["date"].dt.to_period("M"))["id_prod"].nunique()
print(f"Clients/mois moy  : {clients_mois.mean():.0f}    → présentation : ~5 700  {'✓' if 5600 < clients_mois.mean() < 5800 else '✗'}")
print(f"Transactions/mois : {tx_mois.mean():,.0f}    → présentation : ~28 000 {'✓' if 27000 < tx_mois.mean() < 29000 else '✗'}")
print(f"Références/mois   : {refs_mois.mean():.0f}    → présentation : ~2 450  {'✓' if 2400 < refs_mois.mean() < 2500 else '✗'}")

# ── Slide 6 — Top / Flop ─────────────────────────────────
print(f"\n{SEP}")
print("SLIDE 6 — Top produit")
print(SEP)
ca_prod = df.groupby("id_prod")["price"].sum().sort_values(ascending=False)
print(f"Top produit       : {ca_prod.idxmax()} — {ca_prod.max():,.0f} €  → présentation : 2_159 / 95 k€  {'✓' if ca_prod.idxmax() == '2_159' else '✗'}")

# ── Slide 7 — Lorenz + BtoB ───────────────────────────────
print(f"\n{SEP}")
print("SLIDE 7 — Lorenz & BtoB")
print(SEP)
ca_client = df.groupby("client_id")["price"].sum().sort_values()
x = np.linspace(0, 1, len(ca_client))
y = ca_client.cumsum() / ca_client.sum()
gini = float(1 - 2 * np.trapezoid(y, x))
p20 = float(y.iloc[int(len(y) * 0.8)])

seuil = ca_client.mean() + 2 * ca_client.std()
btob_ids = ca_client[ca_client >= seuil].index
ca_btob = df[df["client_id"].isin(btob_ids)]["price"].sum()
pct_btob = ca_btob / df["price"].sum()

print(f"Indice de Gini    : {gini:.3f}   → présentation : 0.446  {'✓' if abs(gini - 0.446) < 0.005 else '✗'}")
print(f"Top 20% clients   : {1-p20:.1%} du CA → présentation : 48.4%  {'✓' if abs((1-p20) - 0.484) < 0.005 else '✗'}")
print(f"Clients BtoB proxy: {len(btob_ids)}         → présentation : 4       {'✓' if len(btob_ids) == 4 else '✗'}")
print(f"CA BtoB           : {pct_btob:.1%}      → présentation : 7.4%    {'✓' if abs(pct_btob - 0.074) < 0.005 else '✗'}")

# ── Slides 8-10 — Corrélations ────────────────────────────
print(f"\n{SEP}")
print("SLIDES 8-10 — Corrélations")
print(SEP)
client_stats = df.groupby("client_id").agg(
    ca_total=("price", "sum"),
    nb_transactions=("id_prod", "count"),
    panier_moyen=("price", "mean"),
    age=("age", "first"),
    sex=("sex", "first"),
).reset_index()

r_ca, p_ca = stats.pearsonr(client_stats["age"], client_stats["ca_total"])
r_freq, p_freq = stats.pearsonr(client_stats["age"], client_stats["nb_transactions"])
r_panier, p_panier = stats.pearsonr(client_stats["age"], client_stats["panier_moyen"])

genre_categ = df.groupby(["sex", "categ"]).size().unstack("categ", fill_value=0)
chi2_genre, p_genre, _, _ = stats.chi2_contingency(genre_categ)

age_bins = [0, 25, 35, 50, 65, 110]
age_labels = ["<25", "25–34", "35–49", "50–64", "65+"]
df["tranche_age"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, right=False)
age_categ = df.groupby(["tranche_age", "categ"], observed=True).size().unstack("categ", fill_value=0)
chi2_age, p_age, _, _ = stats.chi2_contingency(age_categ)
age_categ_pct = age_categ.div(age_categ.sum(axis=1), axis=0) * 100

print(f"r Âge/CA total    : {r_ca:.3f}   → présentation : -0.040  {'✓' if abs(r_ca - (-0.040)) < 0.005 else '✗'}")
print(f"r Âge/Fréquence   : {r_freq:.3f}   → présentation : 0.007   {'✓' if abs(r_freq - 0.007) < 0.005 else '✗'}")
print(f"r Âge/Panier moy  : {r_panier:.3f}  → présentation : -0.513  {'✓' if abs(r_panier - (-0.513)) < 0.005 else '✗'}")
print(f"p Genre/Catég     : {p_genre:.4f}  → significatif  {'✓' if p_genre < 0.05 else '✗'}")
print(f"p Âge/Catég       : {p_age:.4f}  → significatif  {'✓' if p_age < 0.05 else '✗'}")
print(f"\nRépartition <25 ans par catégorie :")
print(age_categ_pct.loc["<25"].round(1).to_string())
print(f"→ présentation : cat.2 = 42.5%  {'✓' if abs(age_categ_pct.loc['<25', '2'] - 42.5) < 1 else '✗'}")

print(f"\n{SEP}")
print("RÉSUMÉ")
print(SEP)
print("Tous les chiffres marqués ✓ sont vérifiés.")
print("Un ✗ indique un écart à corriger dans la présentation.")
