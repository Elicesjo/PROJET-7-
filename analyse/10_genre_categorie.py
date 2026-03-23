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

genre_categ = df.groupby(["sex", "categ"]).size().unstack("categ", fill_value=0)
genre_categ_pct = genre_categ.div(genre_categ.sum(axis=1), axis=0) * 100
chi2, p_val, dof, _ = stats.chi2_contingency(genre_categ)

COLORS = ["#2E86AB", "#A23B72", "#F18F01"]
fig, ax = plt.subplots(figsize=(8, 5))
x_pos = np.arange(len(genre_categ_pct.index))
width = 0.25
for i, col in enumerate(genre_categ_pct.columns):
    ax.bar(x_pos + i * width, genre_categ_pct[col], width, label=f"Catégorie {col}", color=COLORS[i])
ax.set_xticks(x_pos + width)
ax.set_xticklabels(["Femme (f)", "Homme (m)"])
ax.set_title(
    f"Catégorie achetée selon le genre\nχ²={chi2:.1f}, p={p_val:.2e}, ddl={dof}",
    fontsize=12, fontweight="bold",
)
ax.set_ylabel("% des achats")
ax.legend(title="Catégorie")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(FIG_DIR / "10_genre_categorie.png")
plt.show()

print(f"Chi² = {chi2:.2f}, p = {p_val:.4f}, ddl = {dof}")
print("→", "Lien significatif (p < 0.05)" if p_val < 0.05 else "Pas de lien significatif (p ≥ 0.05)")
print("\nRépartition % par genre :")
print(genre_categ_pct.round(1).to_string())
