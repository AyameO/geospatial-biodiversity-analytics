import geopandas as gpd

# ============================================================
# File paths
# ============================================================

eez_land_union_path = (
    "data/raw/EEZ_land_union_v4/"
    "EEZ_land_union_v4_202410.shp"
)

output_path = (
    "data/processed/"
    "target3_eligible_mask.gpkg"
)


# ============================================================
# Load EEZ + land union
# ============================================================

print("Loading EEZ + land union...")

eez = gpd.read_file(eez_land_union_path)

print(f"Records: {len(eez)}")
print(f"CRS: {eez.crs}")


# ============================================================
# Remove Antarctica
# ============================================================

print("\nRemoving Antarctica...")

eez_no_antarctica = eez[
    eez["UNION"] != "Antarctica"
].copy()

print(
    f"Records after Antarctica exclusion: "
    f"{len(eez_no_antarctica)}"
)


# ============================================================
# Union all eligible areas
# ============================================================

print("\nCreating Target 3 eligible mask...")

target3_mask = eez_no_antarctica.geometry.union_all()

print("Target 3 eligible mask created.")


# ============================================================
# Create GeoDataFrame
# ============================================================

result = gpd.GeoDataFrame(
    {
        "name": ["target3_eligible"]
    },
    geometry=[target3_mask],
    crs=eez.crs
)


# Save result to file
result.to_file(output_path, driver="GPKG")

print(f"\nSaved: {output_path}")

print("\nResult:")
print(result)