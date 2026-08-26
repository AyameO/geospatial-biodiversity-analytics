import os
import requests
import geopandas as gpd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PROTECTED_PLANET_API_TOKEN")

url = "https://api.protectedplanet.net/v4/protected_areas"

# Pagination test: fetch up to 3 pages
all_protected_areas = []
page = 1
per_page = 50

while True:
    params = {
        "page": page,
        "per_page": per_page,
        "token": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    protected_areas = data["protected_areas"]

    if not protected_areas:
        break

    all_protected_areas.extend(protected_areas)
    print(f"Page {page}: {len(protected_areas)} records")

    page += 1

print("Total records:", len(all_protected_areas))
