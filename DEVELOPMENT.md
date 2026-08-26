# Geospatial Biodiversity Analytics — Portfolio v1.0
## Day 1: Development Environment & Project Design
- Create GitHub repository (Licence: MIT License)
- Confirm Python version (3.12.2)
- Create and activate `.venv`
- Confirm Python execution in VS Code
- Practice basic Git workflow: add / commit / push
- Define Project 01
- Define the research question and objectives
- Select Protected Planet as the primary data source for PAs and OECMs
- Decide to use the Protected Planet API and submit an API access request
- Select Natural Earth as the source for country boundary data
- Select the 1:10m Admin 0 – Countries dataset
Goal: Set up the development environment and define the research scope and data sources.

## Day 2: Geospatial Data Loading & Visualization
- Download and store Natural Earth country boundary data under `data/raw/`
- Install GeoPandas and Matplotlib
- Load the Natural Earth Shapefile using GeoPandas
- Confirm 258 countries/territories and CRS (EPSG:4326)
- Visualize global country boundaries using GeoPandas and Matplotlib
- Configure `.gitignore` for raw data, `.venv`, and system-generated files
- Commit and push the changes to GitHub
Goal: Load and visualize the first geospatial dataset using Python and GeoPandas.

## Day 3: Protected Planet API Integration
- Obtain and configure Protected Planet API token
- Review API documentation and required fields
- Implement API authentication and pagination
- Test data retrieval and GeoDataFrame conversion
- Confirm batch retrieval strategy (50 records/page)
Goal: Establish a reliable API workflow for Protected Planet data.

## Day 4: Large-scale Data Retrieval
- Retrieve approximately 320,000 protected areas
- Save data every 100 pages / 5,000 records
- Store intermediate files in a lightweight geospatial format
- Add progress logging and error handling
Goal: Safely retrieve and store the full dataset with limited memory usage.

## Day 5: Data Integration & Preprocessing
- Combine intermediate files into a GeoPackage
- Check geometry validity and CRS
- Filter relevant protected areas (legal_status = Designated)
- Separate terrestrial and marine areas
- Check duplicates and missing values
- Prepare data for spatial analysis
Goal: Create a clean, analysis-ready dataset.

## Day 6: 30 by 30 Spatial Analysis
- Resolve overlapping protected areas
- Calculate global protected area coverage
- Calculate terrestrial and marine coverage
- Calculate country-level coverage
- Compare coverage with the 30 by 30 target
Goal: Quantify progress toward the 30 by 30 target.

## Day 7: Visualization & Portfolio
- Create global protected area maps
- Visualize country-level coverage
- Create charts for 30 by 30 progress
- Add OpenStreetMap as a background map
- Update README and development notes

Goal: Present the analysis results as a clear and reproducible portfolio project.