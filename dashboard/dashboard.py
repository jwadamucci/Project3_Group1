# Setting up necessary libraries

import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

import dash_leaflet as dl
import dash_leaflet.express as dlx
import json

import folium
from io import StringIO
import branca.colormap as cm
from shapely.geometry import shape

import numpy as np
from sklearn.linear_model import LinearRegression

# Load the data from the CSV file generated after the ETL stage of this project
df = pd.read_csv ("final_crop_data.csv")

# Load GeoJSON for choropleth map
with open("assets/world_countries.geojson", "r") as f:
    geojson_data = json.load(f)

# App setup with error suppression
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE], suppress_callback_exceptions=True)
app.title = "Crop Yield Dashboard"

# Assign colors to crops
crop_colors = {
    "Maize": "#FDB183", "Potatoes": "#C44E52", "Rice, paddy": "#55A868",
    "Sorghum": "#8172B2", "Soybeans": "#CCB974", "Sweet potatoes": "#64B5CD",
    "Wheat": "#8C564B", "Casava": "#FF9896", "Yams": "#9467BD"
}

# Analysis, precomputed 

# Detect outliers in yield values
df['is_outlier'] = ((df['yield_t_ha'] - df['yield_t_ha'].mean()) / df['yield_t_ha'].std()) > 2

# Correlation matrix
corr_matrix = df.corr(numeric_only=True).round(2)

# Average yield per crop and region
avg_yield_by_crop = df.groupby('crop')['yield_t_ha'].mean().sort_values(ascending=False).reset_index()
avg_yield_by_region = df.groupby('region')['yield_t_ha'].mean().sort_values(ascending=False).reset_index()

# Yearly yield percentage change
yearly_yield = df.groupby('year')['yield_t_ha'].mean().reset_index()
yearly_yield['% Change'] = yearly_yield['yield_t_ha'].pct_change().round(4) * 100

# Linear regression: yield ~ rainfall + temp
X = df[['rainfall_mm', 'avg_temp_c', 'pesticide_t']].dropna()
y =df.loc[X.index, 'yield_t_ha']
model = LinearRegression().fit(X, y)
r2 = model.score(X, y)
coefs = dict(zip(X.columns, model.coef_.round(3)))

# Layout of the dashboard
app.layout = dbc.Container([
    html.H1("\U0001F33E Crop Yield Dashboard", className="text-center fw-bold mb-2"),
    html.P("Use the filters below to explore crop yields across different regions, crops, and years.",
           className="text-center fw-semibold text-muted mb-4", style={"fontSize": "16px"}),

    # Filters
    dbc.Row([
        dbc.Col([html.Label("Select Region:"), dcc.Dropdown(
            options=[{"label": r, "value": r} for r in sorted(df['region'].unique())],
            id="region-dropdown", multi=True)], md=4),

        dbc.Col([html.Label("Select Crop:"), dcc.Dropdown(
            options=[{"label": c, "value": c} for c in sorted(df['crop'].unique())],
            id="crop-dropdown", multi=True)], md=4),

        dbc.Col([html.Label("Chart Theme:"), dcc.RadioItems(
            id='theme-toggle', options=[
                {'label': 'Light', 'value': 'plotly_white'},
                {'label': 'Dark', 'value': 'plotly'}],
            value='plotly_white', labelStyle={'display': 'inline-block', 'marginRight': '10px'})], md=4)      
    ], className="mb-3"),

    # Year Slider
    dbc.Row([dbc.Col([html.Label("Select Year Range:"), dcc.RangeSlider(
        min=df['year'].min(), max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],
        marks={str(y): str(y) for y in range(df['year'].min(), df['year'].max()+1, 5)},
        id='year_slider')])], className="mb-4"),

    # Summary Cards
    dbc.Row([dbc.Col(id="summary-cards")], className="mb-4"),

    # Tabs
    dbc.Tabs([
        dbc.Tab(label="\U0001F4C8 Yield Over Time", tab_id="tab-1"),
        dbc.Tab(label="\U0001F4CA Correlation Explorer", tab_id="tab-2"),
        dbc.Tab(label="\U0001F30D Regional Comparison", tab_id="tab-3"),
        dbc.Tab(label="\U0001F4CA Statistical Analysis", tab_id="tab-4"),
        dbc.Tab(label="🗺️ Choropleth Map", tab_id="tab-5"),
        dbc.Tab(label="🗺️ Folium Yield Map", tab_id="tab-6")
    ], id="tabs", active_tab="tab-1", className="mb-3"),

    # Hidden placeholder components (to register callbacks)
    html.Div([
        dcc.Dropdown(id="chart_type", style={"display": "none"}),
        dcc.Graph(id="yield-graph", style={"display": "none"}),
        html.Button("Download", id="download-btn", style={"display": "none"}),
        dcc.Download(id="download-data")
    ], style={"display": "none"}),

    html.Div(id="tab-content"),
    dcc.Store(id='shared-filters', storage_type='session')
], fluid=True)


