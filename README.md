# **Project3_Group1**
# **Crop Yield Global Visualization**

## **Overview**
The **Crop Yield Global Visualization** project is an interactive data visualization tool focused on global agricultural metrics. By integrating crop yield and environmental data into GeoJSON files, this project provides an intuitive platform for exploring agricultural efficiency and environmental impacts through interactive maps.

## **Background**
This project bridges the gap between complex agricultural datasets and actionable insights. It visualizes crop yields, pesticide usage, rainfall, temperature deviations, and efficiency metrics to help users better understand the factors driving agricultural performance across different regions and time periods.

## **Implementation Details**

### **Crop Yield Data Processing**
#### **Data Integration**
* **Technology:** Python with `pandas`
* **Data Source:** User-provided datasets (see `Resources` folder)
* **Functionality:** Enriches GeoJSON files with agricultural metrics for geographic representation

### **Interactive Map Creation**
#### **Visualization Features**
* **Library:** Folium
* **Marker Representation:**
   * Yield efficiency with size-based markers
   * Color-coded layers for additional clarity
* **Hover Tooltips:** Display detailed metrics dynamically
* **Year Filter:** Allows focused exploration of specific years
* **Choropleth Layers:** Highlight agricultural data distribution and spatial patterns

#### **Map Layers and Controls**
* **Basemap Styles:**
   * Standard Map
   * Satellite View
   * Terrain Map
* **Legend:**
   * Comprehensive color-coding explanations for yield efficiency and environmental factors
* **Interactive Elements:**
   * Detailed popups and hover-over insights for specific data points

### **Environmental Impact Analysis**
* Visualization of temperature deviations, rainfall, and pesticide usage impacts on yields

## **Features**

### **Interactive Elements**
* **Layer Controls:** Toggle between different basemap styles and data overlays
* **Hover and Click:** Explore detailed regional information
* **Dynamic Updates:** Filter and display data based on selected metrics and timeframes

### **Visualizations**
* **Agricultural Metrics:** Choropleth layers and dynamic markers for crop yield data
* **Environmental Factors:** Overlay data for rainfall, temperature, and pesticide usage

## **Tech Stack**

### **Backend:**
* Python
   * Libraries: pandas, Folium, JSON

### **Visualization:**
* Folium (Interactive Maps)
* GeoJSON (Spatial Data Representation)

## **Data Sources**
* **Crop Yield Data:** Available in `Resources/crop_yields.csv`
* **Environmental Data:** Includes rainfall, temperature, and pesticide datasets (see `Resources` folder)

## **Repository Structure**

```
project_root/
├── Data_Processing/ # Data preparation workflows
│   ├── crop_yields_Gurpreet.ipynb # [Jupyter Notebook] Main data cleaning pipeline:
│   │   # - Handles missing values
│   │   # - Standardizes country names
│   │   # - Calculates yield efficiency metrics
│   │
│   └── yield_df.csv # [Processed Data] Output from cleaning pipeline:
│       # - 150+ countries
│       # - 2000-2020 temporal coverage
│       # - 12 crop types
│
├── Visualizations/ # Mapping and analysis outputs
│   ├── Visualizations_Gurpreet.ipynb # [Jupyter Notebook] Creates:
│   │   # - Interactive Folium maps
│   │   # - Comparative charts
│   │   # - Statistical summaries
│   │
│   ├── crop_yield_map_enhanced.html # [HTML Export] Interactive map features:
│   │   # - Layer controls
│   │   # - Dynamic tooltips
│   │   # - Year filtering
│   │
│   └── Screenshot*.png # [Image Files] Sample visualizations:
│       # 1. Choropleth_map_2020.png
│       # 2. Efficiency_scatterplot.png
│       # 3. Climate_correlation.png
│
├── Resources/ # Original and intermediate datasets
│   ├── crop_yields.csv # [Primary Data] Raw yield metrics:
│   │   # - Columns: Country,Year,CropType,Yield
│   │
│   ├── environmental_factors.csv # [Climate Data] Contains:
│   │   # - Temperature anomalies
│   │   # - Precipitation levels
│   │   # - Growing season length
│   │
│   ├── pesticides.csv # [Agricultural Inputs]
│   ├── rainfall.csv # [Climate Metrics]
│   ├── temp.csv # [Temperature Data]
│   └── yield.csv # [Alternative Yield Format]
│
├── GeoJSON/ # Spatial data components
│   ├── custom.geo.json # [Base Geography] Contains:
│   │   # - Country boundaries
│   │   # - Standard ISO codes
│   │
│   └── custom_updated.geo.json # [Enhanced Data] Merges:
│       # - Geographic features
│       # - Agricultural metrics
│       # - Environmental indicators
│
├── SQL/ # Database management
│   ├── crop.sql # [Schema Definition] Creates:
│   │   # - Tables structure
│   │   # - Indexes
│   │   # - Relationships
│   │
│   └── crop_data-sql.csv # [Query Output] Exported results:
│       # - Joined tables
│       # - Filtered records
│       # - Calculated fields
│
└── README.md # Project documentation
```

## **Usage**
1. Navigate to the repository directory:
   ```bash
   cd PROJECT3_GROUP1
   ```
2. Place the required datasets in the `Resources/` folder.
3. Open the `crop_yield_map_with_markers.html` file in your browser to explore the visualization.

## **Credits**

### **Data Sources**
* Crop yield and environmental data provided in the `Resources` folder

### **Acknowledgments**
* Folium and pandas for their powerful libraries
* Microsoft Copilot for ideation and guidance
