# 🌍 All-India Predictive AQI Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://predictive-aqi-dashboard.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-Scikit_Learn-orange)
![Database](https://img.shields.io/badge/Database-Supabase-green)

An end-to-end Data Science and Machine Learning pipeline that predicts the next hour's Air Quality Index (AQI) across India's major metropolitan anchor cities. 

Unlike standard weather dashboards that simply display third-party API data, this application utilizes a custom **Random Forest Regressor** to actively forecast pollution levels based on incoming meteorological shifts and historical time-series baselines.

## 🚀 Live Demo
**[Experience the Live Predictive Dashboard Here](https://predictive-aqi-dashboard.streamlit.app/)**

## 🧠 The Data Science Architecture

### 1. Data Extraction & Storage
* **Source:** Harvested **10,600+ rows** of highly detailed, multi-city historical environmental data via the Open-Meteo API.
* **Storage:** Data is securely batched and routed to a cloud-hosted **PostgreSQL (Supabase)** database.
* **Engineering:** Implemented automated pagination scripts to bypass standard API row-limits during data retrieval.

### 2. Feature Engineering (Solving Geographical Variance)
Predicting AQI across a subcontinent requires the model to understand distinct regional climates (e.g., coastal humidity in Mumbai vs. landlocked dry heat in Delhi). 
* **One-Hot Encoding:** Applied to categorical city data to allow the algorithm to apply specific regional weights.
* **Autocorrelation (Lag Features):** Engineered `aqi_1_hour_ago` and `aqi_2_hours_ago` features, teaching the model to weigh recent pollution baselines against incoming weather changes for hyper-accurate, short-term forecasting.

### 3. The Machine Learning Model
* **Algorithm:** Random Forest Regressor (`scikit-learn`)
* **Mean Absolute Error (MAE):** 1.91 AQI Points
* **R² Score:** 0.99

## 💻 Tech Stack
* **Frontend/UI:** Streamlit Community Cloud
* **Data Manipulation:** Pandas
* **Machine Learning:** Scikit-Learn, Joblib
* **Backend Database:** Supabase (PostgreSQL)

## 🛠️ Local Installation & Setup

Want to run the model locally? 

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rangajanithram/predictive-aqi-dashboard.git](https://github.com/rangajanithram/predictive-aqi-dashboard.git)
   cd predictive-aqi-dashboard