# Yield chart updater 
@app.callback(
    Output("yield-graph", "figure"),
    [Input("chart_type", "value"),
     Input("region-dropdown", "value"),
     Input("crop-dropdown", "value"),
     Input("year_slider", "value"),
     Input("theme-toggle", "value")]
)

def update_yield_graph(chart_type, regions, crops, years, theme):
    dff = df.copy()
    if regions:
        dff = dff[dff['region'].isin(regions)]
    if crops:
        dff = dff[dff['crop'].isin(crops)]
    dff = dff[(dff['year'] >= years[0]) & (dff['year'] <= years[1])]

    if chart_type == 'bar':
        return px.bar(dff, x="year", y="yield_t_ha", color="crop", barmode="group", template=theme,
                      color_discrete_map=crop_colors)
    return px.line(dff, x="year", y="yield_t_ha", color="crop", template=theme, color_discrete_map=crop_colors)

# Download callback
@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    [State("region-dropdown", "value"),
     State("crop-dropdown", "value"),
     State("year_slider", "value")],
    prevent_initial_call=True
)
def download_filtered_data(n_clicks, regions, crops, years):
    dff = df.copy()
    if regions:
        dff = dff[dff['region'].isin(regions)]
    if crops:
        dff = dff[dff['crop'].isin(crops)]
    dff = dff[(dff['year'] >= years[0]) & (dff['year'] <= years[1])]
    return dcc.send_data_frame(dff.to_csv, "filtered_crop_data.csv")

