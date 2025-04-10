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
    html.H1("\U0001F33E Crop Yield Dashboard", className = "text-center fw-bold mb-2"),
    html.P("Use the filters below to explore crop yields across different regions, crops, and years.",
           className = "text-center fw-semibold text-muted mb-4", style={"fontSize": "16px"}),

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
    ],  className="mb-3"),

    # Year Slider
    dbc.Row([dbc.Col([html.Label("Select Year Range:"), dcc.RangeSlider(
        min=df['year'].min(), max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],
        marks={str(y): str(y) for y in range(df['year'].min(), df['year'].max()+1, 5)},
        id='year_slider')])], className="mb_4"),

    # Summary Cards
    dbc.Row([dbc.Col(id="summary-cards")], className="mb-4"),

    # Tabs
    dbc.Tabs([
        dbc.Tab(label="\U0001F4C8 Yield Over Time", tab_id="tab-1"),
        dbc.Tab(label="\U0001F4CA Correlation Explorer", tab_id="tab-2"),
        dbc.Tab(label="\U0001F30D Regional Comparison", tab_id="tab-3"),
        dbc.Tab(label="\U0001F4CA Statistical Analysis", tab_id="tab-4"),
        dbc.Tab(label="🗺️ Choropleth Map", tab_id="tab-5"),
        dbc.Tab(label="🗺️ Folium Yield Map", tab_id="tab-6"),
        dbc.Tab(label="🗺️ Crop Yield Over Time Map", tab_id="tab-7")
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

  ##_________________INSERTED DEVIN'S CDOE FOR TAB 5 BELOW___________________________  
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

##_________________INSERTED DEVIN'S CDOE FOR TAB 5 ABOVE___________________________
    
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

#________________JWA TAB ODE IS BELOW THIS LINE_____________________

    elif tab == "tab-7":
        
        # Use fallback values if inputs are missing
        selected_crops = crops if crops else df['crop'].unique()
        min_year = df['year'].min()
        max_year = df['year'].max()
        year_marks = {str(year): str(year) for year in range(min_year, max_year + 1, 5)}

        return html.Div([
            html.H1("Crop Yield by Country Over Time 🚀", style={"textAlign": "center"}),

            # Top filters
            html.Div([
                html.Div([
                    html.Label("Select Crop:"),
                    dcc.Dropdown(
                        id='crop-dropdown-tab7',  # <-- unique ID
                        options=[{'label': crop, 'value': crop} for crop in selected_crops],
                        value=selected_crops[0] if isinstance(selected_crops, (list, np.ndarray)) else selected_crops,
                        clearable=False
                    ),
                ], style={"width": "20%", "padding": "10px"}),

                html.Div([
                    html.Label("Select Year:"),
                    dcc.Slider(
                        id='year-slider-tab7',  # <-- unique ID
                        min=min_year,
                        max=max_year,
                        step=1,
                        value=min_year,
                        marks=year_marks,
                        tooltip={"placement": "bottom", "always_visible": False}
                    ),
                ], style={"width": "75%", "padding": "10px"})
            ], style={
                "display": "flex",
                "width": "100%",
                "alignItems": "center",
                "justifyContent": "space-between"
            }),

            # Play/Pause button
            html.Div([
                html.Button("Pause Timeline", id="play-pause-btn", n_clicks=0, style={
                    "width": "100%",
                    "padding": "5px"
                })
            ], style={
                "padding": "5px",
                "margin": "0 auto",
                "width": "20%",
                "textAlign": "center"
            }),

            # Map display
            dcc.Graph(id='yield-map-tab7', style={"height": "650px"}),

            # Animation tools
            dcc.Interval(
                id='year-interval-tab7',
                interval=1000,
                n_intervals=0,
                disabled=False
            ),
            dcc.Store(id='current-year-tab7', data=min_year)
        ]), cards

#________________JWA TAB CODE IS ABOVE THIS LINE_____________________


@app.callback(
    Output("geojson-layer", "data"),
    [Input("year-slider", "value"), Input("metric-dropdown", "value")]
)
def update_choropleth(year, metric):
    dff = df[df['year'] == year]
    region_metric = dff.groupby("region")[metric].mean().dropna()
    min_val, max_val = region_metric.min(), region_metric.max()

    def get_color(val):
        if pd.isna(val): return "#ccc"
        pct = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
        return (
            "#ffffcc" if pct < 0.2 else
            "#a1dab4" if pct < 0.4 else
            "#41b6c4" if pct < 0.6 else
            "#2c7fb8" if pct < 0.8 else
            "#253494"
        )

    features = []
    for feature in geojson_data["features"]:
        name = feature["properties"]["name"]
        val = region_metric.get(name)
        color = get_color(val)
        feature["properties"]["style"] = {
            "fillColor": color, "color": "black", "weight": 1, "fillOpacity": 0.8
        }
        feature["properties"]["popup"] = f"{name}<br>{metric}: {val:.2f}" if val else f"{name}: No data"
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}

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

    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB Positron')

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

#______________________JWA callback code follows this line:_________________

# the following will add in the start and stop functionality for the button.
@app.callback(
    Output('year-interval-tab7', 'disabled'),
    Output('play-pause-btn', 'children'),
    Input('play-pause-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_animation(n_clicks):
    # Toggle logic: even clicks = play, odd = pause
    paused = n_clicks % 2 != 0
    button_text = "Play Timeline" if paused else "Pause Timeline"
    return paused, button_text

## begin add-ons (along with Interval and Store) teh callback and update for the slider
@app.callback(
    Output('year-slider-tab7', 'value'),
    Output('current-year-tab7', 'data'),
    Input('year-interval-tab7', 'n_intervals'),
    Input('crop-dropdown-tab7', 'value'),
    State('current-year-tab7', 'data')
)
def update_year_slider(n_intervals, selected_crop, current_year):
    # Get sorted list of years for the selected crop
    years = sorted(df[df['crop'] == selected_crop]['year'].unique())

    if not years:
        return dash.no_update, dash.no_update

    # Loop back to the start when at the end
    try:
        next_index = (years.index(current_year) + 1) % len(years)
    except ValueError:
        next_index = 0

    next_year = years[next_index]
    return next_year, next_year

@app.callback(
    Output('yield-map-tab7', 'figure'),
    Input('crop-dropdown-tab7', 'value'),
    Input('year-slider-tab7', 'value')
)
def update_map(selected_crop, selected_year):
    filtered_df = df[(df["crop"] == selected_crop) & (df["year"] == selected_year)]

    fig = px.choropleth(
        filtered_df,
        locations="region",
        locationmode="country names",
        color="yield_hg_ha",
        hover_name="region",
        color_continuous_scale="YlGnBu",
        labels={"Crop_Yield": "Yield (hg/ha)"},
        title=f"{selected_crop} Yield in {selected_year}"
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=False),
        coloraxis_colorbar=dict(title="Yield (hg/ha)")
    )

    return fig

# ^^^^^^^^  JWA callback code is above this line. ^^^^^^

#________________ADDDED DEVIN'S CALLBACK CODE BELOW_______________________

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

#________________ADDED DEVIN'S CALLBACK CODE ABOVE________________________


# Run
if __name__ == '__main__':
    app.run(debug=True)
