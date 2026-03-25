from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

st.set_page_config(page_title="Lapage — Dashboard", layout="wide")

CLEAN_DIR = Path("data_clean")
COLORS = ["#2E86AB", "#A23B72", "#F18F01"]


@st.cache_data
def load_data():
    tx = pd.read_csv(CLEAN_DIR / "transactions_clean.csv", parse_dates=["date"])
    tx = tx[tx["is_duplicate"] == False]
    prod = pd.read_csv(CLEAN_DIR / "products_clean.csv")
    cust = pd.read_csv(CLEAN_DIR / "customers_clean.csv")
    df = tx.merge(prod, on="id_prod")
    df_full = df.merge(cust, on="client_id")
    df_full["categ"] = df_full["categ"].astype(str)
    df_full["age"] = 2023 - df_full["birth"]
    return tx, df, df_full


tx, df, df_full = load_data()

st.title("Lapage — Analyse e-commerce 2021–2023")

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.header("Paramètres")
periode = st.sidebar.selectbox("Période d'agrégation", ["Jour", "Semaine", "Mois"], index=2)
freq_map = {"Jour": "D", "Semaine": "W", "Mois": "ME"}
freq = freq_map[periode]

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.subheader("Chiffres clés")
k1, k2, k3, k4 = st.columns(4)
k1.metric("CA total", f"{df['price'].sum():,.0f} €")
k2.metric("Clients actifs", f"{tx['client_id'].nunique():,}")
k3.metric("Transactions", f"{len(tx):,}")
k4.metric("Prix moyen / article", f"{df['price'].mean():.2f} €")

st.divider()

# ── CA avec moyenne mobile ─────────────────────────────────────────────────────
st.subheader("Chiffre d'affaires")
window = st.slider("Fenêtre moyenne mobile (périodes)", 2, 12, 3)

ca_periode = df.set_index("date")["price"].resample(freq).sum().reset_index()
ca_periode["ma"] = ca_periode["price"].rolling(window).mean()

fig, ax = plt.subplots(figsize=(12, 4))
ax.bar(ca_periode["date"], ca_periode["price"], width={"D": 0.8, "W": 5, "ME": 25}[freq],
       alpha=0.55, color="#2E86AB", label=f"CA ({periode.lower()})")
ax.plot(ca_periode["date"], ca_periode["ma"], color="#C73E1D", linewidth=2,
        label=f"Moy. mobile {window} périodes")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k€"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend()
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()

# ── CA par catégorie ───────────────────────────────────────────────────────────
st.subheader("CA par catégorie")

ca_cat = df.set_index("date").groupby("categ")["price"].resample(freq).sum().reset_index()
ca_cat_pivot = ca_cat.pivot(index="date", columns="categ", values="price").fillna(0)

fig, ax = plt.subplots(figsize=(12, 4))
for i, col in enumerate(ca_cat_pivot.columns):
    ax.plot(ca_cat_pivot.index, ca_cat_pivot[col], label=f"Catégorie {col}",
            color=COLORS[i], linewidth=2)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k€"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend()
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()

