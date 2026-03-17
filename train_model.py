import os
import pandas as pd
from supabase import create_client, Client
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 🗄️ SUPABASE CONFIGURATION
# Paste your keys here just like you did for the seeder
SUPABASE_URL = "https://cleothngpaqybiomauei.supabase.co"
SUPABASE_KEY = "sb_publishable_MnROBSTNKcCxzGr6CDPmEA_sIiagimS"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_all_data():
    print("📥 Downloading historical data from Supabase...")
    # Fetching up to 1000 rows
    response = supabase.table('air_quality_logs').select("*").limit(1000).execute()
    data = response.data
    return pd.DataFrame(data)

def prepare_data(df):
    print("⚙️ Preparing data and engineering features...")
    # Convert string timestamp to actual datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Feature Engineering: The model can't read "dates", but it CAN read numbers.
    # Let's extract the hour and day of the week so it learns traffic patterns!
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek # 0=Monday, 6=Sunday
    
    # Select our Features (X) and our Target (y)
    features = ['temperature', 'humidity', 'wind_speed', 'hour', 'day_of_week']
    
    # Drop any rows that might have missing data
    df = df.dropna(subset=features + ['aqi'])
    
    X = df[features]
    y = df['aqi']
    
    return X, y

if __name__ == "__main__":
    # 1. Get the data
    df = fetch_all_data()
    print(f"📊 Loaded {len(df)} rows of data.")
    
    # 2. Prepare it
    X, y = prepare_data(df)
    
    # 3. Split into Training Data (80%) and Testing Data (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train the Model!
    print("🧠 Training the Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Test the Model's accuracy
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    score = r2_score(y_test, predictions)
    
    print("\n✅ Model Training Complete!")
    print(f"🎯 Mean Absolute Error (MAE): {mae:.2f} AQI points")
    print(f"📈 R2 Score (Accuracy): {score:.2f} (1.0 is perfect)")
    
    # 6. Save the trained model to a file
    joblib.dump(model, 'aqi_model.pkl')
    print("\n💾 Model saved successfully as 'aqi_model.pkl'!")