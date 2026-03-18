import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# 🎨 App Configuration
st.set_page_config(page_title="Bengaluru AQI Predictor", page_icon="🌍", layout="centered")

# 🧠 Load the Trained Model
@st.cache_resource
def load_model():
    return joblib.load('aqi_model.pkl')

model = load_model()

st.title("🌍 Bengaluru AQI Predictor")

# 🗂️ Create Tabs
tab1, tab2 = st.tabs(["🔮 Live Predictor", "📊 Behind the ML Model"])

# ==========================================
# TAB 1: THE PREDICTOR (For Regular Users)
# ==========================================
with tab1:
    st.markdown("""
    This interactive dashboard uses a **Machine Learning Random Forest** model trained on real-world historical data to predict the Air Quality Index (AQI) based on weather conditions and time of day.
    """)
    st.divider()

    st.subheader("⚙️ Adjust Weather Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        temp = st.slider("Temperature (°C)", min_value=15.0, max_value=45.0, value=28.0, step=0.5)
        humidity = st.slider("Humidity (%)", min_value=10.0, max_value=100.0, value=50.0, step=1.0)
    with col2:
        wind = st.slider("Wind Speed (km/h)", min_value=0.0, max_value=30.0, value=5.0, step=0.5)
        hour = st.slider("Hour of Day", min_value=0, max_value=23, value=datetime.now().hour)

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = st.selectbox("Day of the Week", days_of_week)
    day_number = days_of_week.index(day_name)

    if st.button("🔮 Predict AQI", use_container_width=True):
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
    st.header("🧠 Model Architecture")
    st.markdown("""
    Unlike standard weather apps that simply display third-party API data, this application features a **custom Machine Learning pipeline**. 
    
    The predictive engine is powered by a **Random Forest Regressor** trained on historical environmental data specific to Bengaluru.
    """)
    
    # Show off your metrics
    st.subheader("📈 Model Performance Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Algorithm", value="Random Forest")
    col2.metric(label="Mean Absolute Error", value="15.59 AQI")
    col3.metric(label="R² Score", value="0.36")
    
    st.caption("*Note: An R² score of 0.36 using strictly baseline weather data (without traffic or industrial emissions data) provides a highly realistic baseline for meteorological impact on PM2.5 levels.*")
    
    st.divider()

    # Extract exactly how the AI "thinks" directly from the .pkl file!
    st.subheader("📊 Feature Importance")
    st.markdown("This chart reveals which environmental factors the AI relies on most heavily to make its predictions. (Extracted dynamically from the trained model).")
    
    # Get the feature names and their importance scores directly from the model
    features = ['Temperature', 'Humidity', 'Wind Speed', 'Hour of Day', 'Day of Week']
    importances = model.feature_importances_
    
    # Create a DataFrame for the chart
    importance_df = pd.DataFrame({
        'Impact on AQI': importances
    }, index=features).sort_values(by='Impact on AQI', ascending=True)
    
    # Display the built-in Streamlit Bar Chart
    st.bar_chart(importance_df, horizontal=True)

    st.divider()
    st.subheader("🗄️ The Data Pipeline")
    st.markdown("""
    1. **Extraction:** Real historical weather and pollution data fetched via the Open-Meteo API.
    2. **Storage:** Stored in a cloud-hosted **PostgreSQL (Supabase)** database.
    3. **Preprocessing:** Cleaned and engineered using **Pandas** (e.g., converting UTC timestamps to local traffic-hour weights).
    4. **Deployment:** Hosted live via Streamlit Community Cloud.
    """)

st.divider()
st.caption("Built with Python, Scikit-Learn, Pandas, and Streamlit.")