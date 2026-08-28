import glob
import json
import os
import gc
import re
import geopandas as gpd

# ============================================================
# Find the latest batch files (Input files)
# ============================================================

all_files = glob.glob("data/raw/protected_planet_batches/protected_planet_*.json")

# Extract dates from filenames
dates = [re.search(r"protected_planet_(\d{8})_batch_", f).group(1) for f in all_files]

# Find the latest date
latest_date = max(dates)

# Use only files from the latest date
input_pattern = (
    f"data/raw/protected_planet_batches/"
    f"protected_planet_{latest_date}_batch_*.json"
)

input_files = sorted(glob.glob(input_pattern))

print(f"Latest date: {latest_date}")
print(f"Found {len(input_files)} batch files.")


# ============================================================
# Output GeoPackage
# ============================================================

output_path = f"data/protected_planet_{latest_date}.gpkg"

# Remove existing GeoPackage
if os.path.exists(output_path):
    os.remove(output_path)

# ============================================================
# Flatten one API record
# ============================================================

def flatten_record(record):
    """Convert one Protected Planet API record into flat attributes."""

    iucn = record.get("iucn_category") or {}
    designation = record.get("designation") or {}
    jurisdiction = designation.get("jurisdiction") or {}
    no_take = record.get("no_take_status") or {}
    management_authority = record.get("management_authority") or {}
    governance = record.get("governance") or {}
    realm = record.get("realm") or {}

    countries = record.get("countries") or []
    country = countries[0] if countries else {}

    legal_status = record.get("legal_status") or {}

    return {
        # Basic information
        "site_id": record.get("site_id"),
        "site_pid": record.get("site_pid"),
        "name_english": record.get("name_english"),
        "name": record.get("name"),
        "parent_iso3": record.get("parent_iso3"),

        # Protected area classification
        "site_type": record.get("site_type"),
        "is_oecm": record.get("is_oecm"),
        "marine": record.get("marine"),

        # Area
        "reported_area": record.get("reported_area"),
        "reported_marine_area": record.get("reported_marine_area"),
        "gis_area": record.get("gis_area"),
        "gis_marine_area": record.get("gis_marine_area"),

        # Verification / criteria
        "international_criteria": record.get("international_criteria"),
        "verif": record.get("verif"),

        # Management
        "management_plan": record.get("management_plan"),
        "management_authority_id": management_authority.get("id"),
        "management_authority_name": management_authority.get("name"),

        # Conservation / governance / ownership
        "conservation_objectives": record.get("conservation_objectives"),
        "governance_subtype": record.get("governance_subtype"),
        "owner_type": record.get("owner_type"),
        "ownership_subtype": record.get("ownership_subtype"),
        "inland_waters": record.get("inland_waters"),
        "oecm_assessment": record.get("oecm_assessment"),

        # Legal status
        "legal_status_id": legal_status.get("id"),
        "legal_status_name": legal_status.get("name"),
        "legal_status_updated_at": record.get("legal_status_updated_at"),

        # IUCN category
        "iucn_category_id": iucn.get("id"),
        "iucn_category_name": iucn.get("name"),

        # Designation
        "designation_id": designation.get("id"),
        "designation_name": designation.get("name"),
        "designation_jurisdiction_id": jurisdiction.get("id"),
        "designation_jurisdiction_name": jurisdiction.get("name"),

        # No-take status
        "no_take_status_id": no_take.get("id"),
        "no_take_status_name": no_take.get("name"),
        "no_take_status_area": no_take.get("area"),

        # Governance
        "governance_id": governance.get("id"),
        "governance_type": governance.get("governance_type"),

        # Realm
        "realm_id": realm.get("id"),
        "realm_name": realm.get("name"),

        # Green List
        "is_green_list": record.get("is_green_list"),

        # Other information
        "supplementary_info": record.get("supplementary_info"),

        # Country
        "country_name": country.get("name"),
        "country_iso3": country.get("iso_3"),
    }


# ============================================================
# Process batch files
# ============================================================

for i, input_file in enumerate(input_files, start=1):

    print(f"\nProcessing batch {i}/{len(input_files)}:")
    print(input_file)

    # Load one JSON batch
    with open(input_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Convert JSON records into GeoJSON Features
    features = []
    for record in records:
        geojson = record.get("geojson")

        if not geojson or not geojson.get("geometry"):
            continue

        features.append({
            "type": "Feature",
            "geometry": geojson.get("geometry"),
            "properties": flatten_record(record),
        })

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
    print(f"Records converted: {len(gdf)}")

    # Write to GeoPackage
    if i == 1:
        gdf.to_file(
            output_path,
            layer="parotected_areas",
            driver="GPKG"
        )
    else:
        gdf.to_file(
            output_path,
            layer="parotected_areas",
            driver="GPKG",
            mode="a"
        )

    #Release memory
    del features
    del records
    del gdf
    gc.collect()

    print("Batch completed")

# ============================================================
# Finished
# ============================================================

print("\nIntegration completed.")
print(f"Output: {output_path}")