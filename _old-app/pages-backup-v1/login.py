"""
Login Page
User authentication with email and password
"""
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash_iconify import DashIconify
from modules.auth import AuthManager
import json

# Initialize auth manager
auth = AuthManager()

def create_login_layout():
    """Create the login page layout"""
    return dmc.Center(
        style={"minHeight": "100vh", "backgroundColor": "#f8f9fa"},
        children=dmc.Stack([
            # Logo and title
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:buildings-3-bold", width=48, color="#228be6"),
                    dmc.Stack([
                        dmc.Text(
                            "Island Glass Leads",
                            size="32px",
                            fw=700,
                            c="blue",
                            style={"lineHeight": "1"}
                        ),
                        dmc.Text(
                            "CRM System",
                            size="sm",
                            c="dimmed"
                        ),
                    ], gap=0)
                ], gap="md", justify="center")
            ], align="center", gap="xs"),

            dmc.Space(h=20),

            # Login card
            dmc.Paper([
                dmc.Stack([
                    # Title
                    dmc.Stack([
                        dmc.Text("Sign In", size="xl", fw=600),
                        dmc.Text("Enter your credentials to access the CRM", size="sm", c="dimmed"),
                    ], gap="xs", align="center"),

                    dmc.Space(h=10),

                    # Error alert container
                    html.Div(id="login-error-container"),

                    # Email input
                    dmc.TextInput(
                        id="login-email",
                        label="Email Address",
                        placeholder="your@email.com",
                        leftSection=DashIconify(icon="solar:letter-bold"),
                        size="md",
                        required=True
                    ),

                    # Password input
                    dmc.PasswordInput(
                        id="login-password",
                        label="Password",
                        placeholder="Enter your password",
                        leftSection=DashIconify(icon="solar:lock-password-bold"),
                        size="md",
                        required=True
                    ),

                    # Remember me and forgot password
                    dmc.Group([
                        dmc.Checkbox(
                            id="login-remember-me",
                            label="Remember me",
                            size="sm"
                        ),
                        dmc.Anchor(
                            "Forgot password?",
                            id="forgot-password-link",
                            size="sm",
                            href="#",
                            underline="hover"
                        )
                    ], justify="space-between"),

                    # Login button
                    dmc.Button(
                        "Sign In",
                        id="login-button",
                        fullWidth=True,
                        size="lg",
                        leftSection=DashIconify(icon="solar:login-3-bold"),
                        loading=False
                    ),

                    # Loading indicator
                    dcc.Loading(
                        id="login-loading",
                        type="default",
                        children=html.Div(id="login-status")
                    ),

                ], gap="md")
            ], p=40, withBorder=True, shadow="sm", radius="md", style={"width": "450px", "backgroundColor": "white"}),

            dmc.Space(h=10),

            # Footer
            dmc.Text(
                "© 2025 Island Glass Leads. All rights reserved.",
                size="xs",
                c="dimmed",
                ta="center"
            ),

            # Hidden stores for session management
            dcc.Store(id="login-session-store"),
            dcc.Store(id="login-redirect-trigger"),

        ], gap="md", align="center")
    )


# Full layout for when accessed directly
layout = create_login_layout()


# Callback to handle login
@callback(
    Output("login-error-container", "children"),
    Output("login-session-store", "data"),
    Output("login-button", "loading"),
    Output("login-redirect-trigger", "data"),
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    """Handle login button click"""
    if not n_clicks:
        return None, None, False, None

    # Validate inputs
    if not email or not password:
        return dmc.Alert(
            "Please enter both email and password",
            title="Missing Information",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), None, False, None

    # Attempt login
    result = auth.login(email, password)

    if result['success']:
        # Store session data
        session_data = {
            'user': result['user'],
            'session': result['session'],
            'authenticated': True
        }

        # Success - redirect will happen via another callback
        return None, session_data, False, {'redirect': True, 'timestamp': dash.callback_context.triggered[0]['value']}
    else:
        # Show error
        error_message = result.get('error', 'Login failed. Please try again.')
        return dmc.Alert(
            error_message,
            title="Login Failed",
            color="red",
            icon=DashIconify(icon="solar:close-circle-bold")
        ), None, False, None


# Callback for forgot password modal
@callback(
    Output("forgot-password-modal", "opened", allow_duplicate=True),
    Input("forgot-password-link", "n_clicks"),
    prevent_initial_call=True
)
def open_forgot_password_modal(n_clicks):
    """Open forgot password modal"""
    if n_clicks:
        return True
    return False


# Create forgot password modal (static, doesn't need to be in layout)
def create_forgot_password_modal():
    """Create forgot password modal"""
    return dmc.Modal(
        id="forgot-password-modal",
        title="Reset Password",
        children=dmc.Stack([
            dmc.Text(
                "Enter your email address and we'll send you a password reset link.",
                size="sm"
            ),
            dmc.TextInput(
                id="forgot-password-email",
                label="Email Address",
                placeholder="your@email.com",
                leftSection=DashIconify(icon="solar:letter-bold"),
            ),
            html.Div(id="forgot-password-result"),
            dmc.Group([
                dmc.Button(
                    "Cancel",
                    id="forgot-password-cancel",
                    variant="subtle",
                    color="gray"
                ),
                dmc.Button(
                    "Send Reset Link",
                    id="forgot-password-submit",
                    leftSection=DashIconify(icon="solar:letter-bold")
                )
            ], justify="flex-end")
        ], gap="md"),
        size="md"
    )


# Callback to handle password reset
@callback(
    Output("forgot-password-result", "children"),
    Output("forgot-password-modal", "opened"),
    Input("forgot-password-submit", "n_clicks"),
    Input("forgot-password-cancel", "n_clicks"),
    State("forgot-password-email", "value"),
    prevent_initial_call=True
)
def handle_password_reset(submit_clicks, cancel_clicks, email):
    """Handle password reset request"""
    ctx = dash.callback_context

    if not ctx.triggered:
        return None, True

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == "forgot-password-cancel":
        return None, False

    if triggered_id == "forgot-password-submit":
        if not email:
            return dmc.Alert(
                "Please enter your email address",
                color="red"
            ), True

        result = auth.reset_password_request(email)

        if result['success']:
            return dmc.Alert(
                "If an account exists with this email, you will receive a password reset link shortly.",
                color="green",
                icon=DashIconify(icon="solar:check-circle-bold")
            ), True
        else:
            return dmc.Alert(
                result.get('error', 'Failed to send reset email'),
                color="red"
            ), True

    return None, True
