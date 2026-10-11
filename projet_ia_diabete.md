# Projet IA --- Analyse et Prédiction du Risque de Diabète

## Contexte du projet

Vous êtes développeur IA junior au sein d'un laboratoire biomédical.
Votre mission consiste à concevoir un système intelligent capable
d'analyser des données cliniques (**Glucose, Blood Pressure, Skin
Thickness, Insulin, BMI, Diabetes Pedigree Function et Age**) afin
d'identifier des profils de patients et d'estimer leur risque de
diabète.

Le projet comprend deux volets : **clustering non supervisé** pour
identifier des profils similaires, puis **classification supervisée** à
partir des groupes obtenus.

À partir d'un jeu de données historiques comprenant les résultats de
tests déjà réalisés par des patients au sein du laboratoire, vous serez
chargé(e) de :

## Étape 1 --- Chargement et analyse exploratoire des données (EDA)

-   Importer les données à l'aide de **pandas**.
-   Comprendre la structure générale du jeu de données :
    -   types des variables ;
    -   dimensions ;
    -   aperçu des données.
-   Identifier les valeurs manquantes et les doublons.
-   Analyser la distribution des variables numériques.

## Étape 2 --- Prétraitement des données : gestion des valeurs manquantes et aberrantes

-   Identifier et traiter les valeurs manquantes dans le jeu de données
    si elles existent.
-   Utiliser des techniques statistiques (ex. : boîte à moustaches,
    **Z-score**, **IQR**) pour détecter les outliers.
-   Gérer les lignes contenant des valeurs aberrantes dans les colonnes
    pertinentes.
-   Étudier les relations entre les variables.
-   Sélectionner les variables présentant la plus grande variabilité.
-   Visualiser les relations entre les variables via des outils
    graphiques comme le **pairplot**.
-   Appliquer la technique appropriée pour normaliser ou standardiser
    les échelles des variables numériques.

## Étape 3 --- Entraînement des modèles de clustering avec K-Means

-   Déterminer la valeur optimale de **k** via :
    -   la méthode du coude ;
    -   le score de silhouette.
-   Visualiser la courbe d'inertie et la courbe de silhouette pour
    appuyer le choix de **k**.
-   Entraîner un modèle **K-Means** avec le nombre de clusters choisi.
-   Ajouter une colonne `Cluster` au dataset indiquant le groupe assigné
    à chaque individu.
-   Visualiser la répartition des observations par cluster et
    interpréter les résultats.

## Étape 4 --- Analyse des clusters

-   Calculer les moyennes des caractéristiques au sein de chaque
    cluster.
-   Compter le nombre d'observations par groupe.
-   Le cluster dont les moyennes des variables **Glucose (\>126)**,
    **BMI (\>30)** et **Diabetes Pedigree Function (\>0,5)** dépassent
    les seuils critiques peut être interprété comme à haut risque de
    diabète.
-   Ajouter une colonne `risk_category` basée sur le numéro de cluster :
    -   si `1` → risque élevé ;
    -   si `0` → risque faible.

## Étape 5 --- Classification supervisée et évaluation des modèles

-   Définir la variable cible `y` à partir de la colonne `Cluster`.
-   Définir `X` à partir des variables sélectionnées.
-   Diviser les données en ensemble d'entraînement et de test à l'aide
    de `train_test_split`.
-   Gérer le déséquilibre des classes avec des techniques de
    sur-échantillonnage ou sous-échantillonnage :
    -   `RandomOverSampler` ;
    -   `RandomUnderSampler` via `imblearn`.
-   Entraîner et comparer au minimum **3 modèles de classification** en
    utilisant les mêmes données d'entraînement et de test.
-   Utiliser des métriques appropriées à la classification telles que :
    -   matrice de confusion ;
    -   précision ;
    -   rappel ;
    -   F1-score.
-   Utiliser des techniques comme `GridSearchCV` ou `RandomizedSearchCV`
    pour affiner les hyperparamètres des modèles et améliorer leurs
    performances.
-   Comparer les performances des différents modèles.
-   Choisir le modèle le plus performant.
-   Construire un **Pipeline** intégrant le prétraitement des données et
    le modèle final, puis sauvegarder l'ensemble dans un fichier (`.pkl`
    ou `.joblib`).

