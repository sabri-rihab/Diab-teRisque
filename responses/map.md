# 🗺️ Roadmap — Étapes 6 & 7 : MLflow + App Web + Docker

> Basé sur l'analyse de `notebooks/classification.ipynb` et `notebooks/clustring.ipynb`
> Chaque étape est petite, précise, et dit exactement où agir.

---

## ═══════════════════════════════════════
## ÉTAPE 6 — MLFLOW TRACKING
## ═══════════════════════════════════════

---

### 🔷 BLOC A — Préparation MLflow

---

#### A.1 — Installer MLflow
**Où :** Terminal, depuis le dossier racine du projet
```bash
pip install mlflow
```
**Comprendre :** MLflow est une plateforme open-source pour tracker les expériences ML. Il enregistre tes paramètres, métriques, modèles et artefacts dans une base locale.

---

#### A.2 — Démarrer le serveur MLflow
**Où :** Terminal (nouveau terminal, garder ouvert)
```bash
mlflow server --host 127.0.0.1 --port 5000
```
**Comprendre :** Ce serveur = une interface web + une base de données locale.
- Ouvre `http://127.0.0.1:5000` dans ton navigateur → tu dois voir l'interface MLflow vide.
- Si tu fermes ce terminal, le serveur s'arrête.
- **Document à lire :** https://mlflow.org/docs/latest/tracking.html (section "Where Runs Are Recorded")

---

#### A.3 — Corriger la Cell 21 dans `classification.ipynb`
**Où :** `notebooks/classification.ipynb` → Cell 21 (la dernière)

**Supprimer ce code (Cell 21 actuelle) :**
```python
import mlflow

mlflow.set_tracking_uri('https:127.0.0.1:5000')   # ← ERREUR : https au lieu de http
mlflow.search_experiments("diabete_risk_prediction")  # ← ERREUR : mauvaise fonction
```

**Remplacer par :**
```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")   # http pas https
mlflow.set_experiment("diabete_risk_prediction")    # set_experiment pas search_experiments
```

**Comprendre :**
- `set_tracking_uri()` = dit à MLflow où envoyer les données (ton serveur local)
- `set_experiment()` = crée l'expérience si elle n'existe pas, ou la sélectionne si elle existe
- Exécute cette cellule → va sur `http://127.0.0.1:5000`, tu dois voir l'expérience apparaître

---

### 🔷 BLOC B — Tracer le run de Clustering

---

#### B.1 — Ouvrir `notebooks/clustring.ipynb`
**Où :** `notebooks/clustring.ipynb`

Ajoute une nouvelle cellule **tout en haut** du notebook (avant la Cell 1) :
```python
import mlflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("diabete_risk_prediction")
```

---

#### B.2 — Sauvegarder le scaler et le KMeans dans `models/`
**Où :** `notebooks/clustring.ipynb` → après la Cell 3 (après `df['risk_tier'] = ...`)

Ajoute une nouvelle cellule :
```python
import joblib

joblib.dump(scaler, '../models/scaler.joblib')
joblib.dump(kmeans, '../models/kmeans_k2.joblib')
print("Scaler et KMeans sauvegardés")
```
**Comprendre :** MLflow va logger ces fichiers comme "artefacts" (fichiers attachés au run). Il faut qu'ils existent d'abord sur le disque.

---

#### B.3 — Créer le run de clustering MLflow
**Où :** `notebooks/clustring.ipynb` → nouvelle cellule après B.2

```python
from sklearn.metrics import silhouette_score

sil_score = silhouette_score(x_scaled, kmeans.labels_)
inertia = kmeans.inertia_

with mlflow.start_run(run_name="kmeans_k2_clustering"):

    # Paramètres
    mlflow.log_param("k", 2)
    mlflow.log_param("scaler", "StandardScaler")
    mlflow.log_param("random_state", 42)

    # Métriques
    mlflow.log_metric("inertia", inertia)
    mlflow.log_metric("silhouette_score", sil_score)

    # Artefacts (les fichiers .joblib)
    mlflow.log_artifact("../models/scaler.joblib")
    mlflow.log_artifact("../models/kmeans_k2.joblib")

    print(f"Run terminé — Silhouette: {sil_score:.4f}, Inertia: {inertia:.2f}")
```

