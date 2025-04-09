import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State

# Load and clean data
df = pd.read_csv("Resources/final_crop_data.csv")
df["Rain_mm"] = pd.to_numeric(df["Rain_mm"], errors='coerce')
df = df.drop(columns=["Unnamed: 0"])

# Filter to crops of interest
crops = ['Maize', 'Potatoes', 'Rice, paddy', 'Sorghum', 'Soybeans', 'Wheat','Cassava', 'Sweet potatoes', 'Plantains and others', 'Yams']
df = df[df["Crop"].isin(crops)]

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Crop Yield by Country Over Time — v4  w/slider and button 🚀", style={"textAlign": "center"}),
        html.Div([
            # start of the top Div
            html.Div([
                html.Label("Select Crop:"),
                dcc.Dropdown(
                    id='crop-dropdown',
                    options=[{'label': crop, 'value': crop} for crop in crops],
                    value='Sorghum',
                    clearable=False
                ),
            ], style={"width" : "15%", "padding": "10px"}),

            html.Div([
                html.Label("Select Year:"),
                dcc.Slider(
                    id='year-slider',
                    min=df['Year'].min(),
                    max=df['Year'].max(),
                    step=1,
                    value=df['Year'].min(),
                    marks={str(year): str(year) for year in sorted(df['Year'].unique())},
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
            ], style={"width" : "75%", "padding": "10px"})
        ], style={
            "display": "flex",          # 👈 THIS is the key
            "width": "100%",
            "alignItems": "center",
            "justifyContent": "space-between"
        }),
            # end of the top div


    html.Div([
        html.Button("Pause Timeline", id="play-pause-btn", n_clicks=0, style={
            "width": "100%",  # make the button fill its container
            "padding": "5px"
        })
    ], style={
        "padding": "5px",
        "margin": "0 auto",       # center the container
        "width": "20%",           # control button width overall
        "textAlign": "center"     # optional: center text if needed
    }),

    dcc.Graph(id='yield-map', style={"height": "650px"}),

    #the Interval and teh Store are used to add automation functionality.
    dcc.Interval(
        id='year-interval',
        interval=1000,  # ms between steps, change to speed up/slow down
        n_intervals=0,
        disabled=False  # Set to True if you want it paused initially
    ),
    dcc.Store(id='current-year', data=df['Year'].min())

    ])


# the following will add in the start and stop functionality for the button.
@app.callback(
    Output('year-interval', 'disabled'),
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
    Output('year-slider', 'value'),
    Output('current-year', 'data'),
    Input('year-interval', 'n_intervals'),
    Input('crop-dropdown', 'value'),
    State('current-year', 'data')
)
def update_year_slider(n_intervals, selected_crop, current_year):
    # Get sorted list of years for the selected crop
    years = sorted(df[df['Crop'] == selected_crop]['Year'].unique())

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
    Output('yield-map', 'figure'),
    Input('crop-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_map(selected_crop, selected_year):
    filtered_df = df[(df["Crop"] == selected_crop) & (df["Year"] == selected_year)]

    fig = px.choropleth(
        filtered_df,
        locations="Area",
        locationmode="country names",
        color="Crop_Yield",
        hover_name="Area",
        color_continuous_scale="YlGnBu",
        labels={"Crop_Yield": "Yield (hg/ha)"},
        title=f"{selected_crop} Yield in {selected_year}"
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=False),
        coloraxis_colorbar=dict(title="Yield (hg/ha)")
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
