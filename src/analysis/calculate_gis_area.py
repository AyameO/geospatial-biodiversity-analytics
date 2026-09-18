import gc
import warnings
from pathlib import Path
import geopandas as gpd
import pandas as pd
import shapely
from shapely.geometry import box

# Shapely の非推奨警告（UserWarning）を非表示にする設定
warnings.filterwarnings("ignore", category=UserWarning)

# ============================================================
# Settings & Paths
# ============================================================

wdpca_path = "data/processed/cleaned_protected_planet_gis_analysis.gpkg"
target3_mask_path = "data/processed/target3_eligible_mask.gpkg"
output_path = "data/processed/gis_area_results.csv"

# 一時保存ディレクトリ
temp_dir = Path("data/temp/grid_area_results")
temp_dir.mkdir(parents=True, exist_ok=True)

# 視認性向上のため、グリッドサイズを 1,000km に設定
grid_size = 1_000_000

# ============================================================
# Load & Prepare Data
# ============================================================

print("Loading WDPCA...")
wdpca = gpd.read_file(wdpca_path)
print(f"WDPCA records: {len(wdpca):,}")

print("\nLoading Target 3 eligible mask...")
mask_gdf = gpd.read_file(target3_mask_path)
print(f"Mask records: {len(mask_gdf):,}")

print("\nReprojecting data to EPSG:6933...")
wdpca = wdpca.to_crs("EPSG:6933")
mask_gdf = mask_gdf.to_crs("EPSG:6933")

print("Validating Target 3 mask...")
mask_gdf["geometry"] = mask_gdf.geometry.make_valid()

print("Validating WDPCA geometries (fixing invalid polygons)...")
wdpca["geometry"] = wdpca.geometry.make_valid()

print("Creating spatial index for Target 3 mask...")
mask_sindex = mask_gdf.sindex

# ============================================================
# Create Global Grid System
# ============================================================

print("\nCreating global grid system...")
minx, miny, maxx, maxy = mask_gdf.total_bounds

grid_cells = []
grid_id = 0
x = minx

while x < maxx:
    y = miny
    while y < maxy:
        cell = box(x, y, min(x + grid_size, maxx), min(y + grid_size, maxy))
        
        # 空間インデックスを使い、マスクが存在するグリッドのみ採用
        possible_mask_idx = list(mask_sindex.query(cell, predicate="intersects"))
        if possible_mask_idx:
            grid_cells.append({"grid_id": grid_id, "geometry": cell})
            grid_id += 1
        y += grid_size
    x += grid_size

grid_gdf = gpd.GeoDataFrame(grid_cells, crs="EPSG:6933")
total_grids_count = len(grid_gdf)
print(f"Total processing grids created: {total_grids_count:,}")

del grid_cells
gc.collect()

# ============================================================
# Helper Function to Extract Only Polygons from any Geometry
# ============================================================
def extract_only_polygons(geom):
    """GeometryCollection やその他のデータから Polygon / MultiPolygon のみを取り出す安全関数"""
    if geom.is_empty:
        return geom
    if geom.geom_type in ['Polygon', 'MultiPolygon']:
        return geom
    if geom.geom_type == 'GeometryCollection':
        polygons = [g for g in geom.geoms if g.geom_type in ['Polygon', 'MultiPolygon']]
        if polygons:
            return shapely.unary_union(polygons)
    return shapely.geometry.Polygon()

# ============================================================
# Core Processing Function
# ============================================================

