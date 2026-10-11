from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.sklearn
import pandas as pd

app = FastAPI()

#importer le model enregitrer depuis MLflow
# mlflow.set_tracking_uri('http://127.0.0.1:5000') #mlflow smit service docker
mlflow.set_tracking_uri('http://mlflow:5000') #mlflow smit service docker
model = mlflow.sklearn.load_model('models:/DiabetesRiskPipeline/Production')


class PatientData(BaseModel):
    Pregnancies : int
    Glucose : float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: float

@app.get('/')
def root():
    return {"status": "API DiabèteRisque opérationnelle"}

@app.post('/predict')
def predict(patient: PatientData):
    data = pd.DataFrame([patient.dict()])
    prediction = model.predict(data)[0]
    risk = "High Risk" if prediction == 1 else 'Low Risk'

    return {
        'prediction' : int(prediction),
        'risk_level' : risk
    }
