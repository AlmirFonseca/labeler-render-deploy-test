import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.express as px
from modules.data_reader import FirebaseReader
from modules.base_app import app, DEBUG_STATE

# ===== File Variables ===== #
reader = FirebaseReader()
dates_avaiable = reader.dates

# ===== Layout ===== #
layout = html.Div([
    # ===== Check box to toggle debug mode ===== #
    dcc.Checklist(
        id='debug-mode',
        options=[{'label': 'Debug Mode', 'value': True}],
        value=[]  # By default, the checkbox is unchecked
    ),
    html.Div(id='debug-output'),

    # ===== Date Selector ===== #
    dbc.Select(
        id='date-selector',
        options=dates_avaiable,
        value=None,
        placeholder='Select a Date'
    ),
    dbc.Button('Load', id='load-button', color='primary', outline=True),

    # === Loading === #
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div(id="loading-output"),
    ),

    # ===== Video Player ===== #
    html.H2('Video Player'),
    html.Div([
        html.Div(id='player_div'),
        dbc.Button('Previous', id='previous-button', n_clicks=0),
        dbc.Button('Play', id='play-button', n_clicks=0),
        dcc.Interval(
            id='interval-component',
            interval=200,
            n_intervals=0,
            disabled=True
        ),
        dbc.Button('Next', id='next-button', n_clicks=0)
    ], className='w-75'),
], className='d-flex flex-column align-items-center')


# ===== Callbacks ===== #
# Callback to update debug output based on the checkbox state
@app.callback(
    Output('debug-output', 'children'),
    Input('debug-mode', 'value')
)
def update_debug_output(value):
    if value:
        # If debug checkbox is checked, perform debugging actions here
        return "Debug mode is ON"
    else:
        return "Debug mode is OFF"


@app.callback(
    Output('player_div', 'children'),
    Output('loading-output', 'children'),
    Input('load-button', 'n_clicks'),
    State('date-selector', 'value'),
    State('debug-mode', 'value'),
    prevent_initial_call=True
)
def load_frames(n_clicks, date, debug_mode):
    reader.set_date(date, debug_mode)

    return [
        dcc.Graph(id='image-view'),
        html.P(list(reader.data.keys())[0], id='image-name'),
        dcc.Slider(
            id='image-slider',
            min=0,
            max=len(reader.data)-1,
            step=1,
            value=0,
            marks=None,
            dots=False,
            updatemode='drag',
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], None


@app.callback(
    Output('image-view', 'figure'),
    Output('image-name', 'children'),
    Input('image-slider', 'value'),
)
def update_image_src(slider_value):
    timestamp = list(reader.data.keys())[slider_value]
    image = reader.data[timestamp]
    fig = px.imshow(
        image,
        zmin=25,
        zmax=30,
        color_continuous_scale='thermal'
    )
    return fig, timestamp


@app.callback(
    Output('interval-component', 'disabled'),
    Output('play-button', 'children'),
    Input('play-button', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_interval(n_clicks):
    if n_clicks % 2 == 0:
        return True, 'Play'
    else:
        return False, 'Pause'


@app.callback(
    Output('image-slider', 'value'),
    Input('interval-component', 'n_intervals'),
    State('image-slider', 'value'),
)
def play(n_intervals, slider_value):
    if slider_value+1 >= len(reader.data)-1:
        return 0
    else:
        return slider_value+1
