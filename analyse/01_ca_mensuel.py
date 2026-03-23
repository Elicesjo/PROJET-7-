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

df["year_month"] = df["date"].dt.to_period("M")
monthly = df.groupby("year_month")["price"].sum().reset_index()
monthly["date"] = monthly["year_month"].dt.to_timestamp()
monthly["ma3"] = monthly["price"].rolling(3).mean()

fig, ax = plt.subplots(figsize=(13, 5))
ax.bar(monthly["date"], monthly["price"], width=25, alpha=0.55, color="#2E86AB", label="CA mensuel")
ax.plot(monthly["date"], monthly["ma3"], color="#C73E1D", linewidth=2.5, label="Moyenne mobile 3 mois")
ax.set_title("Chiffre d'affaires mensuel", fontsize=13, fontweight="bold")
ax.set_ylabel("CA (€)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k€"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "01_ca_mensuel.png")
plt.show()

print("CA total        :", f"{df['price'].sum():,.0f} €")
print("CA moyen/mois   :", f"{monthly['price'].mean():,.0f} €")
print("Mois record     :", monthly.loc[monthly['price'].idxmax(), 'year_month'])
print("Mois creux      :", monthly.loc[monthly['price'].idxmin(), 'year_month'])
