from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
products = pd.read_csv(DATA_DIR / "products_clean.csv")

transactions = transactions[transactions["is_duplicate"] == False]
df = transactions.merge(products, on="id_prod")

ca_client = df.groupby("client_id")["price"].sum().sort_values()
x = np.linspace(0, 1, len(ca_client))
y = ca_client.cumsum() / ca_client.sum()
gini = float(1 - 2 * np.trapezoid(y, x))

fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(x, y.values, color="#2E86AB", linewidth=2, label="Courbe de Lorenz")
ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1.5, label="Égalité parfaite")
ax.fill_between(x, y.values, x, alpha=0.15, color="#2E86AB")
ax.set_xlabel("Part cumulée des clients (du moins au plus dépensier)")
ax.set_ylabel("Part cumulée du CA")
ax.set_title("Courbe de Lorenz — concentration du CA", fontsize=13, fontweight="bold")
ax.text(0.05, 0.82, f"Indice de Gini : {gini:.3f}", transform=ax.transAxes, fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "09_lorenz.png")
plt.show()

print(f"Indice de Gini : {gini:.3f}")
p20 = float(y.iloc[int(len(y) * 0.8)])
print(f"Les 20% des clients les plus dépensiers représentent {1 - p20:.1%} du CA")