# Callback: Render visualization and summary for each tab
@app.callback(
    [Output("tab-content", "children"), Output("summary-cards", "children")],
    [Input("tabs", "active_tab"), Input("region-dropdown", "value"),
     Input("crop-dropdown", "value"), Input("year_slider", "value"),
     Input("theme-toggle", "value")]
)
def render_tabs(tab, regions, crops, years, theme):
    dff = df.copy()
    if regions: dff = dff[dff['region'].isin(regions)]
    if crops: dff = dff[dff['crop'].isin(crops)]
    dff = dff[(dff['year']>= years[0]) & (dff['year'] <= years[1])]

    avg_y = round(dff['yield_t_ha'].mean(), 2) if not dff.empty else 0
    top_crop = dff.groupby('crop')['yield_t_ha'].mean().idxmax() if not dff.empty else "N/A"
    wettest = dff.loc[dff['rainfall_mm'].idxmax()]['year'] if not dff.empty else "N/A"

    cards = dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Avg Yield"), html.P(f"{avg_y} t/ha")])]), md=4),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Top Crop"), html.P(top_crop)])]), md=4),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Wettest Year"), html.P(wettest)])]), md=4)
    ])

    if tab == "tab-1":
        return html.Div([
            dcc.Dropdown(
                id='chart_type',
                options=[
                    {"label": "📈 Line Chart", "value": "line"},
                    {"label": "📊 Bar Chart", "value": "bar"}
                ],
                value='line', clearable=False, className="mb-3"
            ),
            dcc.Graph(id='yield-graph'),
            html.Button("💾 Download Filtered Data", id="download-btn", className="btn btn-outline-secondary mt-2"),
            dcc.Download(id="download-data")
        ]), cards
    
    elif tab == "tab-2":
        figA = px.scatter(
            dff, x="rainfall_mm", y="yield_t_ha", color="avg_temp_c",
            hover_data={'crop': True, 'year': True, 'region': True},
            template=theme, title="Rainfall vs Yield (colored by Avg Temp)"
        )

        figB = px.scatter(
            dff, x="pesticide_t", y="yield_t_ha", color="crop",
            hover_data={'region': True, 'year': True},
            template=theme, title="Pesticide Use vs Yield (by Crop)"
        )

        return html.Div([
            dbc.Row([dbc.Col(dcc.Graph(figure=figA))]),
            dbc.Row([dbc.Col(dcc.Graph(figure=figB))])
    ]), cards
    
    elif tab == "tab-3":
        dff_latest = dff[dff['year'] == years[1]]
        fig = px.bar(dff_latest, x="region", y="yield_t_ha", color="crop", template=theme,
                     barmode='group', title=f"Regional Yield in {years[1]}")
        return dcc.Graph(figure=fig), cards
    
    elif tab == "tab-4":
        fig1 = px.bar(avg_yield_by_crop, x='crop', y='yield_t_ha', title='Average Yield by Crop', template='plotly_white')
        fig2 = px.bar(avg_yield_by_region, x='region', y='yield_t_ha', title='Average Yield by Region', template='plotly_white')
        fig3 = px.line(yearly_yield, x='year', y='yield_t_ha', title='Yield Trend Over Time', template='plotly_white')
        fig4 = go.Figure(go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index,
                                    colorscale='Viridis', zmin=-1, zmax=1))
        fig4.update_layout(title='Correlation Matrix', template='plotly_white')

        outlier_count = df['is_outlier'].sum()
        regression_note = f"R2: {r2:.3f}, Coefs: {coefs}"

        return html.Div([
            dbc.Row([dbc.Col(dcc.Graph(figure=fig1))]),
            dbc.Row([dbc.Col(dcc.Graph(figure=fig2))]),
            dbc.Row([dbc.Col(dcc.Graph(figure=fig3))]),
            dbc.Row([dbc.Col(dcc.Graph(figure=fig4))]),
            html.Hr(),
            html.H5(f"Outliers Detected: {outlier_count}", className="text-danger fw-bold"),
            html.H5(regression_note, className="text-primary fw-bold"),
            html.H5("% Change is Yield by Year:", className="mt-4"),
            dbc.Table.from_dataframe(yearly_yield.tail(10), striped=True, bordered=True, hover=True)
        ]), cards
    
    elif tab == "tab-5":
        
        return html.Div([
        html.Div([
            html.Label("Select Metric:"),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[{"label": m, "value": m} for m in ['rainfall_mm', 'avg_temp_c', 'pesticide_t']],
                value="rainfall_mm", 
                clearable=False, style={"width": "300px"}
            ),
            html.Br(),
            html.Label("Select Year:"),
            
            dcc.Slider(
                id="year-slider",
                min=df['year'].min(),
                max=df['year'].max(),
                value=df['year'].max(),  # default selected year
                step=1,
                marks={str(y): str(y) for y in range(df['year'].min(), df['year'].max() + 1, 5)},
                tooltip={"placement": "bottom", "always_visible": True}
            )

        ], className="mb-3"),
        html.Iframe(id="folium-map", style={"height": "600px", "width": "100%", "border": "none"})
    ]), cards

    elif tab == "tab-6":
        m = generate_crop_yield_map(target_year=2000)  # Or make dynamic later
        map_html = m.get_root().render()

        legend = html.Div([
            html.Div([
                html.H5("Yield Legend (t/ha)", className="mb-2", style={"marginBottom": "10px"}),
                html.Div([
                    html.Div(style={"width": "20px", "height": "12px", "background": "#006837", "display": "inline-block", "marginRight": "8px"}),
                    html.Span("High")
                ]),
                html.Div([
                    html.Div(style={"width": "20px", "height": "12px", "background": "#31a354", "display": "inline-block", "marginRight": "8px"}),
                    html.Span("Medium-High")
                ]),
                html.Div([
                    html.Div(style={"width": "20px", "height": "12px", "background": "#78c679", "display": "inline-block", "marginRight": "8px"}),
                    html.Span("Medium")
                ]),
                html.Div([
                    html.Div(style={"width": "20px", "height": "12px", "background": "#c2e699", "display": "inline-block", "marginRight": "8px"}),
                    html.Span("Low-Medium")
                ]),
                html.Div([
                    html.Div(style={"width": "20px", "height": "12px", "background": "#ffffcc", "display": "inline-block", "marginRight": "8px"}),
                    html.Span("Very Low")
                ]),
                html.Div([
                    html.Div(style={"width": "20px", "height": "12px", "background": "#ff0000", "display": "inline-block", "marginRight": "8px"}),
                    html.Span("No Data", style={"color": "red", "fontWeight": "bold"})
                ])
            ], style={
                "background": "white",
                "border": "1px solid #ccc",
                "padding": "10px",
                "borderRadius": "5px",
                "boxShadow": "2px 2px 6px rgba(0,0,0,0.2)",
                "fontSize": "12px",
                "width": "180px"
            })
        ], style={
            "position": "absolute",
            "top": "100px",  # adjust as needed
            "left": "30px",  # adjust as needed
            "zIndex": "1000"
        })

        return html.Div([
            html.H4("Folium Map"),
            html.Div([
                legend,
                html.Iframe(srcDoc=map_html,
                            style={"height": "700px", "width": "100%", "border": "none"})
            ], style={"position": "relative"})  # << this wraps the map + floating items
        ]), cards


