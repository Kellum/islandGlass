"""
Island Glass Leads CRM - v2 (Complete Rebuild)
Clean architecture with proper session management
"""

import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_mantine_components as dmc
from flask import Flask
import os

# Import pages (we'll add more as we build them)
from pages import login, clients

# Initialize Flask server with session support
server = Flask(__name__)
server.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
server.config['SESSION_TYPE'] = 'filesystem'

# Initialize Dash app
app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    title="Island Glass Leads CRM",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ]
)

# Clean, modern theme
app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "violet",
        "fontFamily": "Inter, sans-serif",
        "defaultRadius": "md",
    },
    children=[
        # URL routing
        dcc.Location(id='url', refresh=False),

        # Main content container
        html.Div(id='page-content')
    ]
)


@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page(pathname):
    """
    Simple routing - no complex auth checking here

    Each page will handle its own auth requirements using @require_auth decorator
    """
    print(f"📍 Routing to: {pathname}")

    if pathname == '/login':
        # Handle both layout() function and layout variable
        return login.layout() if callable(login.layout) else login.layout

    elif pathname == '/clients':
        return clients.layout()

    elif pathname == '/' or pathname is None:
        # Default: show clients page
        return clients.layout()

    # Unknown route: redirect to login
    return login.layout()


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Island Glass Leads CRM v2 - Starting")
    print("=" * 80)
    print("📊 Running on: http://localhost:8050")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=8050)
