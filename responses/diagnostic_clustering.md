# Diagnostic & Plan d'action — Clustering Diabète

## 1. Problème racine : les données contiennent des zéros impossibles médicalement

C'est **le vrai problème** qui bloque tout. Avant même de parler de K-Means ou silhouette, regarde ça :

| Colonne | Zéros | % |
|---|---|---|
| Glucose | 5 | 0.7% |
| BloodPressure | 35 | 4.6% |
| **SkinThickness** | **227** | **29.6%** |
| **Insulin** | **374** | **48.7%** |
| BMI | 11 | 1.4% |

**Un humain vivant ne peut pas avoir Glucose=0, Insulin=0 ou BMI=0.**  
Ce sont des **valeurs manquantes déguisées en 0** — c'est la réalité de ce dataset (Pima Indians Diabetes).  
Ton `cleaned_data.csv` est **identique au dataset original** : le nettoyage n'a PAS traité ces faux zéros.  
C'est pour ça que ton clustering est mauvais.

---

## 2. Pourquoi ton silhouette score est bas (0.21–0.5)

| Symptôme | Cause |
|---|---|
| K-Means silhouette ~0.21 | Clusters pas du tout séparés dans l'espace |
| HDBSCAN silhouette ~0.5 mais visuellement flou | HDBSCAN force des clusters même dans du bruit |
| PCA/UMAP ne montrent pas de groupes clairs | Les features sont peu corrélées entre elles (max corr = 0.54 Pregnancies-Age) |

Les corrélations sont faibles → les données ne forment naturellement **pas de clusters bien séparés** dans l'espace 8D.  
C'est **normal pour ce dataset** : c'est un dataset de classification (Outcome 0/1) pas un dataset de clustering naturel.

> **Note :** Ce dataset est conçu pour la classification supervisée. Le clustering est artificiellement imposé par le brief. Ce n'est pas un défaut de ta méthode — c'est la nature du dataset.

---

## 3. Ce que tu aurais dû faire à l'Étape 2 (nettoyage)

### Remplacer les faux zéros par NaN, puis imputer

```python
cols_with_impossible_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
df[cols_with_impossible_zeros] = df[cols_with_impossible_zeros].replace(0, np.nan)

# Option 1 : médiane (robuste aux outliers)
df.fillna(df.median(), inplace=True)

# Option 2 : médiane par groupe (meilleure)
# df[col] = df.groupby('Outcome')[col].transform(lambda x: x.fillna(x.median()))
```

> **Attention :** Sans cette correction, Insulin a 48.7% de zéros. Ces zéros tirent les clusters vers des zones artificielles de l'espace.

### Normalisation correcte

Après imputation, utilise `StandardScaler` ou `RobustScaler` (préférable car tu as des outliers).

```python
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
X_scaled = scaler.fit_transform(df.drop(columns=['Unnamed: 0']))
```

---

## 4. Plan d'action concret — Ce que tu dois faire maintenant

### Étape A : Corriger le nettoyage (src/cleaning.py)

1. Remplacer les 0 impossibles par `NaN`
2. Imputer par la médiane
3. Supprimer `Unnamed: 0`
4. Appliquer `RobustScaler`
5. Sauvegarder le dataset propre

### Étape B : Relancer le clustering correctement

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Elbow + Silhouette pour k=2 à 8
inertias = []
silhouettes = []
K_range = range(2, 9)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))

# Visualiser les deux courbes
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(K_range, inertias, 'bo-')
axes[0].set_title('Méthode du Coude (Elbow)')
axes[0].set_xlabel('k')
axes[0].set_ylabel('Inertie')

axes[1].plot(K_range, silhouettes, 'ro-')
axes[1].set_title('Score de Silhouette')
axes[1].set_xlabel('k')
axes[1].set_ylabel('Score')
plt.show()
```

### Étape C : Choisir k=2 et l'assumer

Pour ce dataset, **k=2 est le bon choix** car :
- Il correspond au sens métier : Diabétique / Non-diabétique
- Le brief (Étape 4) parle de `risk_category` : 0 (faible) ou 1 (élevé)
- Les données ont naturellement 2 groupes cliniques

> **Note :** Un silhouette score de 0.2–0.3 est **acceptable** pour des données médicales réelles. Ce n'est pas un projet de clustering de données synthétiques — les patients ne sont pas parfaitement séparables.

### Étape D : Visualisation correcte

Pour PCA, tu n'as besoin que de la visualisation des clusters **après K-Means** :

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='RdYlGn', alpha=0.7)
plt.colorbar(scatter)
plt.title(f'K-Means k=2 — Visualisation PCA\n(Variance expliquée: {pca.explained_variance_ratio_.sum():.1%})')
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
plt.show()
```

> **Astuce :** Si PCA n'explique que ~40-50% de la variance, les clusters vont quand même sembler chevauchés en 2D — c'est **normal**. Ajoute la variance expliquée dans le titre pour le justifier.

---

## 5. Ce que tes résultats te disent (interprétation)

| Résultat | Interprétation |
|---|---|
| Silhouette K-Means k=2 : 0.21 | Clusters faiblement séparés — attendu sur données médicales réelles |
| Silhouette K-Means k=3 : 0.20 | k=3 n'apporte rien de plus → choisir k=2 |
| HDBSCAN score 0.5 | HDBSCAN trouve des structures locales, pas globales ; ne pas utiliser pour ce brief |
| PCA/UMAP chevauchement | Les features ne suffisent pas à séparer parfaitement les patients en 2D — normal |

---

## 6. Résumé de la démarche à corriger

```
Étape 1 ✅  EDA correcte
Étape 2 ⚠️  Nettoyage INCOMPLET : faux zéros non traités → À corriger
Étape 3 🔄  K-Means à relancer après correction étape 2
             → Choisir k=2
             → Silhouette ~0.2 est acceptable
             → Justifier visuellement avec elbow + silhouette curve
```

---

## 7. Code complet corrigé pour cleaning.py

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
import joblib

df = pd.read_csv('data/dataset.csv')

# Drop index column
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# Traiter les zéros impossibles médicalement
cols_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
df[cols_zeros] = df[cols_zeros].replace(0, np.nan)
print("Valeurs manquantes après correction des zéros:")
print(df.isna().sum())

# Imputation par la médiane
df.fillna(df.median(numeric_only=True), inplace=True)

# Vérification
print("\nPas de valeurs nulles restantes:", df.isna().sum().sum() == 0)

# Standardisation robuste
features = df.columns.tolist()
scaler = RobustScaler()
X_scaled = scaler.fit_transform(df)
df_scaled = pd.DataFrame(X_scaled, columns=features)

# Sauvegarde
df.to_csv('data/cleaned_data.csv', index=False)
df_scaled.to_csv('data/scaled_data.csv', index=False)
joblib.dump(scaler, 'models/scaler.joblib')

print("\nFichiers sauvegardés: cleaned_data.csv, scaled_data.csv, scaler.joblib")
```