# ── Clients / Transactions / Produits ─────────────────────────────────────────
st.subheader("Activité")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Clients uniques**")
    clients = tx.set_index("date")["client_id"].resample(freq).nunique().reset_index()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(clients["date"], clients["client_id"], color="#A23B72", linewidth=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("**Transactions**")
    nb_tx = tx.set_index("date").resample(freq).size().reset_index(name="n")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(nb_tx["date"], nb_tx["n"], color="#F18F01",
           width={"D": 0.8, "W": 5, "ME": 25}[freq], alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col3:
    st.markdown("**Références distinctes vendues**")
    refs = tx.set_index("date")["id_prod"].resample(freq).nunique().reset_index(name="n")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(refs["date"], refs["n"], color="#2E86AB", linewidth=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

# ── Top / Flop produits ────────────────────────────────────────────────────────
st.subheader("Top / Flop produits")
n_top = st.slider("Nombre de produits à afficher", 5, 20, 10)

ca_prod = df.groupby("id_prod")["price"].sum().sort_values(ascending=False)
top = ca_prod.head(n_top)
flop = ca_prod.tail(n_top).sort_values()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].barh(top.index[::-1], top.values[::-1], color="#2E86AB")
axes[0].set_title(f"Top {n_top} — CA", fontweight="bold")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}€"))
axes[0].spines["top"].set_visible(False)
axes[0].spines["right"].set_visible(False)

axes[1].barh(flop.index, flop.values, color="#C73E1D")
axes[1].set_title(f"Flop {n_top} — CA", fontweight="bold")
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()

# ── Corrélations Julie ─────────────────────────────────────────────────────────
st.subheader("Corrélations comportementales")
corr_choice = st.selectbox("Analyse", [
    "Genre ↔ Catégorie (Chi²)",
    "Âge ↔ CA total (Pearson)",
    "Âge ↔ Fréquence d'achat (Pearson)",
    "Âge ↔ Panier moyen (Pearson)",
    "Tranche d'âge ↔ Catégorie (Chi²)",
])

if corr_choice == "Genre ↔ Catégorie (Chi²)":
    gc = df_full.groupby(["sex", "categ"]).size().unstack(fill_value=0)
    gc_pct = gc.div(gc.sum(axis=1), axis=0) * 100
    chi2_v, p_v, dof, _ = stats.chi2_contingency(gc)
    st.info(f"χ² = {chi2_v:.1f} | p = {p_v:.2e} | ddl = {dof} → {'Lien significatif ✓' if p_v < 0.05 else 'Pas de lien significatif'}")
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(gc_pct.index))
    w = 0.25
    for i, col in enumerate(gc_pct.columns):
        ax.bar(x + i * w, gc_pct[col], w, label=f"Cat. {col}", color=COLORS[i])
    ax.set_xticks(x + w)
    ax.set_xticklabels(["Femme", "Homme"])
    ax.set_ylabel("% des achats")
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

elif corr_choice in ["Âge ↔ CA total (Pearson)", "Âge ↔ Fréquence d'achat (Pearson)", "Âge ↔ Panier moyen (Pearson)"]:
    agg_map = {
        "Âge ↔ CA total (Pearson)": ("price", "sum", "CA total (€)"),
        "Âge ↔ Fréquence d'achat (Pearson)": ("id_prod", "count", "Nb transactions"),
        "Âge ↔ Panier moyen (Pearson)": ("price", "mean", "Panier moyen (€)"),
    }
    col_src, agg_fn, ylabel = agg_map[corr_choice]
    cs = df_full.groupby("client_id").agg(val=(col_src, agg_fn), age=("age", "first")).reset_index()
    r, p_v = stats.pearsonr(cs["age"], cs["val"])
    m, b = np.polyfit(cs["age"], cs["val"], 1)
    x_line = np.array([cs["age"].min(), cs["age"].max()])
    st.info(f"r de Pearson = {r:.3f} | p = {p_v:.2e} → {'Corrélation significative ✓' if p_v < 0.05 else 'Pas de corrélation significative'}")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(cs["age"], cs["val"], alpha=0.2, s=8, color="#2E86AB")
    ax.plot(x_line, m * x_line + b, color="#C73E1D", linewidth=2)
    ax.set_xlabel("Âge")
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

elif corr_choice == "Tranche d'âge ↔ Catégorie (Chi²)":
    bins = [0, 25, 35, 50, 65, 110]
    labels = ["<25", "25–34", "35–49", "50–64", "65+"]
    df_full["tranche_age"] = pd.cut(df_full["age"], bins=bins, labels=labels, right=False)
    ac = df_full.groupby(["tranche_age", "categ"], observed=True).size().unstack(fill_value=0)
    ac_pct = ac.div(ac.sum(axis=1), axis=0) * 100
    chi2_v, p_v, dof, _ = stats.chi2_contingency(ac)
    st.info(f"χ² = {chi2_v:.1f} | p = {p_v:.2e} | ddl = {dof} → {'Lien significatif ✓' if p_v < 0.05 else 'Pas de lien significatif'}")
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(ac_pct.index))
    w = 0.25
    for i, col in enumerate(ac_pct.columns):
        ax.bar(x + i * w, ac_pct[col], w, label=f"Cat. {col}", color=COLORS[i])
    ax.set_xticks(x + w)
    ax.set_xticklabels(labels)
    ax.set_ylabel("% des achats")
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