**Comprendre :**
- `log_param()` = enregistre un hyperparamètre (valeur fixe, pas calculée)
- `log_metric()` = enregistre une métrique numérique (résultat calculé)
- `log_artifact()` = attache un fichier au run (modèle, image, csv...)
- `with mlflow.start_run()` = ouvre un run, tout ce qui est dans le bloc est loggé dans ce run, le run se ferme automatiquement à la fin du `with`

**Vérification :** Va sur `http://127.0.0.1:5000` → expérience `diabete_risk_prediction` → tu dois voir un run `kmeans_k2_clustering` avec ses paramètres et métriques.

---

### 🔷 BLOC C — Tracer les runs de Classification

---

#### C.1 — Tracer la comparaison des modèles
**Où :** `notebooks/classification.ipynb` → Cell 12

**Situation actuelle :** La Cell 12 a le code de comparaison des modèles commenté. Les résultats sont dans une cellule markdown (Cell 13). C'est bien pour ton notebook, mais pour MLflow tu vas logger ces résultats manuellement depuis Cell 13.

Ajoute une **nouvelle cellule** après Cell 13 :

```python
# Résultats de la comparaison (tirés de ta Cell 13)
comparison_results = {
    "Logistic Regression": {"accuracy": 0.987, "precision": 0.9868, "recall": 0.9868, "f1": 0.9868},
    "SVM":                 {"accuracy": 0.9545, "precision": 0.96,   "recall": 0.9473, "f1": 0.9536},
    "Random Forest":       {"accuracy": 0.9220, "precision": 0.9444, "recall": 0.8947, "f1": 0.9189},
    "Gradient Boosting":   {"accuracy": 0.9220, "precision": 0.9324, "recall": 0.9078, "f1": 0.92},
    "KNN":                 {"accuracy": 0.9090, "precision": 0.9078, "recall": 0.9078, "f1": 0.9078},
    "Decision Tree":       {"accuracy": 0.8571, "precision": 0.8857, "recall": 0.8157, "f1": 0.8493},
}

for model_name, metrics in comparison_results.items():
    with mlflow.start_run(run_name=f"comparison_{model_name.replace(' ', '_')}"):
        mlflow.log_param("model", model_name)
        mlflow.log_param("scaling", "StandardScaler")
        mlflow.log_param("data_split", "80/20")
        mlflow.log_metrics(metrics)

print("Tous les runs de comparaison loggés")
```

---

#### C.2 — Tracer le run GridSearchCV
**Où :** `notebooks/classification.ipynb` → Cell 15

