"""
Bulk Actions Page
CSV export and bulk operations
"""
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash_iconify import DashIconify
from modules.database import Database
import csv
import io
import base64
from datetime import datetime

db = Database()

layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Bulk Actions", order=1),
        dmc.Badge("Export & Operations", color="gray", variant="light")
    ], justify="space-between"),

    dmc.Text("Perform bulk operations and export contractor data", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # CSV Export Section
    dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:download-minimalistic-bold", width=28, color="blue"),
                dmc.Text("CSV Export", size="lg", fw=600)
            ], gap="sm"),

            dmc.Text("Export contractor data to CSV format", size="sm", c="dimmed"),

            dmc.Space(h=5),

            # Export options
            dmc.Stack([
                dmc.Text("Select export scope:", fw=500, size="sm"),
                dmc.RadioGroup(
                    id="export-scope-radio",
                    children=[
                        dmc.Radio(label="All contractors", value="all", description="Export everything"),
                        dmc.Radio(label="Enriched only", value="enriched", description="Only contractors with AI analysis"),
                        dmc.Radio(label="High priority (8+)", value="high_priority", description="Hot leads only"),
                        dmc.Radio(label="Custom score range", value="custom_score", description="Specify min/max score"),
                    ],
                    value="all",
                    size="sm"
                )
            ], gap="xs"),

            # Custom score range (hidden by default)
            html.Div(id="custom-score-range", style={"display": "none"}),

            dmc.Space(h=5),

            # Include outreach option
            dmc.Checkbox(
                id="include-outreach-checkbox",
                label="Include outreach materials in export (separate columns)",
                checked=False,
                size="sm"
            ),

            dmc.Space(h=5),

            # Export info
            html.Div(id="export-info-container"),

            dmc.Space(h=5),

            # Export button
            dmc.Button(
                "Export to CSV",
                id="export-csv-btn",
                leftSection=DashIconify(icon="solar:download-minimalistic-bold"),
                color="blue",
                size="lg",
                fullWidth=True
            ),

            # Download component
            dcc.Download(id="download-csv")
        ], gap="md")
    ], p="lg", withBorder=True, radius="md"),

    dmc.Space(h=10),

    # Database Statistics
    dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:chart-bold", width=28, color="purple"),
                dmc.Text("Database Statistics", size="lg", fw=600)
            ], gap="sm"),

            html.Div(id="database-stats-container")
        ], gap="md")
    ], p="lg", withBorder=True, radius="md"),

], gap="md")


# Callback to show/hide custom score range
@callback(
    Output("custom-score-range", "style"),
    Output("custom-score-range", "children"),
    Input("export-scope-radio", "value"),
)
def toggle_custom_score_range(scope):
    """Show custom score range inputs when custom_score is selected"""
    if scope == "custom_score":
        return {"display": "block"}, dmc.Group([
            dmc.NumberInput(
                id="min-score-input",
                label="Min Score",
                value=1,
                min=1,
                max=10,
                step=1,
                size="sm",
                style={"width": "150px"}
            ),
            dmc.NumberInput(
                id="max-score-input",
                label="Max Score",
                value=10,
                min=1,
                max=10,
                step=1,
                size="sm",
                style={"width": "150px"}
            )
        ], gap="md")
    return {"display": "none"}, None


# Callback to update export info
@callback(
    Output("export-info-container", "children"),
    Output("database-stats-container", "children"),
    Input("export-scope-radio", "value"),
    Input("include-outreach-checkbox", "checked"),
    State("custom-score-range", "children"),
)
def update_export_info(scope, include_outreach, _):
    """Display info about what will be exported and database stats"""

    # Get contractors
    try:
        all_contractors = db.client.table("contractors").select("*").execute()
        contractors = all_contractors.data if all_contractors.data else []
    except:
        contractors = []

    # Filter based on scope
    if scope == "all":
        filtered = contractors
        scope_text = "all contractors"
    elif scope == "enriched":
        filtered = [c for c in contractors if c.get('enrichment_status') == 'completed']
        scope_text = "enriched contractors"
    elif scope == "high_priority":
        filtered = [c for c in contractors if c.get('enrichment_status') == 'completed' and c.get('lead_score', 0) >= 8]
        scope_text = "high priority contractors (score 8+)"
    elif scope == "custom_score":
        # Will be filtered in export callback
        filtered = [c for c in contractors if c.get('enrichment_status') == 'completed']
        scope_text = "contractors in custom score range"
    else:
        filtered = contractors
        scope_text = "contractors"

    # Count with outreach
    try:
        outreach_data = db.client.table("outreach_materials").select("contractor_id").execute()
        contractor_ids_with_outreach = set([o['contractor_id'] for o in outreach_data.data]) if outreach_data.data else set()
    except:
        contractor_ids_with_outreach = set()

    # Export info
    export_info = dmc.Alert(
        dmc.Stack([
            dmc.Text(f"Will export {len(filtered)} {scope_text}", fw=500, size="sm"),
            dmc.Text(f"Outreach materials: {'Included' if include_outreach else 'Not included'}", size="xs", c="dimmed")
        ], gap=4),
        color="blue",
        variant="light",
        icon=DashIconify(icon="solar:info-circle-bold")
    )

    # Database statistics
    enriched = [c for c in contractors if c.get('enrichment_status') == 'completed']
    pending = [c for c in contractors if c.get('enrichment_status') == 'pending' or not c.get('enrichment_status')]
    failed = [c for c in contractors if c.get('enrichment_status') == 'failed']

    high_priority = [c for c in enriched if c.get('lead_score', 0) >= 8]
    medium_priority = [c for c in enriched if 5 <= c.get('lead_score', 0) < 8]

    stats = dmc.SimpleGrid([
        dmc.Stack([
            dmc.Text("Total", size="xs", c="dimmed"),
            dmc.Text(str(len(contractors)), size="xl", fw=700)
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("Enriched", size="xs", c="dimmed"),
            dmc.Text(str(len(enriched)), size="xl", fw=700, c="green")
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("Pending", size="xs", c="dimmed"),
            dmc.Text(str(len(pending)), size="xl", fw=700, c="orange")
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("Failed", size="xs", c="dimmed"),
            dmc.Text(str(len(failed)), size="xl", fw=700, c="red")
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("Hot Leads", size="xs", c="dimmed"),
            dmc.Text(str(len(high_priority)), size="xl", fw=700, c="orange")
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("Warm Leads", size="xs", c="dimmed"),
            dmc.Text(str(len(medium_priority)), size="xl", fw=700, c="yellow")
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("With Outreach", size="xs", c="dimmed"),
            dmc.Text(str(len(contractor_ids_with_outreach)), size="xl", fw=700, c="blue")
        ], gap=0, align="center"),

        dmc.Stack([
            dmc.Text("Avg Score", size="xs", c="dimmed"),
            dmc.Text(
                f"{sum(c.get('lead_score', 0) for c in enriched) / len(enriched):.1f}" if enriched else "N/A",
                size="xl",
                fw=700,
                c="purple"
            )
        ], gap=0, align="center"),
    ], cols=4, spacing="md")

    return export_info, stats


