import pandas as pd

# ============================================================
# Settings
# ============================================================

input_path = "data/processed/gis_area_results.csv"
output_path = "data/processed/visualization_results.csv"

# Official Target 3 denominators from Protected Planet Report 2024
denominators = {
    "terrestrial": 134_530_000,
    "marine": 363_000_000,
}

target_pct = 30.0


# ============================================================
# Load GIS-derived results
# ============================================================

print(f"Loading GIS results: {input_path}")

df = pd.read_csv(input_path)

print(f"Records: {len(df)}")


# ============================================================
# Create visualization-ready records
# ============================================================

rows = []

for _, row in df.iterrows():

    category = row["category"]

    for realm, area_column, skipped_column in [
        (
            "terrestrial",
            "terrestrial_km2",
            "terrestrial_skipped_count",
        ),
        (
            "marine",
            "marine_km2",
            "marine_skipped_count",
        ),
    ]:

        area_km2 = row[area_column]
        denominator_km2 = denominators[realm]

        coverage_pct = (
            area_km2 / denominator_km2 * 100
        )

        rows.append(
            {
                "category": category,
                "realm": realm,
                "gis_area_km2": area_km2,
                "denominator_km2": denominator_km2,
                "coverage_pct": coverage_pct,
                "target_pct": target_pct,
                "skipped_non_polygon_count": row[
                    skipped_column
                ],
            }
        )


# ============================================================
# Create DataFrame
# ============================================================

result = pd.DataFrame(rows)


# ============================================================
# Round values for presentation
# ============================================================

result["gis_area_km2"] = result["gis_area_km2"].round(2)
result["coverage_pct"] = result["coverage_pct"].round(2)


# ============================================================
# Save
# ============================================================

result.to_csv(
    output_path,
    index=False
)

print("\nVisualization results:")
print(result.to_string(index=False))

print(
    f"\nSaved visualization-ready results to: "
    f"{output_path}"
)