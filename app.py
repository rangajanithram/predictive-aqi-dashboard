import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# 🎨 App Configuration
st.set_page_config(page_title="Bengaluru AQI Predictor", page_icon="🌍", layout="centered")

# 🧠 Load the Trained Model
# We use st.cache_resource so it only loads the model once, making the app super fast
@st.cache_resource
def load_model():
    return joblib.load('aqi_model.pkl')

model = load_model()

# 🖥️ Main UI
st.title("🌍 Bengaluru AQI Predictor")
st.markdown("""
This interactive dashboard uses a **Machine Learning Random Forest** model trained on real-world historical data to predict the Air Quality Index (AQI) based on weather conditions and time of day.
""")

st.divider()

# 🎛️ Sidebar for User Inputs
st.sidebar.header("⚙️ Adjust Parameters")
st.sidebar.write("Play with the sliders to see how weather affects pollution!")

temp = st.sidebar.slider("Temperature (°C)", min_value=15.0, max_value=45.0, value=28.0, step=0.5)
humidity = st.sidebar.slider("Humidity (%)", min_value=10.0, max_value=100.0, value=50.0, step=1.0)
wind = st.sidebar.slider("Wind Speed (km/h)", min_value=0.0, max_value=30.0, value=5.0, step=0.5)

hour = st.sidebar.slider("Hour of Day", min_value=0, max_value=23, value=datetime.now().hour)

# Map day numbers to actual names for the UI
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_name = st.sidebar.selectbox("Day of the Week", days_of_week)
day_number = days_of_week.index(day_name)

# 🚀 Prediction Logic
if st.button("🔮 Predict AQI", use_container_width=True):
    # Format the user's input exactly how the model expects it
    input_data = pd.DataFrame({
        'temperature': [temp],
        'humidity': [humidity],
        'wind_speed': [wind],
        'hour': [hour],
        'day_of_week': [day_number]
    })
    
    with st.spinner('Calculating complex environmental algorithms...'):
        prediction = model.predict(input_data)[0]
    
    st.subheader("Predicted Air Quality Index:")
    
    # 🚥 Color-Coded Results
    if prediction <= 50:
        st.success(f"## 🌿 {prediction:.0f} (Good)")
        st.write("Air quality is considered satisfactory, and air pollution poses little or no risk.")
    elif prediction <= 100:
        st.warning(f"## 😐 {prediction:.0f} (Moderate)")
        st.write("Air quality is acceptable; however, there may be a moderate health concern for a very small number of people.")
    elif prediction <= 150:
        st.error(f"## 😷 {prediction:.0f} (Unhealthy for Sensitive Groups)")
        st.write("Members of sensitive groups may experience health effects. The general public is not likely to be affected.")
    else:
        st.error(f"## ☠️ {prediction:.0f} (Unhealthy/Hazardous)")
        st.write("Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.")

st.divider()
st.caption("Built with Python, Scikit-Learn, and Streamlit. Data sourced from Open-Meteo.")