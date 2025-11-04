"""
Outreach Materials Display Component
Helper functions for displaying email templates and call scripts
"""
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def create_outreach_tab(contractor_id, outreach_materials=None):
    """
    Create the outreach tab content showing emails and scripts

    Args:
        contractor_id: ID of the contractor
        outreach_materials: Dict with 'emails' and 'scripts' lists

    Returns:
        dmc.Stack with outreach content
    """
    if not outreach_materials or (not outreach_materials.get('emails') and not outreach_materials.get('scripts')):
        # No materials generated yet
        return dmc.Stack([
            dmc.Alert(
                "No outreach materials have been generated yet for this contractor.",
                title="Generate Outreach",
                color="blue",
                icon=DashIconify(icon="solar:magic-stick-bold")
            ),
            dmc.Space(h=10),
            dmc.Text("Click the 'Generate Outreach' button below to create personalized email templates and call scripts using Claude AI.", size="sm", c="dimmed")
        ], gap="md")

    # Display existing materials
    emails = outreach_materials.get('emails', [])
    scripts = outreach_materials.get('scripts', [])

    return dmc.Stack([
        # Email Templates Section
        dmc.Text("Email Templates", fw=600, size="lg"),
        dmc.Space(h=5),

        dmc.Accordion(
            children=[
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="solar:letter-bold", width=20),
                            dmc.Text(email.get('subject_line', 'Email Template'), fw=500)
                        ], gap=10)
                    ),
                    dmc.AccordionPanel(
                        dmc.Stack([
                            dmc.Group([
                                dmc.Text("Subject:", fw=600, size="sm"),
                                dmc.Group([
                                    dmc.ActionIcon(
                                        DashIconify(icon="solar:copy-bold", width=16),
                                        variant="subtle",
                                        size="sm",
                                        id={'type': 'copy-subject-btn', 'index': f"{contractor_id}-email-{i+1}"}
                                    ),
                                    dmc.ActionIcon(
                                        DashIconify(icon="solar:trash-bin-trash-bold", width=16),
                                        variant="subtle",
                                        color="red",
                                        size="sm",
                                        id={'type': 'delete-outreach-btn', 'index': email.get('id', f"email-{i+1}")}
                                    ) if email.get('id') else None
                                ], gap=5)
                            ], justify="space-between"),
                            dmc.Text(email.get('subject_line', 'N/A'), size="sm", style={"fontStyle": "italic"}),

                            dmc.Space(h=10),

                            dmc.Group([
                                dmc.Text("Body:", fw=600, size="sm"),
                                dmc.ActionIcon(
                                    DashIconify(icon="solar:copy-bold", width=16),
                                    variant="subtle",
                                    size="sm",
                                    id={'type': 'copy-email-body-btn', 'index': f"{contractor_id}-email-{i+1}"}
                                )
                            ], justify="space-between"),
                            dmc.Textarea(
                                value=email.get('content', 'N/A'),
                                autosize=True,
                                minRows=6,
                                readOnly=True,
                                id={'type': 'email-body-text', 'index': f"{contractor_id}-email-{i+1}"}
                            )
                        ], gap=5)
                    )
                ], value=f"email-{i+1}")
                for i, email in enumerate(emails)
            ]
        ) if emails else dmc.Text("No email templates", c="dimmed", size="sm"),

        dmc.Space(h=20),
        dmc.Divider(),
        dmc.Space(h=20),

        # Call Scripts Section
        dmc.Text("Call Scripts", fw=600, size="lg"),
        dmc.Space(h=5),

        dmc.Accordion(
            children=[
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="solar:phone-bold", width=20),
                            dmc.Text(f"Script {i+1}", fw=500)
                        ], gap=10)
                    ),
                    dmc.AccordionPanel(
                        dmc.Stack([
                            dmc.Group([
                                dmc.Text("Script:", fw=600, size="sm"),
                                dmc.Group([
                                    dmc.ActionIcon(
                                        DashIconify(icon="solar:copy-bold", width=16),
                                        variant="subtle",
                                        size="sm",
                                        id={'type': 'copy-script-btn', 'index': f"{contractor_id}-script-{i+1}"}
                                    ),
                                    dmc.ActionIcon(
                                        DashIconify(icon="solar:trash-bin-trash-bold", width=16),
                                        variant="subtle",
                                        color="red",
                                        size="sm",
                                        id={'type': 'delete-outreach-btn', 'index': script.get('id', f"script-{i+1}")}
                                    ) if script.get('id') else None
                                ], gap=5)
                            ], justify="space-between"),
                            dmc.Textarea(
                                value=script.get('content', 'N/A'),
                                autosize=True,
                                minRows=8,
                                readOnly=True,
                                id={'type': 'script-text', 'index': f"{contractor_id}-script-{i+1}"}
                            )
                        ], gap=5)
                    )
                ], value=f"script-{i+1}")
                for i, script in enumerate(scripts)
            ]
        ) if scripts else dmc.Text("No call scripts", c="dimmed", size="sm"),
    ], gap="md")


