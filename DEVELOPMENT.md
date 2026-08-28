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

## Day 6: 30 by 30 Spatial Analysis
- Resolve overlapping protected areas
- Calculate global protected area coverage
- Calculate terrestrial and marine coverage
- Calculate country-level coverage
- Compare coverage with the 30 by 30 target
**Goal: Quantify progress toward the 30 by 30 target.**

## Day 7: Visualization & Portfolio
- Create an interactive global protected area map
- Visualize country-level coverage
- Create charts for 30 by 30 progress
- Add OpenStreetMap as a background map
- Deploy the interactive map online
- Update README and development notes
**Goal: Visualize and communicate the analysis results.**