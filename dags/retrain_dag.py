from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import mlflow
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score

default_args = {
    'owner' : 'diabete_project',
    'retries' : 1,
    'retry_delay' : timedelta(minutes=5)
}

def extract_data(**kwargs):
    df = pd.read_csv('data/clustered_data.csv')
    kwargs['ti'].xcom_push(
        key='data_shape', 
        value=str(df.shape)
        )
    print(f'données chargées : {df.shape}')

def preprocess(**kwarg):
    df = pd.read_csv('data/clustered_data.csv')
    X = df.drop(columns=['cluster', 'risk_tier'])
    y = df['cluster']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  
    print('split train/test done!!') 

def retrain(**kwarg):
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

    t1 >> t2 >> t3