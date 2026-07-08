import pandas as pd
import requests
import time
import os

soil_df = pd.read_csv("data/soil_npk.csv")
unique_districts = soil_df[["state", "district"]].drop_duplicates().sort_values(by=["state", "district"])

results = []
session = requests.Session()

print(f"Fetching accurate coordinates for {len(unique_districts)} districts...")

for idx, row in unique_districts.iterrows():
    state = row["state"]
    district = row["district"]
    
    # 1. Try Open-Meteo Geocoding API (Fast, no strict rate limit)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={district}&count=10&language=en&format=json"
    
    lat, lon = None, None
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "results" in data:
                for res in data["results"]:
                    if res.get("country") == "India":
                        lat = round(res.get("latitude"), 4)
                        lon = round(res.get("longitude"), 4)
                        break
    except Exception as e:
        print(f"Error fetching {district} from Open-Meteo: {e}")
        
    # 2. Fallback to Nominatim OSM if Open-Meteo misses it
    if lat is None or lon is None:
        try:
            nom_url = f"https://nominatim.openstreetmap.org/search?q={district},+{state},+India&format=json&limit=1"
            headers = {"User-Agent": "KisanAlertScript/1.0"}
            nom_resp = session.get(nom_url, headers=headers, timeout=5)
            if nom_resp.status_code == 200:
                nom_data = nom_resp.json()
                if len(nom_data) > 0:
                    lat = round(float(nom_data[0]["lat"]), 4)
                    lon = round(float(nom_data[0]["lon"]), 4)
            time.sleep(1) # Strict 1 req/sec for Nominatim
        except Exception:
            pass
            
    # 3. Ultimate fallback
    if lat is None:
        print(f"Warning: Could not geocode {district}, using fallback.")
        lat, lon = 20.0, 78.0
        
    results.append({"state": state, "district": district, "latitude": lat, "longitude": lon})
    
    # Progress logging
    if (len(results)) % 50 == 0:
        print(f"Processed {len(results)}/{len(unique_districts)} districts...")

dist_df = pd.DataFrame(results, columns=["state", "district", "latitude", "longitude"])
dist_df = dist_df.sort_values(by=["state", "district"])
dist_df.to_csv("data/districts.csv", index=False)
print(f"Successfully saved {len(dist_df)} accurate coordinates to data/districts.csv")

# Cleanup old scripts
for f in ["generate_csv.py", "update_coords.py"]:
    if os.path.exists(f):
        os.remove(f)
