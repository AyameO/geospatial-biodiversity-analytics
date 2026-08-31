import geopandas as gpd
import pandas as pd
import glob
from shapely import make_valid
# from shapely.validation import explain_validity

# ============================================================
# 1. Load the latest GeoPackage
# ============================================================

# Find the latest GeoPackage
input_pattern = "data/processed/protected_planet_*.gpkg"
input_files = sorted(glob.glob(input_pattern))

if not input_files:
    raise FileNotFoundError("No Protected Planet GeoPackage found.")

input_path = input_files[-1]

print(f"Input file: {input_path}")

# Load the GeoPackage
gdf = gpd.read_file(input_path)

print(f"Total records: {len(gdf)}")
print(f"CRS: {gdf.crs}")


# ============================================================
# 2. Extract Polygon / MultiPolygon geometries
# ============================================================

# Select Polygon / MultiPolygon geometries
polygon_mask = gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])

polygon_gdf = gdf[polygon_mask].copy()

print("\nPolygon geometries:")
print(f"Records: {len(polygon_gdf)}")


# ============================================================
# 3. Validate polygon geometries
# ============================================================

valid_count = polygon_gdf.geometry.is_valid.sum()
invalid_count = (~polygon_gdf.geometry.is_valid).sum()

print(f"Valid geometries: {valid_count}")
print(f"Invalid geometries: {invalid_count}")

invalid_polygons = polygon_gdf[~polygon_gdf.geometry.is_valid].copy()

"""
# Classify invalid geometry reasons
def classify_invalid_reason(reason):
    if reason.startswith("Too few points"):
        return "Too few points"
    elif reason.startswith("Self-intersection"):
        return "Self-intersection"
    elif reason.startswith("Ring Self-intersection"):
        return "Ring Self-intersection"
    else:
        return "Other"


invalid_polygons["reason"] = (invalid_polygons.geometry.apply(explain_validity).apply(classify_invalid_reason))

print("\nInvalid geometry types:")
print(invalid_polygons["reason"].value_counts())
"""

# ============================================================
# 4. Repair invalid polygon geometries
# ============================================================

repaired_geometries = {}
failed_indices = []

for idx, geometry in invalid_polygons.geometry.items():

    try:
        repaired_geometries[idx] = make_valid(
            geometry,
            method="structure"
        )

    except Exception:
        failed_indices.append(idx)


# ============================================================
# 5. Extract polygon components from GeometryCollections
# ============================================================

# Start with all Polygon / MultiPolygon geometries
gis_geometry = polygon_gdf.geometry.copy()

# Replace invalid geometries with repaired geometries
for idx, geometry in repaired_geometries.items():
    gis_geometry.loc[idx] = geometry

def extract_polygon_geometry(geometry):

    if geometry is None:
        return None

    if geometry.geom_type in ["Polygon", "MultiPolygon"]:
        return geometry

    if geometry.geom_type == "GeometryCollection":

        polygons = [
            geom
            for geom in geometry.geoms
            if geom.geom_type in ["Polygon", "MultiPolygon"]
        ]

        if not polygons:
            return None

        if len(polygons) == 1:
            return polygons[0]

        return gpd.GeoSeries(
            polygons,
            crs=polygon_gdf.crs
        ).union_all()

    return None

gis_geometry = gis_geometry.apply(extract_polygon_geometry)


# ============================================================
# 6. Create final GIS GeoDataFrame
# ============================================================

# Identify geometries that remain invalid after repair
remaining_invalid_indices = gis_geometry[
    ~gis_geometry.isna()
    & ~gis_geometry.is_empty
    & ~gis_geometry.is_valid
].index

# Combine all unusable polygon geometries
excluded_invalid_indices = list(
    set(failed_indices) | set(remaining_invalid_indices)
)

print("\nGeometry repair:")
print(f"make_valid() succeeded: {len(repaired_geometries)}")

gis_gdf = polygon_gdf.copy()

gis_gdf["geometry"] = gis_geometry

# Remove unusable polygon geometries
gis_gdf = gis_gdf[
    ~gis_gdf.index.isin(excluded_invalid_indices)
].copy()

# Remove geometries without polygon components
gis_gdf = gis_gdf[
    ~gis_gdf.geometry.isna()
    & ~gis_gdf.geometry.is_empty
].copy()


# ============================================================
# 7. Inspect polygon geometries excluded from GIS analysis
# ============================================================

# Convert area fields to numeric
area_data = gdf[["gis_area", "reported_area"]].copy()

area_data["gis_area"] = pd.to_numeric(
    area_data["gis_area"],
    errors="coerce"
)

area_data["reported_area"] = pd.to_numeric(
    area_data["reported_area"],
    errors="coerce"
)


# ------------------------------------------------------------
# Unusable polygon geometries
# ------------------------------------------------------------

excluded_data = area_data.loc[excluded_invalid_indices]

print("\nUnusable polygon geometries:")
print(f"Records: {len(excluded_data)}")
print(f"gis_area Total (unusable): {excluded_data['gis_area'].sum()}")
print(f"reported_area Total (unusable): {excluded_data['reported_area'].sum()}")


# ------------------------------------------------------------
# Geometries without polygon components
# ------------------------------------------------------------

no_polygon_mask = (
    gis_geometry.isna()
    | gis_geometry.is_empty
)

no_polygon_indices = gis_geometry[no_polygon_mask].index

no_polygon_data = area_data.loc[no_polygon_indices]

print("\nGeometries without polygon components:")
print(f"Records: {len(no_polygon_data)}")
print(f"gis_area Total: {no_polygon_data['gis_area'].sum()}")
print(f"reported_area Total: {no_polygon_data['reported_area'].sum()}")


# ============================================================
# 8. Validate final GIS dataset
# ============================================================

print("\nFinal GIS dataset:")
print(f"Records: {len(gis_gdf)}")

print("\nGeometry types:")
print(gis_gdf.geometry.geom_type.value_counts())

print(f"\nRemaining invalid geometries: {(~gis_gdf.geometry.is_valid).sum()}")


# ============================================================
# 9. Save final GIS dataset
# ============================================================

output_path = ("data/processed/cleaned_protected_planet_gis_analysis.gpkg")

gis_gdf.to_file(output_path, driver="GPKG")

print(f"\nSaved GIS dataset: {output_path}")