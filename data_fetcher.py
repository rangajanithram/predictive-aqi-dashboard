import os
import requests
import json
from datetime import datetime, timezone
from supabase import create_client, Client

# ⚙️ SECURE CONFIGURATION
CITY = "bangalore" 
TOKEN = os.getenv("WAQI_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
def fetch_aqi_data(city, token):
    url = f"https://api.waqi.info/feed/{city}/?token={token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok':
            raw_data = data['data']
            extracted = {
                # Format changed slightly to match PostgreSQL timestamptz requirements
                "timestamp": datetime.now(timezone.utc).isoformat(), 
                "city": raw_data['city']['name'],
                "aqi": raw_data['aqi'],
                "pm25": raw_data.get('iaqi', {}).get('pm25', {}).get('v', None),
                "pm10": raw_data.get('iaqi', {}).get('pm10', {}).get('v', None),
                "temperature": raw_data.get('iaqi', {}).get('t', {}).get('v', None),
                "humidity": raw_data.get('iaqi', {}).get('h', {}).get('v', None),
                "wind_speed": raw_data.get('iaqi', {}).get('w', {}).get('v', None)
            }
            return extracted
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print(f"📡 Fetching live environmental data for {CITY}...")
    current_data = fetch_aqi_data(CITY, TOKEN)
    
    if current_data:
        print("✅ Data Extracted. Pushing to Supabase...")
        
        # 🚀 PUSH TO DATABASE
        try:
            response = supabase.table('air_quality_logs').insert(current_data).execute()
            print("🎉 Success! Row inserted into database.")
            print(json.dumps(current_data, indent=4))
        except Exception as e:
            print(f"❌ Database Insertion Failed: {e}")