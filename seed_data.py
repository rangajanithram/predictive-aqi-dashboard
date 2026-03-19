import requests
import pandas as pd
from supabase import create_client, Client
import time

# 🗄️ SUPABASE CONFIGURATION
SUPABASE_URL = "https://cleothngpaqybiomauei.supabase.co"

SUPABASE_KEY = "sb_publishable_MnROBSTNKcCxzGr6CDPmEA_sIiagimS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🌍 Fetching REAL historical data for All-India Anchors from Open-Meteo...")

# India's Major Anchor Cities (Representing different climate zones)
CITIES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},       # Northern / Landlocked
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},      # Western / Coastal Humid
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},   # Southern / Moderate Elevation
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},     # Eastern / Coastal
    "Chennai": {"lat": 13.0827, "lon": 80.2707},     # Southern / Tropical Wet
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867}    # Central / Dry
}

DAYS_BACK = 90
all_city_records = []

for city_name, coords in CITIES.items():
    print(f"📡 Downloading data for {city_name}...")
    lat = coords["lat"]
    lon = coords["lon"]
    
    # 1. Fetch Real Weather Data
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&past_days={DAYS_BACK}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    weather_res = requests.get(weather_url).json()

    # 2. Fetch Real Air Quality Data
    aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&past_days={DAYS_BACK}&hourly=pm10,pm2_5,us_aqi"
    aqi_res = requests.get(aqi_url).json()

    # 3. Combine them using Pandas
    df_weather = pd.DataFrame(weather_res['hourly'])
    df_aqi = pd.DataFrame(aqi_res['hourly'])

    # Merge the datasets
    df_real = pd.merge(df_weather, df_aqi, on='time')
    df_real = df_real.rename(columns={
        'time': 'timestamp',
        'temperature_2m': 'temperature',
        'relative_humidity_2m': 'humidity',
        'wind_speed_10m': 'wind_speed',
        'us_aqi': 'aqi',
        'pm2_5': 'pm25'
    })
    
    # Tag the row with the specific city
    df_real['city'] = city_name
    df_real = df_real.dropna()
    
    # Add to our master list
    records = df_real.to_dict(orient='records')
    all_city_records.extend(records)
    
    # Pause for 1 second to respect the free API limits
    time.sleep(1)

print(f"\n🚀 Total rows collected: {len(all_city_records)}. Pushing to Supabase in batches...")

# 4. Push to Supabase in batches
batch_size = 100
for i in range(0, len(all_city_records), batch_size):
    batch = all_city_records[i:i + batch_size]
    try:
        supabase.table('air_quality_logs').insert(batch).execute()
        print(f"✅ Inserted batch {i // batch_size + 1} of {len(all_city_records) // batch_size + 1}...")
    except Exception as e:
        print(f"❌ Error on batch {i // batch_size + 1}: {e}")

print("🎉 ALL-INDIA historical data successfully seeded!")