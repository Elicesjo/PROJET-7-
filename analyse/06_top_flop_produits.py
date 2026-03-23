from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
products = pd.read_csv(DATA_DIR / "products_clean.csv")

transactions = transactions[transactions["is_duplicate"] == False]
df = transactions.merge(products, on="id_prod")

ca_prod = df.groupby("id_prod")["price"].agg(ca="sum", ventes="count").sort_values("ca", ascending=False)
top10 = ca_prod.head(10)
flop10 = ca_prod.tail(10).sort_values("ca")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].barh(top10.index[::-1], top10["ca"][::-1], color="#2E86AB")
axes[0].set_title("Top 10 produits — CA", fontweight="bold")
axes[0].set_xlabel("CA (€)")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}€"))
axes[0].spines["top"].set_visible(False)
axes[0].spines["right"].set_visible(False)

axes[1].barh(flop10.index, flop10["ca"], color="#C73E1D")
axes[1].set_title("Flop 10 produits — CA", fontweight="bold")
axes[1].set_xlabel("CA (€)")
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(FIG_DIR / "06_top_flop_produits.png")
plt.show()

print("Top 10 :")
print(top10.to_string())
print("\nFlop 10 :")
print(flop10.to_string())