def calculate_grid_area(gdf, category, realm):
    print("\n" + "=" * 60)
    print(f"Processing: {category} / {realm}")
    print("=" * 60)
    print(f"Total Grids to analyze: {total_grids_count:,}")

    print("Building spatial index for geometries...")
    sindex = gdf.sindex
    
    checkpoint_csv = temp_dir / f"{category}_{realm}_progress.csv"
    
    # 【変更】実行するたびに過去の進捗キャッシュファイルを完全に強制削除する
    if checkpoint_csv.exists():
        print(f"  [Reset] Removing old cache file for a fresh run: {checkpoint_csv.name}")
        checkpoint_csv.unlink()
    
    grid_results = []
    total_area_km2 = 0.0  # 常に0からスタート
    total_filtered_polygons = 0

    # グリッド単位でループ処理
    for idx, grid_row in grid_gdf.iterrows():
        grid_id = int(grid_row["grid_id"])
        grid_geometry = grid_row.geometry

        # 50グリッドごと、または最初と最後だけログを出してスッキリさせる
        is_log_step = (idx % 50 == 0) or (idx == total_grids_count - 1)
        if is_log_step:
            print(f"Progress: Grid {idx + 1:,} / {total_grids_count:,} | Running Total: {total_area_km2:,.2f} km²")

        # 1. グリッド内のマスク抽出
        mask_indices = list(mask_sindex.query(grid_geometry, predicate="intersects"))
        if not mask_indices:
            grid_results.append({"grid_id": grid_id, "area_km2": 0.0})
            continue

        local_masks = mask_gdf.geometry.iloc[mask_indices]
        clipped_masks = [
            shapely.intersection(m, grid_geometry, grid_size=1) 
            for m in local_masks if m.intersects(grid_geometry)
        ]
        
        clipped_masks = [extract_only_polygons(g) for g in clipped_masks]
        clipped_masks = [g for g in clipped_masks if not g.is_empty]
        
        if not clipped_masks:
            grid_results.append({"grid_id": grid_id, "area_km2": 0.0})
            continue
            
        local_target3_mask = shapely.union_all(clipped_masks, grid_size=1)
        local_target3_mask = extract_only_polygons(local_target3_mask)
        
        if local_target3_mask.is_empty:
            grid_results.append({"grid_id": grid_id, "area_km2": 0.0})
            del local_target3_mask
            continue

        # 2. グリッド内の WDPCA 抽出
        candidate_indices = list(sindex.query(grid_geometry, predicate="intersects"))
        if not candidate_indices:
            grid_results.append({"grid_id": grid_id, "area_km2": 0.0})
            del local_target3_mask
            continue

        local_wdpca = gdf.geometry.iloc[candidate_indices]

        # WDPCA側の面データ以外の除外フロー
        raw_count = len(local_wdpca)
        local_wdpca = local_wdpca[local_wdpca.geom_type.isin(['Polygon', 'MultiPolygon'])]
        filtered_count = raw_count - len(local_wdpca)
        total_filtered_polygons += filtered_count
        
        if filtered_count > 0 and is_log_step:
            print(f"  [Filter Status] Skipped {filtered_count:,} non-polygon geometries in this batch.")
        
        if local_wdpca.empty:
            grid_results.append({"grid_id": grid_id, "area_km2": 0.0})
            del local_target3_mask, local_wdpca
            continue

        # クリップ処理
        clipped_wdpca = []
        for geom in local_wdpca:
            if geom.intersects(local_target3_mask):
                intersected = shapely.intersection(geom, local_target3_mask, grid_size=1)
                intersected_poly = extract_only_polygons(intersected)
                if not intersected_poly.is_empty:
                    clipped_wdpca.append(intersected_poly)

        if not clipped_wdpca:
            grid_results.append({"grid_id": grid_id, "area_km2": 0.0})
            del local_target3_mask, local_wdpca
            gc.collect()
            continue

        # 3. グリッド内部の重複完全排除（セーフティネット付き）
        try:
            grid_union = shapely.union_all(clipped_wdpca, grid_size=1)
        except Exception:
            grid_union = clipped_wdpca
            for g in clipped_wdpca[1:]:
                grid_union = shapely.union(grid_union, g, grid_size=1)

        grid_union = extract_only_polygons(grid_union)

        # 4. 面積の算出 (m² -> km²)
        grid_area_km2 = grid_union.area / 1_000_000
        total_area_km2 += grid_area_km2

        grid_results.append({"grid_id": grid_id, "area_km2": grid_area_km2})

        # （念のため途中でクラッシュした時用のバックアップとしてファイルは残しますが、
        # 次回起動時には上のロジックで確実に真っさらにリセットされます）
        pd.DataFrame(grid_results).to_csv(checkpoint_csv, index=False)

        # メモリ強制解放
        del local_target3_mask, local_wdpca, clipped_wdpca, grid_union
        gc.collect()

    print(f"→ [Filter Summary] Total non-polygon geometries filtered out for {category}/{realm}: {total_filtered_polygons:,}")
    print(f"[COMPLETED] TOTAL AREA FOR {category} / {realm}: {total_area_km2:,.2f} km²")
    return total_area_km2, total_filtered_polygons

# ============================================================
# Run Category & Realm Loop
# ============================================================

categories = {
    "pa_oecm": wdpca,
    "pa_only": wdpca[wdpca["is_oecm"] == False],
    "oecm_only": wdpca[wdpca["is_oecm"] == True],
}

results = []

for category, category_gdf in categories.items():
    print(f"\n\n{'#' * 60}")
    print(f"# RUNNING CATEGORY: {category}")
    print(f"{'#' * 60}")

    terrestrial = category_gdf[category_gdf["marine"] == False]
    marine = category_gdf[category_gdf["marine"] == True]

    print(f"Terrestrial records: {len(terrestrial):,}")
    print(f"Marine records: {len(marine):,}")

    # 1. 陸域の計算
    terrestrial_area, terrestrial_filtered = calculate_grid_area(terrestrial, category, "terrestrial")

    # 2. 海域の計算
    marine_area, marine_filtered = calculate_grid_area(marine, category, "marine")

    results.append({
        "category": category,
        "terrestrial_km2": terrestrial_area,
        "terrestrial_skipped_count": terrestrial_filtered,
        "marine_km2": marine_area,
        "marine_skipped_count": marine_filtered,
    })

    del terrestrial, marine
    gc.collect()

# 最終結果保存
pd.DataFrame(results).to_csv(output_path, index=False)
print("\n" + "=" * 60)
print(f"All analysis successfully completed! Output saved to: {output_path}")
print("=" * 60)
