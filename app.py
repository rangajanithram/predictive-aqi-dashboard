import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# 🎨 App Configuration
st.set_page_config(page_title="India AQI Predictor", page_icon="🌍", layout="wide")

# 🧠 Load the Trained Model & Column Structure
@st.cache_resource
def load_artifacts():
    model = joblib.load('aqi_model.pkl')
    columns = joblib.load('model_columns.pkl')
    return model, columns

model, expected_columns = load_artifacts()

st.title("🌍 All-India AQI Predictor")

tab1, tab2 = st.tabs(["🔮 Live Predictor", "📊 Behind the ML Model"])

# ==========================================
# TAB 1: THE PREDICTOR (For Regular Users)
# ==========================================
with tab1:
    st.markdown("Predict the next hour's Air Quality Index based on current weather and recent pollution trends.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📍 Location & Time")
        cities = ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai", "Hyderabad"]
        selected_city = st.selectbox("Select City", cities)
        
        hour = st.slider("Hour of Day", min_value=0, max_value=23, value=datetime.now().hour)
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_name = st.selectbox("Day of the Week", days_of_week)
        day_number = days_of_week.index(day_name)

    with col2:
        st.subheader("🌤️ Current Weather")
        temp = st.slider("Temperature (°C)", min_value=10.0, max_value=50.0, value=28.0, step=0.5)
        humidity = st.slider("Humidity (%)", min_value=10.0, max_value=100.0, value=50.0, step=1.0)
        wind = st.slider("Wind Speed (km/h)", min_value=0.0, max_value=30.0, value=5.0, step=0.5)

    with col3:
        st.subheader("🏭 Recent Pollution")
        st.caption("How bad was the air 1 and 2 hours ago?")
        aqi_1 = st.slider("AQI (1 Hour Ago)", min_value=0, max_value=500, value=100)
        aqi_2 = st.slider("AQI (2 Hours Ago)", min_value=0, max_value=500, value=95)

    st.divider()

    # 🚀 Prediction Logic
    if st.button("🔮 Predict Next Hour's AQI", use_container_width=True):
        # 1. Gather inputs
        input_dict = {
            'temperature': [temp], 'humidity': [humidity], 'wind_speed': [wind],
            'hour': [hour], 'day_of_week': [day_number],
            'aqi_1_hour_ago': [aqi_1], 'aqi_2_hours_ago': [aqi_2]
        }
        input_df = pd.DataFrame(input_dict)
        
        # 2. Apply One-Hot Encoding for the selected city manually
        for city in cities:
            input_df[f'city_{city}'] = 1 if city == selected_city else 0
            
        # 3. Align with the exact columns the model was trained on!
        # This prevents crashes if the columns get out of order
        input_df = input_df.reindex(columns=expected_columns, fill_value=0)
        
        with st.spinner('Analyzing environmental data...'):
            prediction = model.predict(input_df)[0]
        
        st.subheader(f"Predicted Next-Hour AQI for {selected_city}:")
        
        if prediction <= 50:
            st.success(f"## 🌿 {prediction:.0f} (Good)")
        elif prediction <= 100:
            st.warning(f"## 😐 {prediction:.0f} (Moderate)")
        elif prediction <= 150:
            st.error(f"## 😷 {prediction:.0f} (Unhealthy for Sensitive Groups)")
        else:
            st.error(f"## ☠️ {prediction:.0f} (Unhealthy/Hazardous)")

# ==========================================
# TAB 2: THE DATA SCIENCE (For Recruiters)
# ==========================================
with tab2:
    st.header("🧠 Advanced Model Architecture")
    st.markdown("""
    This application utilizes an advanced **Random Forest Regressor** trained on a dataset of **10,600+ rows** of historical environmental data spanning India's major metropolitan anchor cities.
    """)
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Algorithm", value="Random Forest")
    col2.metric(label="Mean Absolute Error", value="1.91 AQI")
    col3.metric(label="R² Score", value="0.99")
    
    st.caption("*High accuracy achieved via engineering Time-Series 'Lag Features', allowing the model to weigh recent pollution baselines against incoming meteorological shifts.*")
    
    st.divider()
    st.subheader("📊 Feature Importance")
    
    # Dynamically extract feature importance
    importances = model.feature_importances_
    importance_df = pd.DataFrame({'Impact on Prediction': importances}, index=expected_columns).sort_values(by='Impact on Prediction', ascending=True)
    
    # Filter out the city dummy columns so the chart isn't too cluttered
    importance_df = importance_df[~importance_df.index.str.startswith('city_')]
    
    st.bar_chart(importance_df, horizontal=True)

st.divider()
st.caption("Built with Python, Scikit-Learn, Pandas, and Streamlit. Data sourced from Open-Meteo.")