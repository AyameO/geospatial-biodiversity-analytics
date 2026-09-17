import geopandas as gpd
import pandas as pd

# ============================================================
# File paths
# ============================================================

wdpca_path = (
    "data/processed/"
    "cleaned_protected_planet_gis_analysis.gpkg"
)

target3_mask_path = (
    "data/processed/"
    "target3_eligible_mask.gpkg"
)

output_path = (
    "data/processed/"
    "gis_area_results.csv"
)


# ============================================================
# Load WDPCA 
# ============================================================

print("Loading WDPCA...")

wdpca = gpd.read_file(wdpca_path)

print(f"WDPCA records: {len(wdpca)}")
print(f"WDPCA CRS: {wdpca.crs}")


# ============================================================
# Load Target 3 eligible mask
# ============================================================

print("\nLoading Target 3 eligible mask...")

mask_gdf = gpd.read_file(target3_mask_path)

print(f"Mask CRS: {mask_gdf.crs}")

target3_mask = mask_gdf.geometry.union_all()

print("Target 3 eligible mask loaded.")


# ============================================================
# Function to calculate area
# ============================================================

def calculate_area(gdf, category, mask):

    print(f"\nProcessing: {category}")

    terrestrial = gdf[gdf["marine"] == False]
    marine = gdf[gdf["marine"] == True]

    print("  Union terrestrial...")
    terrestrial_union = terrestrial.geometry.union_all()
    print("  Terrestrial union completed.")

    print("  Union marine...")
    marine_union = marine.geometry.union_all()
    print("  Marine union completed.")

    print("  Intersect terrestrial with mask...")
    terrestrial_intersection = terrestrial_union.intersection(mask)
    print("  Terrestrial intersection completed.")

    print("  Intersect marine with mask...")
    marine_intersection = marine_union.intersection(mask)
    print("  Marine intersection completed.")

    terrestrial_area = (
        gpd.GeoSeries(
            [terrestrial_intersection],
            crs=gdf.crs
        )
        .to_crs("EPSG:6933")
        .area.iloc[0]
        / 1_000_000
    )

    marine_area = (
        gpd.GeoSeries(
            [marine_intersection],
            crs=gdf.crs
        )
        .to_crs("EPSG:6933")
        .area.iloc[0]
        / 1_000_000
    )

    print(f"  Terrestrial: {terrestrial_area:,.2f} km²")
    print(f"  Marine: {marine_area:,.2f} km²")

    return {
        "category": category,
        "terrestrial_km2": terrestrial_area,
        "marine_km2": marine_area,
    }


# ============================================================
# Calculate areas
# ============================================================

results = []

results.append(
    calculate_area(
        wdpca,
        "PA + OECM",
        target3_mask
    )
)

pa_only = wdpca[wdpca["is_oecm"] == False]

results.append(
    calculate_area(
        pa_only,
        "PA only",
        target3_mask
    )
)

oecm_only = wdpca[wdpca["is_oecm"] == True]

results.append(
    calculate_area(
        oecm_only,
        "OECM only",
        target3_mask
    )
)


# ============================================================
# Create results table
# ============================================================

results_df = pd.DataFrame(results)


# ============================================================
# Display results
# ============================================================

print("\n" + "=" * 60)
print("GIS-DERIVED AREA RESULTS")
print("=" * 60)

print(results_df.to_string(index=False))


# ============================================================
# Save results
# ============================================================

results_df.to_csv(
    output_path,
    index=False
)

print(f"\nSaved: {output_path}")