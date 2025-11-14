"""
Clients Page - Island Glass CRM v2
Step-by-step build with strict testing
"""

import dash_mantine_components as dmc
from dash import html, callback, Output, Input, State
from dash_iconify import DashIconify
from modules.database import Database
from modules.session_middleware import require_auth

print("✅ clients.py module loaded")


def layout():
    """
    Client page layout

    STEP 1.2: Add "New Client" button
    - Button in header
    - Opens modal (next step)
    - Read-only list still working
    """
    print("📄 Rendering clients page layout")

    return dmc.Stack([
        # Page header with button
        dmc.Group([
            dmc.Title("Clients", order=2),
            dmc.Button(
                "New Client",
                id="new-client-button",
                leftSection=DashIconify(icon="solar:add-circle-bold"),
                color="blue",
                variant="filled"
            )
        ], justify="space-between", align="center"),

        # Client list container
        html.Div(id="clients-list-container"),

        # Modal container (will open when button clicked)
        html.Div(id="client-modal-container")
    ], gap="md", p="md")


# STEP 1.1: Load and display clients (read-only)
@callback(
    Output("clients-list-container", "children"),
    Input("clients-list-container", "id")  # Trigger on page load
)
@require_auth
def load_clients(container_id, current_user=None):
    """
    Load and display clients

    Uses @require_auth decorator - current_user is automatically injected!
    This proves our middleware works.
    """
    print("=" * 80)
    print("🔥 load_clients callback fired!")
    print(f"   current_user: {current_user}")
    print("=" * 80)

    if not current_user:
        print("❌ No current_user - middleware failed!")
        return dmc.Alert(
            "Authentication required",
            title="Not Logged In",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )

    # Get database with user's company_id
    db = Database()

    # Get all clients for this company
    try:
        clients = db.get_all_po_clients()
        print(f"📊 Loaded {len(clients)} clients")

        if not clients:
            return dmc.Alert(
                "No clients yet. Add your first client to get started!",
                title="No Clients",
                color="blue",
                icon=DashIconify(icon="solar:info-circle-bold")
            )

        # Create simple client cards
        client_cards = []
        for client in clients:
            # Determine client name based on type
            if client.get('client_type') == 'residential':
                client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}"
            else:
                client_name = client.get('company_name', 'Unknown')

            card = dmc.Card([
                dmc.Group([
                    # Client info
                    dmc.Stack([
                        dmc.Text(client_name, size="lg", fw=600),
                        dmc.Group([
                            dmc.Badge(
                                client.get('client_type', 'unknown'),
                                color="blue"
                            ),
                            dmc.Text(
                                f"Created by: {client.get('created_by', 'NULL')}",
                                size="sm",
                                c="dimmed"
                            )
                        ], gap="xs")
                    ], gap=4)
                ])
            ], withBorder=True, radius="md", p="md", mb="sm")

            client_cards.append(card)

        return dmc.Stack(client_cards, gap="sm")

    except Exception as e:
        print(f"❌ Error loading clients: {e}")
        import traceback
        traceback.print_exc()

        return dmc.Alert(
            f"Error loading clients: {str(e)}",
            title="Error",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )


# STEP 1.2: Handle modal open/close
@callback(
    Output("client-modal-container", "children"),
    Input("new-client-button", "n_clicks"),
    prevent_initial_call=True
)
def toggle_client_modal(n_clicks):
    """
    Open modal when 'New Client' button is clicked

    For now, just a simple modal that says "Coming soon!"
    We'll add the form in the next step.
    """
    print(f"🔘 New Client button clicked! (n_clicks: {n_clicks})")

    if n_clicks:
        return dmc.Modal(
            children=[
                dmc.Stack([
                    dmc.Title("New Client", order=3),
                    dmc.Text("Client form coming in next step!", c="dimmed"),
                    dmc.Button(
                        "Close",
                        id="close-client-modal",
                        variant="light",
                        color="gray"
                    )
                ], gap="md")
            ],
            id="client-modal",
            opened=True,
            onClose=None,  # We'll handle this in next step
            size="lg",
            title="New Client"
        )

    return None


print("✅ clients.py callbacks registered")
