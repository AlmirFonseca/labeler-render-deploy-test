import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.express as px
from modules.data_reader import FirebaseReader
from modules.labels import Labels
from modules.base_app import app, DEBUG_STATE

# ===== File Variables ===== #
reader = FirebaseReader()
dates_avaiable = reader.dates
labels = Labels('data/labels.json')

# ===== Labels Display ===== #
def get_labels_display(labels_data: list[tuple[str, str, str]]) -> list[html.Div]:
    labels_data = labels.data
    labels_display = []
    for label in labels_data:
        labels_display.append(dbc.Badge(f'{label[0]} - {label[1]}: {label[2]}', color='primary'))
    if len(labels_display) == 0:
        labels_display = 'No Labels selected'
    return labels_display

# ===== Layout ===== #
layout = html.Div([
    html.Div([
        html.H2('Frames Labeler'),
        # ===== Labels ===== #
        html.Div([
            html.P(get_labels_display(labels.data), id='labels-display'),
        ]),
        html.Br(),
        dbc.Button('Add Label', id='add-label-button', color='primary', outline=True),
        # ===== Frames Viewer ===== #
        html.Div([
            html.Div(id='interval_frames_div'),
            dbc.Select(
                id='labels-select',
                options=[
                    {'label': 'Decúbito Dorsal: DD', 'value': 'DD'},
                    {'label': 'Decúbito Lateral Direito: DLD', 'value': 'DLD'},
                    {'label': 'Decúbito Lateral Esquerdo: DLE', 'value': 'DLE'},
                ],
                value=None,
                placeholder='Select a Label'
            ),
            html.Div([], id='submit-button-output'),
            dbc.Button('Submit', id='submit-button', color='primary'),
        ], id='frames-viewer', className='hidden'),
    ], className='w-75'),
], className='d-flex flex-column align-items-center')

# ===== Callbacks ===== #
@app.callback(
    Output('initial-frame-view', 'figure'),
    Output('initial-frame-name', 'children'),
    Output('final-frame-view', 'figure'),
    Output('final-frame-name', 'children'),
    Input('range-frames-slider', 'value'),
)
def update_frames_view(slider_value):
    initial_timestamp = list(reader.data.keys())[slider_value[0]]
    initial_image = reader.data[initial_timestamp]
    final_timestamp = list(reader.data.keys())[slider_value[1]]
    final_image = reader.data[final_timestamp]
    initial_fig = px.imshow(
        initial_image,
        zmin=25,
        zmax=30,
        color_continuous_scale='thermal',
    )
    final_fig = px.imshow(
        final_image,
        zmin=25,
        zmax=30,
        color_continuous_scale='thermal',
    )
    return initial_fig, initial_timestamp, final_fig, final_timestamp


@app.callback(
    Output('interval_frames_div', 'children'),
    Input('load-button', 'n_clicks'),
    State('date-selector', 'value'),
    State('debug-mode', 'value'),
    prevent_initial_call=True
)
def load_frames(n_clicks, date, debug_mode):
    reader.set_date(date, debug_mode)
    return [
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.H2('Initial Frame'),
                    dcc.Graph(id='initial-frame-view'),
                    html.P(list(reader.data.keys())[0], id='initial-frame-name'),
                ], width=6),
                dbc.Col([
                    html.H2('Final Frame'),
                    dcc.Graph(id='final-frame-view'),
                    html.P(list(reader.data.keys())[0], id='final-frame-name'),
                ], width=6),
            ]),
            dcc.RangeSlider(
                id='range-frames-slider',
                min=0,
                max=len(reader.data)-1,
                step=1,
                value=[0, 0],
                marks=None,
                dots=False,
                updatemode='drag',
                tooltip={"placement": "bottom", "always_visible": True}
            )], id='interval_frames_div')
    ]


@app.callback(
    Output('frames-viewer', 'className'),
    Input('add-label-button', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_frames_viewer(n_clicks):
    if n_clicks % 2 == 0:
        return 'hidden'
    else:
        return 'visible'


@app.callback(
    Output('labels-display', 'children'),
    Output('submit-button-output', 'children'),
    Input('submit-button', 'n_clicks'),
    State('labels-select', 'value'),
    State('range-frames-slider', 'value'),
    prevent_initial_call=True
)
def add_label(n_clicks, label, slider_value):
    feedback = ...
    initial_timestamp = int(list(reader.data.keys())[slider_value[0]])
    final_timestamp = int(list(reader.data.keys())[slider_value[1]])
    try:
        labels.add_label((initial_timestamp, final_timestamp, label))
        feedback = dbc.Alert('Label added successfully', color='success')
    except ValueError as e:
        feedback = dbc.Alert(str(e), color='danger')
    # Convert labels data to string
    return get_labels_display(labels.data), feedback