import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

# ============================================================
# Settings
# ============================================================

input_path = "data/dashboard/gis_area_results.csv"
output_path = "data/dashboard/visualization_results.csv"

wdpca_batch_dir = Path("data/raw/protected_planet_batches")
metadata_output_path = Path("data/dashboard/metadata.json")

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
# Save visualization results
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


# ============================================================
# Detect WDPCA data retrieval date
# ============================================================

print("\nDetecting WDPCA data retrieval date...")

date_pattern = re.compile(
    r"protected_planet_(\d{8})_batch_\d+\.json$"
)

retrieval_dates = []

if wdpca_batch_dir.exists():

    for file_path in wdpca_batch_dir.glob("*.json"):

        match = date_pattern.match(file_path.name)

        if match:

            try:
                retrieval_date = datetime.strptime(
                    match.group(1),
                    "%Y%m%d"
                ).date()

                retrieval_dates.append(retrieval_date)

            except ValueError:
                pass


# ============================================================
# Create metadata
# ============================================================

if retrieval_dates:

    latest_retrieval_date = max(retrieval_dates)

    metadata = {
        "wdpca_retrieval_date": latest_retrieval_date.isoformat()
    }

    print(
        "WDPCA data retrieval date: "
        f"{latest_retrieval_date.strftime('%B %d, %Y')}"
    )

else:

    metadata = {
        "wdpca_retrieval_date": None
    }

    print(
        "WDPCA data retrieval date: not detected"
    )


# ============================================================
# Save metadata
# ============================================================

metadata_output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    metadata_output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=2
    )

print(
    f"Saved metadata to: "
    f"{metadata_output_path}"
)