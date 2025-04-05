# Project3_Group1
# Crop Yield Global Visualization

## Overview
The **Crop Yield Global Visualization** project is an interactive data visualization tool focused on global agricultural metrics. By integrating crop yield and environmental data into GeoJSON files, this project provides an intuitive platform for exploring agricultural efficiency and environmental impacts through interactive maps.

## Background
This project bridges the gap between complex agricultural datasets and actionable insights. It visualizes crop yields, pesticide usage, rainfall, temperature deviations, and efficiency metrics to help users better understand the factors driving agricultural performance across different regions and time periods.

## Implementation Details

### Crop Yield Data Processing
#### Data Integration
* **Technology:** Python with `pandas`
* **Data Source:** User-provided datasets (see `Resources` folder)
* **Functionality:** Enriches GeoJSON files with agricultural metrics for geographic representation

### Interactive Map Creation
#### Visualization Features
* **Library:** Folium
* **Marker Representation:**
   * Yield efficiency with size-based markers
   * Color-coded layers for additional clarity
* **Hover Tooltips:** Display detailed metrics dynamically
* **Year Filter:** Allows focused exploration of specific years
* **Choropleth Layers:** Highlight agricultural data distribution and spatial patterns

#### Map Layers and Controls
* **Basemap Styles:**
   * Standard Map
   * Satellite View
   * Terrain Map
* **Legend:**
   * Comprehensive color-coding explanations for yield efficiency and environmental factors
* **Interactive Elements:**
   * Detailed popups and hover-over insights for specific data points

#### Environmental Impact Analysis
* Visualization of temperature deviations, rainfall, and pesticide usage impacts on yields

## Features
### Interactive Elements
* **Layer Controls:** Toggle between different basemap styles and data overlays
* **Hover and Click:** Explore detailed regional information
* **Dynamic Updates:** Filter and display data based on selected metrics and timeframes

### Visualizations
* **Agricultural Metrics:** Choropleth layers and dynamic markers for crop yield data
* **Environmental Factors:** Overlay data for rainfall, temperature, and pesticide usage

## Tech Stack
### Backend:
* Python
   * Libraries: pandas, Folium, JSON

### Visualization:
* Folium (Interactive Maps)
* GeoJSON (Spatial Data Representation)

## Data Sources
* **Crop Yield Data:** Available in `Resources/crop_yields.csv`
* **Environmental Data:** Includes rainfall, temperature, and pesticide datasets (see `Resources` folder)

## Repository Structure
```
CROP-YIELD-VISUALIZATION
├── README.md
├── Resources
│   ├── crop_yields.csv
│   ├── environmental_factors.csv
│   ├── final_crop_data.csv
│   ├── pesticides.csv
│   ├── rainfall.csv
│   ├── temp.csv
│   ├── yield.csv
│   └── yield_df.csv
├── SQL
│   ├── crop.sql
│   └── crop_data-sql.csv
├── Screenshot 2025-04-02 at 11.02.52 PM.png
├── Visualizations_Gurpreet.ipynb
├── crop_yield_map_with_markers.html
├── crop_yields_Gurpreet.ipynb
├── custom.geo.json
└── custom_updated.geo.json

3 directories, 17 files
```

## Usage
1. Navigate to the repository directory:
```bash
cd Crop-Yield-Visualization
```

2. Place the required datasets in the `Resources/` folder.
3. Open the `crop_yield_map_with_markers.html` file in your browser to explore the visualization.

## Credits
### Data Sources
* Crop yield and environmental data provided in the `Resources` folder

### Acknowledgments
* Folium and pandas for their powerful libraries
* Microsoft Copilot for ideation and guidance