## Étape 6 --- Tracking des expériences et registre avec MLflow

-   Démarrer et configurer un serveur de tracking **MLflow** et créer
    une expérience dédiée.
-   Tracer le run de clustering :
    -   paramètre `k` ;
    -   inertie ;
    -   score de silhouette ;
    -   paramètres du scaler ;
    -   artefacts : fichiers du modèle K-Means et du scaler (`.pkl` /
        `.joblib`).
-   Tracer chaque run de classification :
    -   hyperparamètres explorés ;
    -   métriques de performance : F1-score, rappel, précision, accuracy
        ;
    -   matrice de confusion sous forme d'image en artefact.
-   Assurer la **traçabilité et la reproductibilité** :
    -   loguer la liste exacte des features utilisées ;
    -   loguer les versions des bibliothèques ;
    -   loguer la signature du dataset.
-   Enregistrer la pipeline dans le **MLflow Model Registry** et
    effectuer la transition de la version validée vers le stage
    **Production**.

## Étape 7 --- Application Web métier & orchestration du pipeline

### Interface praticien --- Inférence

-   Créer un formulaire interactif permettant la saisie des constantes
    cliniques d'un patient.
-   Charger le modèle directement depuis le **Model Registry de
    MLflow**.
-   Exposer un endpoint `/predict` qui charge le pipeline complet
    (**Scaler + Modèle Production MLflow**).
-   Afficher le niveau de risque prédit accompagné d'un indicateur
    visuel clair :
    -   badge rouge pour **Risque Élevé** ;
    -   badge vert pour **Risque Faible**.
-   Afficher des conseils de suivi.

### DAG --- Training / Retraining

Le DAG doit :

-   extraire les données ;
-   appliquer le préprocessing ;
-   réentraîner les classifieurs ;
-   mettre à jour le Model Registry avec le nouveau pipeline.

### Conteneurisation et orchestration

-   Rédiger les `Dockerfile`.
-   Créer un fichier `docker-compose.yml` orchestrant les services :
    -   FastAPI ;
    -   Streamlit ;
    -   MLflow Server ;
    -   Airflow.

# Modalités pédagogiques

-   **Travail :** Individuel.
-   **Durée de travail :** 10 jours.
-   **Période :** Du 28/09/2026 au 09/10/2026 avant minuit.

# Modalités d'évaluation

Durée : **30 minutes**, organisée comme suit :

1.  **Démonstration --- \~10 minutes**

    -   Démontrer rapidement le contenu et les fonctionnalités de la
        solution.

2.  **Code Review / Culture du projet --- 10 minutes**

3.  **Mise en situation --- 10 minutes**

# Livrables

Un dépôt Git organisé et documenté, contenant :

-   le notebook complet et commenté (`.ipynb`) ;
-   le code source structuré :
    -   `data/`
    -   `notebooks/`
    -   `src/`
    -   `models/`
    -   `app/`
-   le fichier `requirements.txt` ;
-   le modèle entraîné et le scaler sérialisés (`.pkl` / `.joblib`) ;
-   l'application Streamlit ;
-   le serveur & registre MLflow ;
-   les DAGs Apache Airflow ;
-   un `README` clair contenant :
    -   description du projet ;
    -   dataset ;
    -   démarche ;
    -   résultats et métriques ;
    -   instructions d'installation et d'exécution ;
    -   captures d'écran de l'application.
-   le lien vers Jira.

# Critères de performance

## 1. Qualité des modèles

### Précision des prédictions

Les modèles doivent atteindre des métriques de performance élevées sur
l'ensemble de test.

### Tuning des hyperparamètres

Optimiser les hyperparamètres afin d'améliorer les performances du
modèle.

### Robustesse et généralisation

Les modèles doivent être robustes et bien généraliser sur des données
inédites.

## 2. Documentation et reproductibilité

### Qualité de la documentation

Fournir une documentation complète et claire décrivant chaque étape du
projet.

## 3. Efficacité du code

### Lisibilité et organisation

Produire un code clair, bien structuré et facile à maintenir.

### Performance computationnelle

Optimiser l'efficacité du code afin de réduire le temps d'exécution et
l'utilisation des ressources.

### Gestion des erreurs et robustesse

Produire un code robuste capable de gérer les erreurs et les inputs
incorrects.
