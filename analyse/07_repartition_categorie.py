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
df["categ"] = df["categ"].astype(str)

ca_categ = df.groupby("categ")["price"].sum().sort_index()
COLORS = ["#2E86AB", "#A23B72", "#F18F01"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].pie(
    ca_categ,
    labels=[f"Catégorie {c}" for c in ca_categ.index],
    autopct="%1.1f%%",
    colors=COLORS,
    startangle=90,
    wedgeprops={"edgecolor": "white"},
)
axes[0].set_title("Répartition CA par catégorie", fontweight="bold")

axes[1].bar([f"Cat. {c}" for c in ca_categ.index], ca_categ.values, color=COLORS)
axes[1].set_title("CA total par catégorie", fontweight="bold")
axes[1].set_ylabel("CA (€)")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1_000_000:.1f}M€"))
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(FIG_DIR / "07_repartition_categorie.png")
plt.show()

print("CA par catégorie :")
for c, v in ca_categ.items():
    print(f"  Catégorie {c} : {v:,.0f} € ({v/ca_categ.sum():.1%})")
