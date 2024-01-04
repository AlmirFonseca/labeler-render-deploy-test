from dash import html
from components import video_player, frames_labeler
from modules.base_app import app, DEBUG_STATE

server = app.server

app.layout = html.Div([
    video_player.layout,
    frames_labeler.layout
])

if __name__ == "__main__":
    app.run_server(debug=DEBUG_STATE)