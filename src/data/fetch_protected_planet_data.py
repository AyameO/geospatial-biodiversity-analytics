import os
import json
import gc
import requests
from dotenv import load_dotenv
from datetime import datetime

# ============================================================
# Variable Initialization
# ============================================================

load_dotenv()

api_key = os.getenv("PROTECTED_PLANET_API_TOKEN")

url = "https://api.protectedplanet.net/v4/protected_areas"

# Pagination settings
page = 1
per_page = 50

# Save every 200 pages (10,000 records)
pages_per_batch = 200
batch_number = 1

# Outout directory for GeoJSON files
output_dir = "data/raw/protected_planet_batches"
os.makedirs(output_dir, exist_ok=True)
date_str = datetime.now().strftime("%Y%m%d")

# Temporary stoarge for one batch
batch_protected_areas = []


# ============================================================
# Data Retrieval Process
# ============================================================

while True:
    params = {
        "page": page,
        "per_page": per_page,
        "token": api_key,
        "with_geometry": True
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    protected_areas = data["protected_areas"]

    #Stop when there are no more records
    if not protected_areas:
        break

    batch_protected_areas.extend(protected_areas)


    print(
        f"Page {page}: {len(protected_areas)} records"
        f"(batch: {len(batch_protected_areas)} records)"
    )

    #Save every 200 pages (10,000 records)
    if page % pages_per_batch == 0:
        output_path = os.path.join(
            output_dir,
            f"protected_planet_{date_str}_batch_{batch_number:03d}.json"
            )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(batch_protected_areas, f, ensure_ascii=False)

        print(
            f"Saved batch {batch_number}: "
            f"{len(batch_protected_areas)} records"
        )

        # Clear memory
        batch_protected_areas.clear()
        gc.collect()

        batch_number += 1

    page += 1

# Save the final partial batch
if batch_protected_areas:
    output_path = os.path.join(
        output_dir,
        f"protected_planet_{date_str}_batch_{batch_number:03d}.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch_protected_areas, f, ensure_ascii=False)

    print(
        f"Saved final batch {batch_number}: "
        f"{len(batch_protected_areas)} records" 
    )

    batch_protected_areas.clear()
    gc.collect()

print("Data retrieval completed.")