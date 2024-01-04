import dash_bootstrap_components as dbc

from dash import Dash

DEBUG_STATE = True

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
]

app = Dash(__name__, external_stylesheets=external_stylesheets, update_title=None, suppress_callback_exceptions=True)
app.title = "Frame Labeler"