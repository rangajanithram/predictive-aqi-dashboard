import os
import random
from datetime import datetime, timedelta, timezone
import requests
import pandas as pd
from supabase import create_client, Client

# 🗄️ SUPABASE CONFIGURATION
# We can temporarily hardcode this just for the seeder script
SUPABASE_URL = "https://cleothngpaqybiomauei.supabase.co"
SUPABASE_KEY = "sb_publishable_MnROBSTNKcCxzGr6CDPmEA_sIiagimS"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🌍 Fetching REAL historical data for Bengaluru from Open-Meteo...")

# Bengaluru Coordinates
LAT = 12.9716
LON = 77.5946
DAYS_BACK = 90 # Get the last 3 months of real data

# 1. Fetch Real Weather Data
weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&past_days={DAYS_BACK}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
weather_res = requests.get(weather_url).json()

# 2. Fetch Real Air Quality Data
aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&past_days={DAYS_BACK}&hourly=pm10,pm2_5,us_aqi"
aqi_res = requests.get(aqi_url).json()

# 3. Combine them using Pandas
print("🧬 Processing and cleaning the real data...")
df_weather = pd.DataFrame(weather_res['hourly'])
df_aqi = pd.DataFrame(aqi_res['hourly'])

# Merge the two datasets based on the exact hour they were recorded
df_real = pd.merge(df_weather, df_aqi, on='time')

# Rename columns to match our Supabase database exactly
df_real = df_real.rename(columns={
    'time': 'timestamp',
    'temperature_2m': 'temperature',
    'relative_humidity_2m': 'humidity',
    'wind_speed_10m': 'wind_speed',
    'us_aqi': 'aqi',
    'pm2_5': 'pm25'
})

# Add the city name
df_real['city'] = "Bengaluru, India"

# Clean the data: Drop any hours where the real-world sensors were broken/offline (NaN values)
df_real = df_real.dropna()

# Convert to a format Supabase can read
records = df_real.to_dict(orient='records')

print(f"🚀 Pushing {len(records)} rows of REAL data to Supabase...")

# 4. Push to Supabase in batches
batch_size = 100
for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]
    try:
        supabase.table('air_quality_logs').insert(batch).execute()
        print(f"✅ Inserted batch {i // batch_size + 1}...")
    except Exception as e:
        print(f"❌ Error on batch {i // batch_size + 1}: {e}")

print("🎉 REAL historical data successfully seeded!")