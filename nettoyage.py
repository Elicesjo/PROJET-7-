from pathlib import Path

import pandas as pd

DATA_DIR = Path("DAN-P6-donnees/DAN-P6-donnees")
OUT_DIR = Path("data_clean")
OUT_DIR.mkdir(exist_ok=True)

# ── customers ─────────────────────────────────────────────────────────────────

customers = pd.read_csv(DATA_DIR / "customers.csv")
print(f"customers brut      : {len(customers):,} lignes")

# Supprimer les clients de test (ct_0, ct_1)
mask_test = customers["client_id"].str.startswith("ct_")
print(f"  clients test      : {mask_test.sum()}")

customers_clean = customers[~mask_test].copy()

print(f"customers_clean     : {len(customers_clean):,} lignes")
print(f"  supprimés         : {len(customers) - len(customers_clean)}")
customers_clean.to_csv(OUT_DIR / "customers_clean.csv", index=False)

# ── products ──────────────────────────────────────────────────────────────────

products = pd.read_csv(DATA_DIR / "products.csv")
print(f"\nproducts brut       : {len(products):,} lignes")

# Supprimer la ligne de test : id_prod = "T_0", prix = -1.0
mask_test = products["id_prod"] == "T_0"
print(f"  lignes test (T_0) : {mask_test.sum()}")

products_clean = products[~mask_test].copy()

print(f"products_clean      : {len(products_clean):,} lignes")
print(f"  supprimés         : {len(products) - len(products_clean)}")
products_clean.to_csv(OUT_DIR / "products_clean.csv", index=False)

# ── transactions ──────────────────────────────────────────────────────────────

transactions = pd.read_csv(DATA_DIR / "transactions.csv")
transactions["date"] = pd.to_datetime(transactions["date"], errors="coerce")
print(f"\ntransactions brut   : {len(transactions):,} lignes")

# 1. Supprimer les lignes de test (client_id = ct_0, ct_1 / id_prod = T_0)
mask_test = transactions["client_id"].str.startswith("ct_")
print(f"  lignes test       : {mask_test.sum()}")
transactions = transactions[~mask_test].copy()

# 2. Supprimer le produit 0_2245 absent du catalogue (introuvable dans products_clean)
mask_missing_prod = transactions["id_prod"] == "0_2245"
print(f"  produit manquant (0_2245) : {mask_missing_prod.sum()}")
transactions = transactions[~mask_missing_prod].copy()

# 3. Supprimer les doublons (même session_id + même id_prod) — garder la 1re occurrence
n_before = len(transactions)
transactions = transactions.sort_values("date").drop_duplicates(
    subset=["session_id", "id_prod"], keep="first"
)
print(f"  doublons session+produit  : {n_before - len(transactions)}")

transactions_clean = transactions.copy()

print(f"transactions_clean  : {len(transactions_clean):,} lignes")
print(f"  supprimés (total) : {len(pd.read_csv(DATA_DIR / 'transactions.csv')) - len(transactions_clean):,}")
transactions_clean.to_csv(OUT_DIR / "transactions_clean.csv", index=False)

print(f"\nFichiers sauvegardés dans {OUT_DIR}/")
