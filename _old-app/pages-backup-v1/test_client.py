"""
Test Client Page - Minimal Implementation to Prove Pattern

Purpose: Prove that we can:
1. Access user_id reliably via hidden div
2. Create modal with working callback
3. Insert to database with audit trail
4. Refresh list after insert

This is a MINIMAL test - no complexity, just prove the pattern works.
"""

print("=" * 80)
print("DEBUG: test_client.py module is being imported!")
print("=" * 80)

from dash import html, callback, Output, Input, State, ctx, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from modules.database import Database


def layout(session_data=None):
    """
    Test client page layout - MINIMAL version

    Pattern:
    - Layout is a FUNCTION (not static variable)
    - Hidden div stores user_id from session
    - Single modal with one field
    - Simple list display
    """

    return dmc.Stack([
        # Page Header
        dmc.Group([
            dmc.Title("Test Client Page", order=2),
            dmc.Button(
                "Add Test Client",
                id="open-test-modal-btn",
                leftSection=DashIconify(icon="solar:add-circle-bold"),
                color="blue"
            )
        ], justify="space-between"),

        # Note: user_id comes from 'user-id-hidden-div' in dash_app.py (synced from session-store)
        # We reference it in callbacks via State('user-id-hidden-div', 'children')

        # Notification container
        html.Div(id="test-notification-container"),

        # Client list container
        html.Div(id="test-client-list-container"),

        # Add Test Client Modal
        dmc.Modal(
            id="test-client-modal",
            title="Add Test Client (Minimal)",
            size="md",
            children=[
                dmc.Stack([
                    # Single field - client name
                    dmc.TextInput(
                        id="test-client-name",
                        label="Client Name",
                        placeholder="Enter client name",
                        required=True
                    ),

                    # Action buttons (ONLY 2!)
                    dmc.Group([
                        dmc.Button(
                            "Cancel",
                            id="test-cancel-btn",
                            variant="subtle",
                            color="gray"
                        ),
                        dmc.Button(
                            "Submit",
                            id="test-submit-btn",
                            color="blue",
                            leftSection=DashIconify(icon="solar:check-circle-bold")
                        )
                    ], justify="flex-end")
                ], gap="md")
            ]
        )
    ], gap="md")


# =============================================================================
# CALLBACKS
# =============================================================================

print("DEBUG: About to register test_client callbacks...")

@callback(
    Output("test-client-modal", "opened"),
    Input("open-test-modal-btn", "n_clicks"),
    Input("test-cancel-btn", "n_clicks"),
    State("test-client-modal", "opened"),
    prevent_initial_call=True
)
def toggle_test_modal(open_clicks, cancel_clicks, is_opened):
    """Toggle test modal open/closed"""
    print(f"🎯 toggle_test_modal fired! triggered_id: {ctx.triggered_id}")
    triggered_id = ctx.triggered_id

    if triggered_id == "open-test-modal-btn":
        return True
    elif triggered_id == "test-cancel-btn":
        return False

    return is_opened


@callback(
    Output("test-client-modal", "opened", allow_duplicate=True),
    Output("test-client-list-container", "children"),
    Output("test-notification-container", "children"),
    Input("test-submit-btn", "n_clicks"),
    State("test-client-name", "value"),
    State("user-id-hidden-div", "children"),  # Get user_id from hidden div (synced in dash_app.py)
    prevent_initial_call=True
)
def submit_test_client(n_clicks, client_name, user_id):
    """
    Submit test client - MINIMAL implementation

    This proves:
    1. Callback fires
    2. user_id is accessible via hidden div
    3. Database insert works with audit trail
    4. Modal closes and list refreshes
    """

    print("=" * 80)
    print(f"🔥 TEST CLIENT CALLBACK FIRED!")
    print(f"   n_clicks: {n_clicks}")
    print(f"   client_name: {client_name}")
    print(f"   user_id: {user_id}")
    print("=" * 80)

    # Validation
    if not client_name:
        return no_update, no_update, dmc.Notification(
            title="Validation Error",
            message="Client name is required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    # Insert to database
    try:
        db = Database()

        client_data = {
            'client_type': 'residential',  # Default for test
            'first_name': client_name.split()[0] if client_name else 'Test',
            'last_name': ' '.join(client_name.split()[1:]) if len(client_name.split()) > 1 else 'Client',
        }

        print(f"📝 Inserting test client: {client_data}")
        print(f"📝 With user_id: {user_id}")

        result = db.insert_po_client(client_data, user_id=user_id)

        if result:
            print(f"✅ Test client inserted successfully: {result.get('id')}")

            # Create success notification
            success_notification = dmc.Notification(
                title="Success!",
                message=f"Test client '{client_name}' created successfully",
                color="green",
                icon=DashIconify(icon="solar:check-circle-bold"),
                action="show",
                autoClose=3000
            )

            # Load clients and return
            clients = load_test_clients()

            return False, clients, success_notification  # Close modal, refresh list, show notification

        else:
            print("❌ Test client insert failed - no result")
            return no_update, no_update, dmc.Notification(
                title="Error",
                message="Failed to create test client",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                action="show"
            )

    except Exception as e:
        print(f"❌ Exception in submit_test_client: {e}")
        import traceback
        traceback.print_exc()

        return no_update, no_update, dmc.Notification(
            title="Error",
            message=f"Exception: {str(e)}",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )


@callback(
    Output("test-client-list-container", "children", allow_duplicate=True),
    Input("test-client-modal", "opened"),
    prevent_initial_call=True
)
def load_test_clients_on_modal_close(is_opened):
    """Reload clients when modal closes"""
    if not is_opened:  # Modal just closed
        return load_test_clients()
    return no_update


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_test_clients():
    """Load and display test clients"""
    try:
        db = Database()
        clients = db.get_all_po_clients()

        print(f"📊 Loaded {len(clients)} test clients")

        if not clients:
            return dmc.Alert(
                "No test clients yet. Click 'Add Test Client' to create one.",
                title="Empty List",
                color="blue",
                icon=DashIconify(icon="solar:info-circle-bold")
            )

        # Create simple cards
        client_cards = []
        for client in clients:
            card = dmc.Card([
                dmc.Group([
                    dmc.Stack([
                        dmc.Text(
                            f"{client.get('first_name', '')} {client.get('last_name', '')}",
                            size="lg",
                            fw=600
                        ),
                        dmc.Group([
                            dmc.Badge(client.get('client_type', 'unknown'), color="blue"),
                            dmc.Text(
                                f"Created by: {client.get('created_by', 'NULL')}",
                                size="sm",
                                c="dimmed"
                            ),
                        ], gap="xs")
                    ], gap=4),
                ]),
            ], withBorder=True, radius="md", p="md", mb="sm")

            client_cards.append(card)

        return dmc.Stack(client_cards, gap="sm")

    except Exception as e:
        print(f"❌ Error loading test clients: {e}")
        return dmc.Alert(
            f"Error loading clients: {str(e)}",
            title="Error",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )
