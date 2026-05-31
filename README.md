# Segmentation clients e-commerce — La Page

> Segmenter 2 500 clients d'une librairie en ligne en profils RFM et tester statistiquement les différences de comportement d'achat.

**Stack** · Python · Pandas · Matplotlib · Seaborn · SciPy · Jupyter

---

## Contexte

La Page est une librairie en ligne souhaitant mieux comprendre ses clients pour affiner sa stratégie marketing. À partir de 3 tables (clients, produits, transactions), ce projet produit une segmentation RFM complète, des analyses statistiques et des visualisations exploratoires.

## Méthodologie

1. **Nettoyage des données** — déduplication, valeurs manquantes, cohérence des 3 tables
2. **Analyse exploratoire** — CA mensuel, top produits, comportement nouveaux vs récurrents
3. **Segmentation RFM** — scoring Récence / Fréquence / Montant sur 2 500 clients
4. **Tests statistiques** — Mann-Whitney, Kruskal-Wallis, Chi² pour valider les différences entre segments

## Résultats clés

- **5 profils clients** identifiés avec CA, fréquence et ancienneté distincts
- **Loi de Pareto confirmée** : 20% des produits génèrent 80% du CA
- **Différence H/F significative** sur le panier moyen (Mann-Whitney, p < 0.05)
- **82 visualisations** produites couvrant l'ensemble des dimensions d'analyse

## Structure du repo

```
DAN-P6-donnees/     données brutes (clients, produits, transactions)
data_clean/         données nettoyées (CSV)
  customers_clean.csv
  products_clean.csv
  transactions_clean.csv
figures/            82 visualisations PNG générées
nettoyage.py        pipeline de nettoyage et consolidation
analyse.py          analyses exploratoires et RFM
analyse_nouveaux_clients.py  focus cohortes de rétention
verification.py     tests de qualité des données
projet9_lapage.ipynb  notebook d'analyse complet
```

## Lancer le projet

```bash
uv sync
python nettoyage.py     # produit data_clean/
python analyse.py       # produit figures/
```

---

*Formation Data Analyst — OpenClassrooms × ENSAE · Projet 8*