# Callback to handle CSV export
@callback(
    Output("download-csv", "data"),
    Input("export-csv-btn", "n_clicks"),
    State("export-scope-radio", "value"),
    State("include-outreach-checkbox", "checked"),
    State("min-score-input", "value"),
    State("max-score-input", "value"),
    prevent_initial_call=True
)
def export_to_csv(n_clicks, scope, include_outreach, min_score, max_score):
    """Export contractors to CSV"""
    if not n_clicks:
        return dash.no_update

    # Get contractors
    try:
        all_contractors = db.client.table("contractors").select("*").execute()
        contractors = all_contractors.data if all_contractors.data else []
    except:
        return dash.no_update

    # Filter based on scope
    if scope == "all":
        filtered = contractors
    elif scope == "enriched":
        filtered = [c for c in contractors if c.get('enrichment_status') == 'completed']
    elif scope == "high_priority":
        filtered = [c for c in contractors if c.get('enrichment_status') == 'completed' and c.get('lead_score', 0) >= 8]
    elif scope == "custom_score":
        min_val = min_score if min_score else 1
        max_val = max_score if max_score else 10
        filtered = [c for c in contractors if c.get('enrichment_status') == 'completed'
                   and min_val <= c.get('lead_score', 0) <= max_val]
    else:
        filtered = contractors

    if not filtered:
        return dash.no_update

    # Get outreach materials if requested
    outreach_by_contractor = {}
    if include_outreach:
        try:
            outreach_data = db.client.table("outreach_materials").select("*").execute()
            if outreach_data.data:
                for material in outreach_data.data:
                    contractor_id = material['contractor_id']
                    if contractor_id not in outreach_by_contractor:
                        outreach_by_contractor[contractor_id] = {'emails': [], 'scripts': []}

                    if material['material_type'].startswith('email'):
                        outreach_by_contractor[contractor_id]['emails'].append({
                            'subject': material.get('subject_line', ''),
                            'body': material.get('content', '')
                        })
                    elif material['material_type'].startswith('script'):
                        outreach_by_contractor[contractor_id]['scripts'].append(material.get('content', ''))
        except:
            pass

    # Create CSV
    output = io.StringIO()

    # Define columns
    columns = [
        'company_name', 'phone', 'email', 'website', 'address', 'city', 'state',
        'google_rating', 'review_count', 'lead_score', 'enrichment_status',
        'specializations', 'glazing_opportunities', 'use_subcontractors',
        'profile_notes', 'outreach_angle', 'source', 'date_added'
    ]

    if include_outreach:
        columns.extend(['email_subject_1', 'email_body_1', 'email_subject_2', 'email_body_2',
                       'email_subject_3', 'email_body_3', 'script_1', 'script_2'])

    writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()

    for contractor in filtered:
        row = {col: contractor.get(col, '') for col in columns if col not in ['email_subject_1', 'email_body_1', 'email_subject_2', 'email_body_2', 'email_subject_3', 'email_body_3', 'script_1', 'script_2']}

        # Add outreach materials if requested
        if include_outreach and contractor['id'] in outreach_by_contractor:
            materials = outreach_by_contractor[contractor['id']]
            for i, email in enumerate(materials['emails'][:3], 1):
                row[f'email_subject_{i}'] = email['subject']
                row[f'email_body_{i}'] = email['body']
            for i, script in enumerate(materials['scripts'][:2], 1):
                row[f'script_{i}'] = script

        writer.writerow(row)

    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"contractors_{scope}_{timestamp}.csv"

    return dict(content=output.getvalue(), filename=filename)
