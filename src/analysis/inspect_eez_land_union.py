import geopandas as gpd
import matplotlib.pyplot as plt

# ============================================================
# Load Marine Regions EEZ + land union dataset
# ============================================================

input_path = (
    "data/raw/EEZ_land_union_v4/"
    "EEZ_land_union_v4_202410.shp"
)

print(f"Input file: {input_path}")

gdf = gpd.read_file(input_path)

print(f"\nRecords: {len(gdf)}")
print(f"CRS: {gdf.crs}")

output_path = ("data/processed/eez_land_union_v4_preview.png")

# ============================================================
# Geometry types
# ============================================================

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

# ============================================================
# Columns
# ============================================================

print("\nColumns:")
print(gdf.columns.tolist())

# ============================================================
# Antarctica check
# ============================================================

print("\nAntarctica check (TERRITORY1):")

antarctica_territory = gdf[
    gdf["TERRITORY1"]
    .astype(str)
    .str.contains("Antarctica", case=False, na=False)
]

print(
    antarctica_territory[
        ["UNION", "MRGID_EEZ", "TERRITORY1", "AREA_KM2"]
    ]
)

print("\nAntarctica check (UNION):")

antarctica_union = gdf[
    gdf["UNION"]
    .astype(str)
    .str.contains("Antarctica", case=False, na=False)
]

print(
    antarctica_union[
        ["UNION", "MRGID_EEZ", "TERRITORY1", "AREA_KM2"]
    ]
)

# ============================================================
# First rows
# ============================================================

print("\nFirst rows:")
print(
    gdf[
        ["UNION", "MRGID_EEZ", "TERRITORY1", "AREA_KM2"]
    ].head(10)
)


# ============================================================
# Plot
# ============================================================

fig, ax = plt.subplots(figsize=(16, 9))

gdf.plot(
    ax=ax,
    edgecolor="black",
    linewidth=0.2
)

ax.set_title(
    "Marine Regions: Union of World Country Boundaries and EEZs",
    fontsize=14
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.set_aspect("equal")

plt.tight_layout()


# ============================================================
# Save
# ============================================================

plt.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print(f"\nSaved: {output_path}")