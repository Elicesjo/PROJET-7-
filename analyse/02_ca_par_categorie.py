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
df["year_month"] = df["date"].dt.to_period("M")

ca_categ_time = df.groupby(["year_month", "categ"])["price"].sum().unstack("categ", fill_value=0)
ca_categ_time.index = ca_categ_time.index.to_timestamp()

COLORS = ["#2E86AB", "#A23B72", "#F18F01"]

fig, ax = plt.subplots(figsize=(13, 5))
for i, col in enumerate(ca_categ_time.columns):
    ax.plot(ca_categ_time.index, ca_categ_time[col], label=f"Catégorie {col}", color=COLORS[i], linewidth=2)
ax.set_title("CA mensuel par catégorie", fontsize=13, fontweight="bold")
ax.set_ylabel("CA (€)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k€"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "02_ca_par_categorie.png")
plt.show()

ca_total = df.groupby("categ")["price"].sum()
print("CA par catégorie :")
for c, v in ca_total.items():
    print(f"  Catégorie {c} : {v:,.0f} € ({v/ca_total.sum():.1%})")
