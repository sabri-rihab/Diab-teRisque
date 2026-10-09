# Correction — Étape 7 (F.2 → G.5)

---

## 1. `app/main.py` — F.2

### Problème 1 : Type de `Pregnancies`
Le map dit `Pregnancies: float`, tu as mis `int`. Ça peut causer des erreurs de validation Pydantic si la valeur reçue est un float.

**Supprimer :**
```python
Pregnancies : int
```
**Ajouter à la place :**
```python
Pregnancies : float
```

---

### Problème 2 : Typo dans le niveau de risque
Tu as écrit `"Hight Risk"` au lieu de `"High Risk"`. Le Streamlit compare avec `"High Risk"` → la condition ne sera jamais vraie.

**Supprimer :**
```python
risk = "Hight Risk" if prediction == 1 else 'Low Risk'
```
**Ajouter à la place :**
```python
risk = "High Risk" if prediction == 1 else "Low Risk"
```

---

## 2. `app/streamlit.py` → doit être renommé `app/streamlit_app.py` — F.3

### Problème : Mauvais nom de fichier
Ton fichier s'appelle `streamlit.py` mais `Dockerfile.streamlit` (que tu vas créer) et le map disent `streamlit_app.py`. Le CMD dans le Dockerfile sera `streamlit run streamlit_app.py` → fichier introuvable → crash au démarrage.

**Action :** Renomme le fichier `app/streamlit.py` → `app/streamlit_app.py`.

---

### Problème 2 : Valeur par défaut manquante pour `pregnancies`
Le map met `1` comme valeur par défaut. Sans valeur par défaut, Streamlit met `0` ce qui est moins logique cliniquement.

**Supprimer :**
```python
pregnancies = st.number_input('Grossesses', 0, 20)
```
**Ajouter à la place :**
```python
pregnancies = st.number_input('Grossesses', 0, 20, 1)
```

---

## 3. Dockerfiles — G.2 et G.3

### Problème : Tu as un seul `Dockerfile` au lieu de `Dockerfile.fastapi` et `Dockerfile.streamlit`
Le `docker-compose.yml` référence `dockerfile: Dockerfile.fastapi` et `dockerfile: Dockerfile.streamlit` → Docker ne les trouve pas → build échoue.

Ton `Dockerfile` actuel correspond à FastAPI. Il faut :
- Le renommer en `Dockerfile.fastapi`
- Créer `Dockerfile.streamlit`
- Les deux doivent utiliser `python:3.11-slim` pas `python:3.14` (cette image n'existe pas sur Docker Hub)

**Dans `Dockerfile` (à renommer en `Dockerfile.fastapi`) :**

**Supprimer :**
```dockerfile
FROM python:3.14
```
**Ajouter à la place :**
```dockerfile
FROM python:3.11-slim
```

**Créer `Dockerfile.streamlit` à la racine du projet avec ce contenu :**
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

## 4. `docker-compose.yml` — G.5

### Problème : Image MLflow utilise `python:3.14`
`python:3.14` n'existe pas sur Docker Hub → le service MLflow ne démarrera pas.

**Supprimer :**
```yaml
  mlflow:
    image: python:3.14
```
**Ajouter à la place :**
```yaml
  mlflow:
    image: python:3.11-slim
```

---

## 5. `requirements.txt` — G.4

### Problème : Versions pinnées inexistantes
Les versions que tu as mises n'existent pas (`pandas==3.0.5`, `numpy==2.5.3`, `scikit-learn==1.9.1`, etc.). Le `pip install` dans Docker va échouer.

Le map dit de mettre les noms sans versions. 

**Supprimer tout le contenu du fichier et remplacer par :**
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

## Résumé des actions

| Fichier | Action |
|---|---|
| `app/main.py` | Changer `int` → `float` pour Pregnancies, corriger `"Hight Risk"` → `"High Risk"` |
| `app/streamlit.py` | Renommer en `streamlit_app.py`, ajouter valeur par défaut `1` à pregnancies |
| `Dockerfile` | Renommer en `Dockerfile.fastapi`, changer `python:3.14` → `python:3.11-slim` |
| `Dockerfile.streamlit` | Créer ce fichier (contenu ci-dessus) |
| `docker-compose.yml` | Changer `python:3.14` → `python:3.11-slim` dans le service mlflow |
| `requirements.txt` | Supprimer les versions pinnées, garder juste les noms |