# --- Tab 5 Folium Choropleth Functions & Callback Start ---
def create_colormap_tab5(values):
    clean_values = values.dropna()
    if len(clean_values) == 0:
        return cm.LinearColormap(['#ffffff', '#ffffff'], vmin=0, vmax=1)

    # Plasma-style hex codes (manually extracted from matplotlib plasma)
    plasma_colors = [
        "#0d0887", "#6a00a8", "#b12a90", "#e16462",
        "#fca636", "#f0f921"
    ]

    return cm.LinearColormap(plasma_colors, vmin=clean_values.min(), vmax=clean_values.max())

def generate_tab5_folium_map(df, metric, target_year):
    dff = df[df['year'] == target_year].copy()
    avg_values = dff.groupby('region')[metric].mean().reset_index()
    region_value_map = dict(zip(avg_values['region'], avg_values[metric]))

    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB Positron')
    value_series = pd.Series(region_value_map.values())
    colormap = create_colormap_tab5(value_series)
    colormap.caption = f"Average {metric.replace('_', ' ').title()}"
    colormap.add_to(m)

    def style_function(feature):
        region = feature['properties']['name']
        value = region_value_map.get(region)
        return {
            'fillColor': colormap(value) if value is not None else '#d3d3d3',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    for feature in geojson_data["features"]:
        region = feature["properties"]["name"]
        feature["properties"][metric] = region_value_map.get(region)

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['name', metric],
            aliases=['Region:', f'{metric}:'],
            localize=True,
            sticky=True,
            labels=True
        )
    ).add_to(m)

    return m

@app.callback(
    Output("folium-map", "srcDoc"),
    [Input("metric-dropdown", "value"),
     Input("year-slider", "value")]
)
def update_tab5_folium_map(metric, year):
    m = generate_tab5_folium_map(df, metric=metric, target_year=year)
    return m.get_root().render()
# --- Tab 5 Folium Choropleth Functions & Callback End ---

def create_dynamic_colormap(yield_values):
    clean_values = yield_values.dropna()
    if len(clean_values) == 0:
        return cm.LinearColormap(['#ffffff'], vmin=0, vmax=1)

    return cm.LinearColormap(
        colors=['#ffffcc', '#c2e699', '#78c679', '#31a354', '#006837'],
        vmin=clean_values.min(),
        vmax=clean_values.max(),
        caption='Average Yield (t/ha)'
    )

def generate_crop_yield_map(target_year):
    dff = df[df['year'] == target_year].copy()
    if 'yield_t_ha' not in dff.columns:
        return folium.Map(location=[0, 0], zoom_start=2)

    avg_yield = dff.groupby('region')['yield_t_ha'].mean().reset_index()
    region_yield_map = dict(zip(avg_yield['region'], avg_yield['yield_t_ha']))

    m = folium.Map(
        location=[20, 0],
        zoom_start=2.3,
        min_zoom=2,
        max_zoom=4,
        tiles='CartoDB Positron',
        control_scale=True
    )

    # Lock the bounds by limiting panning area:
    m.fit_bounds([[60, -130], [-40, 160]])  # You can adjust these coordinates as needed

    yield_series = pd.Series(region_yield_map.values())
    colormap = create_dynamic_colormap(yield_series)
    colormap.add_to(m)

    def style_function(feature):
        region = feature['properties']['name']
        value = region_yield_map.get(region)
        return {
            'fillColor': colormap(value) if value else '#ff0000',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    # Inject yield values into GeoJSON properties for tooltips
    for feature in geojson_data["features"]:
        region = feature["properties"]["name"]
        feature["properties"]["yield_t_ha"] = region_yield_map.get(region)

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['name', 'yield_t_ha'],
            aliases=['Region:', 'Avg Yield (t/ha):'],
            localize=True,
            sticky=True,
            labels=True
        )
    ).add_to(m)

    return m

# Run
if __name__ == '__main__':
    app.run(debug=True)