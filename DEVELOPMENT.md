# Geospatial Biodiversity Analytics — Portfolio v1.0

## Day 1: Project Setup
- Define the research question and project objectives
- Create GitHub repository (Licence: MIT License)
- Create and activate `.venv`
- Install required geospatial libraries
- Practice basic Git workflow: add / commit / push
- Select Protected Planet as the primary data source for PAs and OECMs
- Decide to use the Protected Planet API and submit an API access request
- Select Natural Earth as the source for country boundary data
- Select the 1:10m Admin 0 – Countries dataset  

**Goal: Set up the development environment and define the research scope and data sources.**


## Day 2: Data Preparation
- Download and store Natural Earth country boundary data under `data/raw/`
- Load the Natural Earth Shapefile using GeoPandas
- Confirm 258 countries/territories and CRS (EPSG:4326)
- Visualize global country boundaries using GeoPandas and Matplotlib]
- Configure `.gitignore` for raw data, `.venv`, and system-generated files
- Commit and push the changes to GitHub  

**Goal: Load and visualize the first geospatial dataset using Python and GeoPandas.**


## Day 3: Protected Planet API Integration
- Obtain and configure Protected Planet API token
- Review API documentation and required fields
- Implement API authentication and pagination
- Test data retrieval and GeoDataFrame conversion
- Confirm batch retrieval strategy (50 records/page)  

**Goal: Establish a reliable API workflow for Protected Planet data.**

## Day 4: Large-scale Data Retrieval
- Implement batch-based API retrieval
- Retrieve 50 records per page
- Save data every 200 pages / 10,000 records
- Store intermediate data as JSON files
- Clear memory after each batch
- Complete full data retrieval

**Goal: Retrieve the full Protected Planet dataset efficiently while minimizing memory usage.**


## Day 5: Data Validation and GeoPackage Integration

- Re-run API retrieval with with_geometry=True
- Validate 320,605 records and confirm all records contain geometry
- Verify 33 JSON batch files
- Implement batch-based JSON to GeoPackage conversion
- Flatten nested API attributes for analysis
- Test GeoPackage creation with 10,000 records
- Successfully integrate all 33 batches into one GeoPackage  

**Goal: Create a validated spatial dataset in GeoPackage format for subsequent analysis.**


## Day 6: Geometry Validation and Repair

- Analyze geometry validity and identify invalid Polygon/MultiPolygon geometries
- Repair invalid geometries using make_valid()
- Extract Polygon components from repaired GeometryCollections
- Investigate geometries that could not be repaired or did not retain polygon components
- Confirm the area statistics of excluded geometries

**Goal: Prepare valid polygon geometries for reliable GIS analysis while documenting excluded records.**


## Day 7: Clean GIS Dataset Preparation

- Refine the geometry cleaning workflow and separate Polygon/MultiPolygon records for GIS analysis
- Exclude unrepaired and geometries with no Polygon / MultiPolygon components from the GIS analysis dataset
- Validate the final GIS geometries and confirm the remaining invalid geometry
- Save the cleaned dataset as cleaned_protected_planet_gis_analysis.gpkg

**Goal: Create a clean and validated polygon dataset ready for country-level and 30 by 30 analysis.**


## Day 8: Protected Area Analysis

- Calculate protected area coverage for terrestrial and marine areas
- Compare protected area coverage with the 30 by 30 target
- Aggregate protected areas by country using parent_iso3
- Analyze differences in protected area coverage across countries and regions
- Prepare analysis-ready datasets for visualization

**Goal: Quantify global and country-level progress toward the 30 by 30 target.**


## Day 9: Data Visualization

- Create a global protected area map using OpenStreetMap as the basemap
- Visualize terrestrial and marine protected areas separately
- Create country-level visualizations of protected area coverage
- Visualize progress toward the 30 by 30 target
- Prepare figures and maps for the portfolio

**Goal: Turn the analysis results into clear and compelling visualizations for the portfolio.**
