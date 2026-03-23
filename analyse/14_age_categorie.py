from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
products = pd.read_csv(DATA_DIR / "products_clean.csv")
customers = pd.read_csv(DATA_DIR / "customers_clean.csv")

transactions = transactions[transactions["is_duplicate"] == False]
df = transactions.merge(products, on="id_prod").merge(customers, on="client_id")
df["categ"] = df["categ"].astype(str)
df["age"] = 2023 - df["birth"]

age_bins = [0, 25, 35, 50, 65, 110]
age_labels = ["<25", "25–34", "35–49", "50–64", "65+"]
df["tranche_age"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, right=False)

age_categ = df.groupby(["tranche_age", "categ"], observed=True).size().unstack("categ", fill_value=0)
age_categ_pct = age_categ.div(age_categ.sum(axis=1), axis=0) * 100
chi2, p_val, dof, _ = stats.chi2_contingency(age_categ)

COLORS = ["#2E86AB", "#A23B72", "#F18F01"]
fig, ax = plt.subplots(figsize=(10, 5))
x_pos = np.arange(len(age_categ_pct.index))
width = 0.25
for i, col in enumerate(age_categ_pct.columns):
    ax.bar(x_pos + i * width, age_categ_pct[col], width, label=f"Catégorie {col}", color=COLORS[i])
ax.set_xticks(x_pos + width)
ax.set_xticklabels(age_labels)
ax.set_title(
    f"Catégorie achetée selon la tranche d'âge\nχ²={chi2:.1f}, p={p_val:.2e}, ddl={dof}",
    fontsize=12, fontweight="bold",
)
ax.set_ylabel("% des achats")
ax.set_xlabel("Tranche d'âge")
ax.legend(title="Catégorie")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(FIG_DIR / "14_age_categorie.png")
plt.show()

print(f"Chi² = {chi2:.2f}, p = {p_val:.4f}, ddl = {dof}")
print("→", "Lien significatif (p < 0.05)" if p_val < 0.05 else "Pas de lien significatif (p ≥ 0.05)")
print("\nRépartition % par tranche d'âge :")
print(age_categ_pct.round(1).to_string())
