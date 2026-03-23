from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path("data_clean")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions_clean.csv", parse_dates=["date"])
products = pd.read_csv(DATA_DIR / "products_clean.csv")

transactions = transactions[transactions["is_duplicate"] == False]
df = transactions.merge(products, on="id_prod")

# Proxy BtoB : clients dont le CA total dépasse moyenne + 2 écarts-types
ca_client = df.groupby("client_id")["price"].sum()
seuil = ca_client.mean() + 2 * ca_client.std()
btob_ids = ca_client[ca_client >= seuil].index

df["segment"] = df["client_id"].apply(lambda x: "BtoB (fort volume)" if x in btob_ids else "BtoC")
ca_segments = df.groupby("segment")["price"].sum()

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    ca_segments,
    labels=[f"{label}\n{val/ca_segments.sum():.1%}" for label, val in ca_segments.items()],
    colors=["#F18F01", "#2E86AB"],
    startangle=90,
    wedgeprops={"edgecolor": "white"},
)
ax.set_title(
    f"Part du CA : BtoC vs clients à fort volume\n(proxy BtoB — seuil : {seuil:,.0f} €)",
    fontweight="bold",
)
plt.tight_layout()
plt.savefig(FIG_DIR / "08_ca_btob.png")
plt.show()

print(f"Seuil BtoB (moy + 2σ) : {seuil:,.0f} €")
print(f"Clients BtoB proxy    : {len(btob_ids)} ({len(btob_ids)/len(ca_client):.1%} des clients)")
print(f"CA BtoB               : {ca_segments.get('BtoB (fort volume)', 0):,.0f} € ({ca_segments.get('BtoB (fort volume)', 0)/ca_segments.sum():.1%})")
print(f"CA BtoC               : {ca_segments.get('BtoC', 0):,.0f} € ({ca_segments.get('BtoC', 0)/ca_segments.sum():.1%})")
