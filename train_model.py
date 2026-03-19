import os
import pandas as pd
from supabase import create_client, Client
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 🗄️ SUPABASE CONFIGURATION
SUPABASE_URL = "https://cleothngpaqybiomauei.supabase.co"

SUPABASE_KEY = "sb_publishable_MnROBSTNKcCxzGr6CDPmEA_sIiagimS"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_all_data():
    print("📥 Downloading All-India data (Bypassing 1000-row safety limit via Pagination)...")
    all_data = []
    start = 0
    limit = 1000
    
    # Keep asking Supabase for chunks of 1000 until there is nothing left
    while True:
        response = supabase.table('air_quality_logs').select("*").range(start, start + limit - 1).execute()
        data = response.data
        
        if not data:
            break # We got all the data!
            
        all_data.extend(data)
        start += limit
        print(f"   ...Downloaded {len(all_data)} rows so far")
        
    return pd.DataFrame(all_data)

def prepare_data(df):
    print("⚙️ Engineering advanced features...")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by city and time so we can look at the "past" accurately
    df = df.sort_values(by=['city', 'timestamp'])
    
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # 🪄 ADVANCED DATA SCIENCE: The "Lag" Feature
    # Teach the model what the AQI was 1 hour ago and 2 hours ago in that specific city
    df['aqi_1_hour_ago'] = df.groupby('city')['aqi'].shift(1)
    df['aqi_2_hours_ago'] = df.groupby('city')['aqi'].shift(2)
    
    # 🪄 ONE-HOT ENCODING
    city_dummies = pd.get_dummies(df['city'], prefix='city')
    
    base_features = ['temperature', 'humidity', 'wind_speed', 'hour', 'day_of_week', 'aqi_1_hour_ago', 'aqi_2_hours_ago']
    
    df_processed = pd.concat([df[base_features + ['aqi']], city_dummies], axis=1)
    
    # Drop rows that don't have past data (like the very first row of the dataset)
    df_processed = df_processed.dropna()
    
    y = df_processed['aqi']
    X = df_processed.drop('aqi', axis=1)
    
    return X, y

if __name__ == "__main__":
    df = fetch_all_data()
    print(f"📊 Total Dataset Loaded: {len(df)} rows.")
    
    X, y = prepare_data(df)
    
    expected_columns = X.columns.tolist()
    joblib.dump(expected_columns, 'model_columns.pkl')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("🧠 Training the highly advanced Random Forest Model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    score = r2_score(y_test, predictions)
    
    print("\n✅ Advanced Training Complete!")
    print(f"🎯 Mean Absolute Error (MAE): {mae:.2f} AQI points")
    print(f"📈 R2 Score (Accuracy): {score:.2f} (1.0 is perfect)")
    
    joblib.dump(model, 'aqi_model.pkl')
    print("\n💾 Model saved successfully!")