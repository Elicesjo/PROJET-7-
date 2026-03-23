from pathlib import Path

import pandas as pd

DATA_DIR = Path("DAN-P6-donnees/DAN-P6-donnees")
OUT_DIR = Path("data_clean")
OUT_DIR.mkdir(exist_ok=True)

transactions = pd.read_csv(DATA_DIR / "transactions.csv")
transactions["date"] = pd.to_datetime(transactions["date"], errors="coerce")
print(f"transactions brut          : {len(transactions):,} lignes")

# 1. Supprimer les lignes de test (client_id = ct_0 / ct_1) — pas de valeur analytique
mask_test = transactions["client_id"].str.startswith("ct_")
print(f"  lignes test              : {mask_test.sum()}")
transactions = transactions[~mask_test].copy()

# 2. Supprimer le produit 0_2245 absent du catalogue — jointure impossible
mask_missing = transactions["id_prod"] == "0_2245"
print(f"  produit manquant (0_2245): {mask_missing.sum()}")
transactions = transactions[~mask_missing].copy()

# 3. Marquer les doublons (même session_id + même id_prod) avec is_duplicate = True
#    On garde toutes les lignes mais la colonne permet de les exclure des analyses.
#    La 1re occurrence (triée par date) est considérée comme valide (is_duplicate = False).
transactions = transactions.sort_values("date").reset_index(drop=True)
transactions["is_duplicate"] = transactions.duplicated(subset=["session_id", "id_prod"], keep="first")

nb_dups = transactions["is_duplicate"].sum()
print(f"  doublons session+produit : {nb_dups} (flagués, non supprimés)")

transactions_clean = transactions.copy()

print(f"transactions_clean         : {len(transactions_clean):,} lignes")
print(f"  dont is_duplicate = True : {nb_dups}")
print(f"  dont is_duplicate = False: {(~transactions_clean['is_duplicate']).sum():,}")

transactions_clean.to_csv(OUT_DIR / "transactions_clean.csv", index=False)
print(f"\nSauvegardé → {OUT_DIR}/transactions_clean.csv")
print("\nPour les analyses, filtrer avec : df[df['is_duplicate'] == False]")
