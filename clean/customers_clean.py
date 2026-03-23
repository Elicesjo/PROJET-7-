from pathlib import Path

import pandas as pd

DATA_DIR = Path("DAN-P6-donnees/DAN-P6-donnees")
OUT_DIR = Path("data_clean")
OUT_DIR.mkdir(exist_ok=True)

customers = pd.read_csv(DATA_DIR / "customers.csv")
print(f"customers brut   : {len(customers):,} lignes")

# Supprimer les clients de test (ct_0, ct_1)
mask_test = customers["client_id"].str.startswith("ct_")
print(f"  clients test   : {mask_test.sum()}")

customers_clean = customers[~mask_test].copy()

print(f"customers_clean  : {len(customers_clean):,} lignes")
print(f"  supprimés      : {len(customers) - len(customers_clean)}")

customers_clean.to_csv(OUT_DIR / "customers_clean.csv", index=False)
print(f"\nSauvegardé → {OUT_DIR}/customers_clean.csv")
