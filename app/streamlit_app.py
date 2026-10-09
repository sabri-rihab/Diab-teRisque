import streamlit_app as st
import requests


st.set_page_config(page_title='Diabète Risk Predictor', page_icon='^^')
st.title('Diabète Risk Predictor')
st.markdown('Remplissez les constantes cliniques du patient :')

col1, col2 = st.columns(2)

with col1 :
    pregnancies = st.number_input('Grossesses', 0, 20, 0)
    glucose = st.number_input("Glucose (mg/dL)", 0, 300, 120)
    blood_pressure = st.number_input("Pression artérielle (mm Hg)", 0, 150, 70)
    skin_thickness = st.number_input("Épaisseur cutanée (mm)", 0, 100, 20)

with col2:
    insulin = st.number_input("Insuline (μU/ml)", 0, 900, 80)
    bmi = st.number_input("IMC (BMI)", 0.0, 70.0, 28.0)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.4)
    age = st.number_input("Âge", 1, 120, 30)

if st.button('Prédire le risque'):
    payload = {
        "Pregnancies": pregnancies, 
        "Glucose": glucose,
        "BloodPressure": blood_pressure, 
        "SkinThickness": skin_thickness,
        "Insulin": insulin, 
        "BMI": bmi,
        "DiabetesPedigreeFunction": dpf, 
        "Age": age
    }

    # response = requests.post('http://127.0.0.1:8000/predict', json=payload)
    response = requests.post('http://fastapi:8000/predict', json=payload)
    result = response.json()

    if result['risk_level'] == 'High Risk':
        st.error("🔴 RISQUE ÉLEVÉ de diabète")
        st.markdown("**Conseils :** Consultez un endocrinologue")

    else :
        st.success("🟢 RISQUE FAIBLE de diabète")
        st.markdown("**Conseils :** Maintenir un mode de vie sain")