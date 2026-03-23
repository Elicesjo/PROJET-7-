from pathlib import Path

import pandas as pd

DATA_DIR = Path("DAN-P6-donnees/DAN-P6-donnees")
OUT_DIR = Path("data_clean")
OUT_DIR.mkdir(exist_ok=True)

products = pd.read_csv(DATA_DIR / "products.csv")
print(f"products brut    : {len(products):,} lignes")

# Supprimer la ligne de test : id_prod = "T_0", prix = -1.0
mask_test = products["id_prod"] == "T_0"
print(f"  lignes test    : {mask_test.sum()}")

products_clean = products[~mask_test].copy()

print(f"products_clean   : {len(products_clean):,} lignes")
print(f"  supprimés      : {len(products) - len(products_clean)}")

products_clean.to_csv(OUT_DIR / "products_clean.csv", index=False)
print(f"\nSauvegardé → {OUT_DIR}/products_clean.csv")