**Situation actuelle :** `grid.fit()` est commenté car tu ne veux plus le relancer (c'est long). Tu as les résultats en commentaire dans la cellule.

Ajoute une **nouvelle cellule** après Cell 15 :

```python
# Logger les résultats du GridSearch (déjà calculés)
with mlflow.start_run(run_name="gridsearch_logistic_regression"):
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("cv_folds", 5)
    mlflow.log_param("scoring", "accuracy")
    mlflow.log_param("param_grid_C", "[0.01, 0.1, 1, 10, 100]")
    mlflow.log_param("param_grid_penalty", "['l1', 'l2', None]")
    mlflow.log_param("param_grid_class_weight", "[None, 'balanced']")

    # Meilleurs paramètres trouvés
    mlflow.log_param("best_C", 1)
    mlflow.log_param("best_penalty", "l2")
    mlflow.log_param("best_class_weight", "None")
    mlflow.log_param("best_solver", "liblinear")
    mlflow.log_metric("best_cv_accuracy", 0.9983)

print("Run GridSearch loggé")
```

---

#### C.3 — Tracer le run du modèle final avec la confusion matrix en image
**Où :** `notebooks/classification.ipynb` → Cell 16

**Situation actuelle :** Cell 16 entraîne le modèle final et calcule les métriques.

Ajoute une **nouvelle cellule** après Cell 16 :

```python
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Générer et sauvegarder l'image de la confusion matrix
os.makedirs('../figures', exist_ok=True)

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Low Risk', 'High Risk'],
            yticklabels=['Low Risk', 'High Risk'], ax=ax)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title('Confusion Matrix — Logistic Regression Final')
plt.tight_layout()
plt.savefig('../figures/confusion_matrix_lr_final.png')
plt.close()

# 2. Logger dans MLflow
with mlflow.start_run(run_name="logistic_regression_final"):
    # Paramètres
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("C", 1)
    mlflow.log_param("penalty", "l2")
    mlflow.log_param("solver", "liblinear")
    mlflow.log_param("class_weight", "None")
    mlflow.log_param("scaling", "StandardScaler")
    mlflow.log_param("features", str(x.columns.tolist()))

    # Métriques
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("balanced_accuracy", balanced_acc)

    # Image de la confusion matrix
    mlflow.log_artifact('../figures/confusion_matrix_lr_final.png')

    print("Run final loggé avec confusion matrix")
```

**Comprendre :** `log_artifact()` avec une image PNG = MLflow va afficher cette image dans l'onglet "Artifacts" de ton run dans l'interface web.

---

### 🔷 BLOC D — Traçabilité et Reproductibilité

---

#### D.1 — Logger les versions des bibliothèques
**Où :** `notebooks/classification.ipynb` → ajouter dans la cellule du run final (C.3), dans le `with mlflow.start_run()` :

```python
import sklearn, pandas, numpy

mlflow.log_param("sklearn_version", sklearn.__version__)
mlflow.log_param("pandas_version", pandas.__version__)
mlflow.log_param("numpy_version", numpy.__version__)
```

---

#### D.2 — Logger la signature du dataset
**Où :** `notebooks/classification.ipynb` → dans le `with mlflow.start_run()` du run final :

```python
from mlflow.models import infer_signature
import pandas as pd

# Signature = structure des inputs et outputs du modèle
X_sample = pd.DataFrame(X_train[:5], columns=x.columns)
y_sample = pipline.predict(X_sample)
signature = infer_signature(X_sample, y_sample)
```
Puis passer `signature=signature` dans `log_model()` (voir Bloc E).

**Comprendre :** La signature documente exactement quelles colonnes le modèle attend en entrée et quel type de sortie il produit. Ça permet à quelqu'un d'autre de savoir comment utiliser ton modèle sans lire ton code.

---

### 🔷 BLOC E — MLflow Model Registry

---

#### E.1 — Logger le pipeline dans le Registry
**Où :** `notebooks/classification.ipynb` → remplacer le `joblib.dump` dans Cell 20 par MLflow

**Situation actuelle dans Cell 20 :**
```python
joblib.dump(pipline, '../models/logistecR_diabete.joblib')
```
**Laisser cette ligne** (garde le .joblib comme backup), et **ajouter en dessous** dans le `with mlflow.start_run()` de ton run final :

```python
# Logger le pipeline complet avec signature
mlflow.sklearn.log_model(
    sk_model=pipline,
    artifact_path="pipeline",
    signature=signature,
    registered_model_name="DiabetesRiskPipeline"   # ← nom dans le Registry
)
```

**Comprendre :**
- `log_model()` = sauvegarde ton pipeline complet dans MLflow (scaler + modèle ensemble)
- `registered_model_name` = crée une entrée dans le Model Registry sous ce nom
- Chaque fois que tu appelles `log_model()` avec le même nom, MLflow crée une nouvelle version (v1, v2, v3...)

---

#### E.2 — Passer la version en stage "Production"
**Où :** `notebooks/classification.ipynb` → nouvelle cellule après E.1

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Récupérer la dernière version enregistrée du modèle
versions = client.get_latest_versions("DiabetesRiskPipeline")
latest_version = versions[-1].version
print(f"Dernière version : {latest_version}")

# Passer en Production
client.transition_model_version_stage(
    name="DiabetesRiskPipeline",
    version=latest_version,
    stage="Production"
)
print(f"Version {latest_version} → Production ✅")
```

**Comprendre :** Le Model Registry a 3 stages : `Staging`, `Production`, `Archived`.
- `Production` = le modèle validé que l'application web va charger
- **Document à lire :** https://mlflow.org/docs/latest/model-registry.html

**Vérification :** Va sur `http://127.0.0.1:5000` → onglet "Models" → `DiabetesRiskPipeline` → tu dois voir la version avec le badge "Production".

---

## ═══════════════════════════════════════
## ÉTAPE 7 — APPLICATION WEB & DOCKER
## ═══════════════════════════════════════

---

### 🔷 BLOC F — Application Streamlit (Interface Praticien)

---

#### F.1 — Installer Streamlit et FastAPI
**Où :** Terminal
```bash
pip install streamlit fastapi uvicorn
```

---

#### F.2 — Créer le fichier FastAPI `app/main.py`
**Où :** Créer le fichier `app/main.py` (le dossier `app/` existe déjà mais est vide)

```python
from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.sklearn
import pandas as pd

app = FastAPI()

# Charger le modèle depuis le Registry MLflow au démarrage
mlflow.set_tracking_uri("http://mlflow:5000")   # "mlflow" = nom du service Docker
model = mlflow.sklearn.load_model("models:/DiabetesRiskPipeline/Production")

class PatientData(BaseModel):
    Pregnancies: float
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: float

@app.get("/")
def root():
    return {"status": "API DiabèteRisque opérationnelle"}

@app.post("/predict")
def predict(patient: PatientData):
    data = pd.DataFrame([patient.dict()])
    prediction = model.predict(data)[0]
    risk = "High Risk" if prediction == 1 else "Low Risk"
    return {
        "prediction": int(prediction),
        "risk_level": risk
    }
```

**Comprendre :**
- FastAPI = framework Python pour créer des APIs REST
- `BaseModel` de Pydantic = valide automatiquement les données reçues (si Glucose est absent → erreur automatique)
- Le modèle est chargé **une seule fois** au démarrage, pas à chaque requête
- **Document à lire :** https://fastapi.tiangolo.com/tutorial/first-steps/

---

#### F.3 — Créer l'interface Streamlit `app/streamlit_app.py`
**Où :** Créer le fichier `app/streamlit_app.py`

```python
import streamlit as st
import requests

st.set_page_config(page_title="Diabète Risk Predictor", page_icon="🩺")
st.title("🩺 Diabète Risk Predictor")
st.markdown("Remplissez les constantes cliniques du patient :")

col1, col2 = st.columns(2)

with col1:
    pregnancies = st.number_input("Grossesses", 0, 20, 1)
    glucose = st.number_input("Glucose (mg/dL)", 0, 300, 120)
    blood_pressure = st.number_input("Pression artérielle (mm Hg)", 0, 150, 70)
    skin_thickness = st.number_input("Épaisseur cutanée (mm)", 0, 100, 20)

with col2:
    insulin = st.number_input("Insuline (μU/ml)", 0, 900, 80)
    bmi = st.number_input("IMC (BMI)", 0.0, 70.0, 28.0)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.4)
    age = st.number_input("Âge", 1, 120, 30)

if st.button("🔍 Prédire le risque"):
    payload = {
        "Pregnancies": pregnancies, "Glucose": glucose,
        "BloodPressure": blood_pressure, "SkinThickness": skin_thickness,
        "Insulin": insulin, "BMI": bmi,
        "DiabetesPedigreeFunction": dpf, "Age": age
    }

    response = requests.post("http://fastapi:8000/predict", json=payload)
    result = response.json()

    if result["risk_level"] == "High Risk":
        st.error("🔴 RISQUE ÉLEVÉ de diabète")
        st.markdown("**Conseils :** Consultez un endocrinologue, réduisez les sucres rapides, activité physique régulière.")
    else:
        st.success("🟢 RISQUE FAIBLE de diabète")
        st.markdown("**Conseils :** Maintenir un mode de vie sain, contrôle annuel recommandé.")
```

**Comprendre :**
- Streamlit = framework Python pour créer des interfaces web sans HTML/CSS/JS
- `st.number_input()` = crée un champ numérique interactif
- `requests.post()` = envoie les données à ton API FastAPI et récupère la prédiction
- **Document à lire :** https://docs.streamlit.io/get-started

---

### 🔷 BLOC G — Docker & Docker Compose

---

#### G.1 — Comprendre Docker avant d'écrire les fichiers
**Document à lire (15 min) :** https://docs.docker.com/get-started/overview/

**Ce qu'il faut retenir :**
- `Dockerfile` = recette pour créer une image (comme une VM légère)
- `docker-compose.yml` = orchestre plusieurs conteneurs qui se parlent entre eux
- Chaque service (FastAPI, Streamlit, MLflow) = un conteneur séparé
- Les services communiquent via leur nom de service (ex: `http://mlflow:5000`)

---

#### G.2 — Créer `Dockerfile.fastapi`
**Où :** Créer à la racine du projet

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/main.py .
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

#### G.3 — Créer `Dockerfile.streamlit`
**Où :** Créer à la racine du projet

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

#### G.4 — Créer `requirements.txt`
**Où :** Créer à la racine du projet

```
pandas
numpy
scikit-learn
mlflow
fastapi
uvicorn
streamlit
requests
joblib
```

---

#### G.5 — Créer `docker-compose.yml`
**Où :** Créer à la racine du projet

```yaml
version: "3.8"

services:

  mlflow:
    image: python:3.11-slim
    command: >
      bash -c "pip install mlflow &&
               mlflow server --host 0.0.0.0 --port 5000
               --backend-store-uri sqlite:///mlflow.db
               --default-artifact-root /mlflow/artifacts"
    ports:
      - "5000:5000"
    volumes:
      - mlflow_data:/mlflow
    networks:
      - diabete_network

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    depends_on:
      - mlflow
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    networks:
      - diabete_network

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    depends_on:
      - fastapi
    networks:
      - diabete_network

volumes:
  mlflow_data:

networks:
  diabete_network:
    driver: bridge
```

**Comprendre :**
- `depends_on` = streamlit attend que fastapi soit démarré, fastapi attend mlflow
- `networks` = tous les services sont sur le même réseau interne → ils se voient par leur nom
- `volumes` = les données MLflow sont persistées même si le conteneur s'arrête
- **Document à lire :** https://docs.docker.com/compose/gettingstarted/

---

#### G.6 — Lancer et tester
**Où :** Terminal, depuis la racine du projet

```bash
# Construire et démarrer tous les services
docker-compose up --build

# Vérifier que tout tourne
docker-compose ps
```

**URLs à tester dans le navigateur :**
- MLflow UI : `http://localhost:5000`
- FastAPI docs : `http://localhost:8000/docs`
- Streamlit app : `http://localhost:8501`

---

### 🔷 BLOC H — DAG Airflow (Training/Retraining)

---

#### H.1 — Comprendre Airflow
**Document à lire (20 min) :** https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html

**Ce qu'il faut retenir :**
- Un DAG = un graphe de tâches qui s'exécutent dans un ordre défini
- Chaque tâche = un `PythonOperator` (fonction Python) ou `BashOperator`
- Airflow peut scheduler le DAG (ex: réentraîner chaque semaine)

---

#### H.2 — Créer le dossier DAGs
**Où :** Créer `dags/` à la racine du projet

---

#### H.3 — Créer `dags/retrain_dag.py`
**Où :** Créer le fichier `dags/retrain_dag.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import mlflow
import joblib

default_args = {
    'owner': 'diabete_project',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_data(**kwargs):
    df = pd.read_csv('/data/clustered_data.csv')
    kwargs['ti'].xcom_push(key='data_shape', value=str(df.shape))
    print(f"Données chargées : {df.shape}")

def preprocess(**kwargs):
    from sklearn.model_selection import train_test_split
    df = pd.read_csv('/data/clustered_data.csv')
    X = df.drop(columns=['risk_tier', 'cluster'])
    y = df['cluster']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Préprocessing terminé")

def retrain(**kwargs):
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score, accuracy_score
    df = pd.read_csv('/data/clustered_data.csv')
    X = df.drop(columns=['risk_tier', 'cluster'])
    y = df['cluster']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(C=1, penalty='l2', solver='liblinear', random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("diabete_risk_prediction")

    with mlflow.start_run(run_name="airflow_retrain"):
        mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
        mlflow.log_metric("f1_score", f1_score(y_test, y_pred))
        mlflow.sklearn.log_model(pipeline, "pipeline",
                                 registered_model_name="DiabetesRiskPipeline")
    print("Réentraînement terminé et loggé")

with DAG(
    dag_id='diabete_retrain_pipeline',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='@weekly',   # réentraîne chaque semaine
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id='extract_data', python_callable=extract_data)
    t2 = PythonOperator(task_id='preprocess', python_callable=preprocess)
    t3 = PythonOperator(task_id='retrain', python_callable=retrain)

    t1 >> t2 >> t3   # ordre d'exécution
```

**Comprendre :**
- `>>` = définit l'ordre (t1 s'exécute, puis t2, puis t3)
- `xcom_push/pull` = pour passer des données entre tâches dans Airflow
- `schedule_interval='@weekly'` = Airflow exécutera ce DAG automatiquement chaque semaine

