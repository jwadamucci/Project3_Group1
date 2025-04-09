# Crop Yield Analysis and Visualization Tools

## Overview
This repository houses a comprehensive solution for analyzing global agricultural efficiency and environmental impact. By combining GeoJSON-based spatial visualizations and statistical insights, the tools empower users to explore crop yield trends, assess environmental factors such as rainfall and temperature deviations, and uncover quantitative metrics driving agricultural performance across regions and timeframes.

## Features

### Interactive Map-Based Visualization
* **Data Processing**
   * Utilizes Python (pandas) for enriching GeoJSON files with crop yield metrics.
   * Handles missing values, standardizes geographic data, and computes yield efficiency.
* **Interactive Map Creation**
   * Built with Folium to display yield efficiency through markers, choropleth layers, and tooltips.
   * Includes basemap styles (Standard, Satellite, Terrain) and layer controls for enhanced interactivity.
* **Environmental Impact Analysis**
   * Visualizes the influence of temperature deviations, rainfall, and pesticide usage on yields.

### Statistical Insight Dashboard
* **Data Processing**
   * Applies cleaning methods and statistical techniques to prepare data for analysis.
   * Handles outliers, computes average yields, and calculates yearly percent changes.
* **Statistical Analysis**
   * Includes linear regression modeling, correlation analysis, and outlier detection.
   * Provides coefficients and R² scores for statistical understanding.
* **Interactive Visualizations**
   * Dynamic filters for crops, regions, and year ranges.
   * Chart toggles (line, bar, scatter) and downloadable filtered data.

## Implementation Details

### Tech Stack
* **Backend**
   * Python with pandas, Folium, Dash, and Sklearn.
   * Spatial data representation using GeoJSON.
* **Visualization Tools**
   * Folium for maps and overlays.
   * Plotly and Dash for interactive charts and dashboards.

### Repository Structure

```
project_root/
├── Cleaned
│   ├── final_crop_data.csv        # Cleaned crop yield dataset after processing, ready for visualization and analysis.
│   └── yield_map.html             # Interactive map displaying agricultural metrics, created with Folium.
├── crop_data_schema.sql           # SQL schema defining the structure of crop yield database tables.
├── dashboard
│   ├── assets
│   │   ├── choropleth.html        # Template for generating choropleth visualizations of agricultural data.
│   │   ├── choropleth.js          # JavaScript code for customizing the choropleth layer interactions.
│   │   ├── custom_updated.geo.json # GeoJSON file enriched with agricultural and environmental data.
│   │   └── world_countries.geojson # Base GeoJSON file containing geographic data for country boundaries.
│   ├── dashboard.py               # Python script for running the interactive crop yield dashboard.
│   ├── final_crop_data.csv        # Cleaned and formatted dataset for dashboard use.
│   └── Visualizations_Gurpreet.ipynb # Jupyter Notebook for generating maps, charts, and statistical summaries.
├── data_cleanup.ipynb             # Jupyter Notebook containing data cleaning workflows, including handling missing values and outliers.
├── README.md                      # Documentation of the project, including usage instructions and features.
└── Resources
    ├── pesticides.csv             # Dataset of pesticide usage metrics across regions and time.
    ├── rainfall.csv               # Dataset with rainfall data relevant to crop yield analysis.
    ├── temp.csv                   # Temperature dataset with anomalies and deviations over time.
    ├── yield_df.csv               # Processed yield data for integration into GeoJSON and dashboard visualizations.
    └── yield.csv                  # Alternative yield data format used in some analyses.

```

## Usage
1. Clone the repository:
```bash
git clone <https://github.com/jwadamucci/Project3_Group1.git>
```

2. Navigate to the repository:
```bash
cd Project3_Group1
```

3. Explore the Interactive Map-Based Visualization:
   * Open `yield_map.html` in your browser.

4. Run the Statistical Insight Dashboard:
   * Set up the environment and start the Dash app:
```bash
python dashboard.py
```

## Resources
* Dash Plotly Documentation
* Folium and Dash libraries for interactive visualizations.
* pandas and Sklearn for data manipulation and statistical analysis.
* GeoJSON for spatial data representation.

## Credits
* Folium and Dash for interactive visualization libraries.
* pandas and Sklearn for data manipulation and analysis.
* Microsoft Copilot for ideation and guidance.
