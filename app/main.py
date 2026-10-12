from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

model = joblib.load('models/logistecR_diabete.joblib')
# model = mlflow.sklearn.load_model('models:/DiabetesRiskPipeline/Production')

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
    risk = "Low Risk" if prediction == 1 else 'High Risk'

    return {
        'prediction' : int(prediction),
        'risk_level' : risk
    }