def create_activity_tab(contractor_id, interactions=None):
    """
    Create the activity/interaction tab content

    Args:
        contractor_id: ID of the contractor
        interactions: List of interaction records

    Returns:
        dmc.Stack with activity content
    """
    return dmc.Stack([
        # Interaction logging form
        dmc.Text("Log New Interaction", fw=600, size="lg"),
        dmc.Space(h=10),

        dmc.Select(
            label="Status",
            placeholder="Select status",
            data=[
                {"label": "Not Contacted", "value": "not_contacted"},
                {"label": "Attempted Contact", "value": "attempted_contact"},
                {"label": "Contacted", "value": "contacted"},
                {"label": "Meeting Scheduled", "value": "meeting_scheduled"},
                {"label": "Proposal Sent", "value": "proposal_sent"},
                {"label": "Negotiating", "value": "negotiating"},
                {"label": "Won", "value": "won"},
                {"label": "Lost", "value": "lost"},
            ],
            id={'type': 'interaction-status', 'index': contractor_id}
        ),

        dmc.TextInput(
            label="Your Name",
            placeholder="e.g., John Doe",
            id={'type': 'interaction-user', 'index': contractor_id}
        ),

        dmc.Textarea(
            label="Notes",
            placeholder="What happened in this interaction?",
            minRows=3,
            id={'type': 'interaction-notes', 'index': contractor_id}
        ),

        dmc.Button(
            "Log Interaction",
            leftSection=DashIconify(icon="solar:add-circle-bold", width=18),
            color="blue",
            id={'type': 'log-interaction-submit-btn', 'index': contractor_id}
        ),

        dmc.Space(h=20),
        dmc.Divider(),
        dmc.Space(h=20),

        # Interaction history
        dmc.Text("Interaction History", fw=600, size="lg"),
        dmc.Space(h=10),

        html.Div(id={'type': 'interaction-history', 'index': contractor_id}),

        # Display existing interactions
        dmc.Stack([
            dmc.Card([
                dmc.Group([
                    dmc.Badge(interaction.get('status', 'N/A').replace('_', ' ').title(), color="blue", variant="light"),
                    dmc.Text(interaction.get('date_logged', 'N/A'), size="sm", c="dimmed")
                ], justify="space-between"),
                dmc.Space(h=5),
                dmc.Text(interaction.get('notes', 'No notes'), size="sm"),
                dmc.Space(h=5),
                dmc.Text(f"By: {interaction.get('user_name', 'Unknown')}", size="xs", c="dimmed")
            ], withBorder=True, padding="md")
            for interaction in (interactions or [])
        ], gap="sm") if interactions else dmc.Text("No interactions logged yet", c="dimmed", size="sm", style={"fontStyle": "italic"})
    ], gap="md")
