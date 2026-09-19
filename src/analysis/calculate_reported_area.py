import geopandas as gpd
import pandas as pd
import glob

# ============================================================
# Load the latest GeoPackage
# ============================================================

input_pattern = "data/processed/protected_planet_*.gpkg"
input_files = sorted(glob.glob(input_pattern))

if not input_files:
    raise FileNotFoundError("No Protected Planet GeoPackage found.")

input_path = input_files[-1]

print(f"Input file: {input_path}")

gdf = gpd.read_file(input_path)

print(f"Records: {len(gdf)}")
print(f"CRS: {gdf.crs}")


# ============================================================
# Calculate Reported Area
# ============================================================

gdf["reported_area"] = pd.to_numeric(
    gdf["reported_area"],
    errors="coerce"
)

gdf["reported_marine_area"] = pd.to_numeric(
    gdf["reported_marine_area"],
    errors="coerce"
)


# ============================================================
# Global Reported Area
# ============================================================

reported_area_count = gdf["reported_area"].count()
reported_area_total = gdf["reported_area"].sum()

print("\nReported Area:")
print(f"Records with reported_area: {reported_area_count}")
print(f"Total reported_area: {reported_area_total:.2f} km²")


# ============================================================
# Marine Reported Area
# ============================================================

reported_marine_count = (
    gdf["reported_marine_area"] > 0
).sum()

reported_marine_total = (
    gdf["reported_marine_area"].sum()
)

print(f"\nRecords with reported_marine_area: {reported_marine_count}")
print(
    f"Total reported_marine_area: "
    f"{reported_marine_total:.2f} km²"
)


# ============================================================
# Terrestrial Reported Area
# ============================================================

reported_terrestrial_total = (
    reported_area_total - reported_marine_total
)

print("\nTotal terrestrial reported area:")
print(f"{reported_terrestrial_total:.2f} km²")


# ============================================================
# Save Results
# ============================================================

results = pd.DataFrame([
    {
        "metric": "reported_area",
        "area_km2": reported_area_total,
        "record_count": reported_area_count,
    },
    {
        "metric": "reported_marine_area",
        "area_km2": reported_marine_total,
        "record_count": reported_marine_count,
    },
    {
        "metric": "reported_terrestrial_area",
        "area_km2": reported_terrestrial_total,
        "record_count": reported_area_count,
    },
])

output_path = "data/processed/reported_area_results.csv"

results.to_csv(
    output_path,
    index=False
)

print(f"\nResults saved to: {output_path}")