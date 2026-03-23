from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
transactions = transactions[transactions["is_duplicate"] == False]

transactions["year_month"] = transactions["date"].dt.to_period("M")
refs_mois = transactions.groupby("year_month")["id_prod"].nunique().reset_index(name="n")
refs_mois["date"] = refs_mois["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(refs_mois["date"], refs_mois["n"], marker="o", color="#2E86AB", linewidth=2)
ax.set_title("Références distinctes vendues par mois", fontsize=13, fontweight="bold")
ax.set_ylabel("Références")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(FIG_DIR / "05_references_par_mois.png")
plt.show()

print(f"Moy. références/mois : {refs_mois['n'].mean():.0f}")
print(f"Max                  : {refs_mois['n'].max()} ({refs_mois.loc[refs_mois['n'].idxmax(), 'year_month']})")
print(f"Min                  : {refs_mois['n'].min()} ({refs_mois.loc[refs_mois['n'].idxmin(), 'year_month']})")
