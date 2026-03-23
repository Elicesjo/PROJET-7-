from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
transactions = transactions[transactions["is_duplicate"] == False]

transactions["year_month"] = transactions["date"].dt.to_period("M")
clients_mois = transactions.groupby("year_month")["client_id"].nunique().reset_index()
clients_mois["date"] = clients_mois["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(clients_mois["date"], clients_mois["client_id"], marker="o", color="#A23B72", linewidth=2)
ax.set_title("Clients uniques par mois", fontsize=13, fontweight="bold")
ax.set_ylabel("Nombre de clients")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(FIG_DIR / "03_clients_par_mois.png")
plt.show()

print(f"Moy. clients/mois : {clients_mois['client_id'].mean():.0f}")
print(f"Max               : {clients_mois['client_id'].max()} ({clients_mois.loc[clients_mois['client_id'].idxmax(), 'year_month']})")
print(f"Min               : {clients_mois['client_id'].min()} ({clients_mois.loc[clients_mois['client_id'].idxmin(), 'year_month']})")