---

#### H.4 — Ajouter Airflow dans `docker-compose.yml`
**Où :** `docker-compose.yml` → dans la section `services`, ajouter :

```yaml
  airflow:
    image: apache/airflow:2.8.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////airflow/airflow.db
    volumes:
      - ./dags:/opt/airflow/dags
      - airflow_data:/airflow
    ports:
      - "8080:8080"
    command: >
      bash -c "airflow db init &&
               airflow users create --username admin --password admin
               --firstname Admin --lastname Admin --role Admin --email admin@example.com &&
               airflow webserver & airflow scheduler"
    networks:
      - diabete_network
```

Et dans `volumes:` ajouter :
```yaml
  airflow_data:
```

**URL Airflow :** `http://localhost:8080` (login: admin / admin)

---

## ═══════════════════════════════════════
## CHECKLIST FINALE
## ═══════════════════════════════════════

### Structure finale du projet

```
DiabèteRisque/
├── data/
│   ├── dataset.csv
│   ├── cleaned_data.csv
│   ├── clustered_data.csv
│   └── scaled_data.csv
├── notebooks/
│   ├── clustring.ipynb        ← Ajouter Blocs A, B
│   └── classification.ipynb  ← Ajouter Blocs A, C, D, E
├── models/
│   ├── scaler.joblib
│   ├── kmeans_k2.joblib
│   └── logistecR_diabete.joblib
├── app/
│   ├── main.py                ← Bloc F.2
│   └── streamlit_app.py       ← Bloc F.3
├── dags/
│   └── retrain_dag.py         ← Bloc H.3
├── figures/
│   └── confusion_matrix_lr_final.png
├── responses/
│   ├── diagnostic_clustering.md
│   └── map.md
├── Dockerfile.fastapi          ← Bloc G.2
├── Dockerfile.streamlit        ← Bloc G.3
├── docker-compose.yml          ← Blocs G.5 + H.4
├── requirements.txt            ← Bloc G.4
└── projet_ia_diabete.md
```

