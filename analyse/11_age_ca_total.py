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
df["age"] = 2023 - df["birth"]

client_stats = df.groupby("client_id").agg(ca_total=("price", "sum"), age=("age", "first")).reset_index()

r, p_val = stats.pearsonr(client_stats["age"], client_stats["ca_total"])
m, b = np.polyfit(client_stats["age"], client_stats["ca_total"], 1)
x_line = np.array([client_stats["age"].min(), client_stats["age"].max()])

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(client_stats["age"], client_stats["ca_total"], alpha=0.25, s=8, color="#2E86AB")
ax.plot(x_line, m * x_line + b, color="#C73E1D", linewidth=2)
ax.set_title(f"Âge ↔ CA total par client\nr de Pearson = {r:.3f}, p = {p_val:.2e}", fontsize=12, fontweight="bold")
ax.set_xlabel("Âge")
ax.set_ylabel("CA total (€)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(FIG_DIR / "11_age_ca_total.png")
plt.show()

print(f"r de Pearson = {r:.3f}, p = {p_val:.4f}")
print("→", "Corrélation significative (p < 0.05)" if p_val < 0.05 else "Pas de corrélation significative (p ≥ 0.05)")
print(f"Pente : +{m:.2f} € de CA par année d'âge supplémentaire")
