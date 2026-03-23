from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
transactions = transactions[transactions["is_duplicate"] == False]

transactions["year_month"] = transactions["date"].dt.to_period("M")
tx_mois = transactions.groupby("year_month").size().reset_index(name="n")
tx_mois["date"] = tx_mois["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 4))
ax.bar(tx_mois["date"], tx_mois["n"], width=25, alpha=0.7, color="#F18F01")
ax.set_title("Nombre de transactions par mois", fontsize=13, fontweight="bold")
ax.set_ylabel("Transactions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(FIG_DIR / "04_transactions_par_mois.png")
plt.show()

print(f"Total transactions  : {tx_mois['n'].sum():,}")
print(f"Moy./mois           : {tx_mois['n'].mean():,.0f}")
print(f"Mois record         : {tx_mois.loc[tx_mois['n'].idxmax(), 'year_month']} ({tx_mois['n'].max():,})")