### Cases à cocher dans l'ordre

- [ ] A.1 — `pip install mlflow`
- [ ] A.2 — Démarrer le serveur MLflow et ouvrir l'interface
- [ ] A.3 — Corriger la Cell 21 de `classification.ipynb`
- [ ] B.1 — Ajouter setup MLflow en haut de `clustring.ipynb`
- [ ] B.2 — Sauvegarder scaler et kmeans dans `models/`
- [ ] B.3 — Logger le run de clustering dans MLflow
- [ ] C.1 — Logger la comparaison des modèles
- [ ] C.2 — Logger le run GridSearchCV
- [ ] C.3 — Logger le run final + confusion matrix en image
- [ ] D.1 — Logger les versions des librairies
- [ ] D.2 — Logger la signature du dataset
- [ ] E.1 — Logger le pipeline dans le Model Registry
- [ ] E.2 — Passer la version en "Production"
- [ ] F.1 — `pip install streamlit fastapi uvicorn`
- [ ] F.2 — Créer `app/main.py` (FastAPI)
- [ ] F.3 — Créer `app/streamlit_app.py`
- [ ] G.1 — Lire la doc Docker (15 min)
- [ ] G.2 — Créer `Dockerfile.fastapi`
- [ ] G.3 — Créer `Dockerfile.streamlit`
- [ ] G.4 — Créer `requirements.txt`
- [ ] G.5 — Créer `docker-compose.yml`
- [ ] G.6 — `docker-compose up --build` et tester les 3 URLs
- [ ] H.1 — Lire la doc Airflow DAGs (20 min)
- [ ] H.2 — Créer le dossier `dags/`
- [ ] H.3 — Créer `dags/retrain_dag.py`
- [ ] H.4 — Ajouter Airflow dans `docker-compose.yml`
