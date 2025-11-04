"""
Contractor Card Component
Reusable card component for displaying contractor preview in grid
"""
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def create_contractor_card(contractor):
    """
    Create a single contractor card with preview information

    Args:
        contractor: Dict with contractor data from database

    Returns:
        dmc.Card component
    """
    contractor_id = contractor.get('id')
    company_name = contractor.get('company_name', 'Unknown')
    city = contractor.get('city', 'Unknown')
    state = contractor.get('state', 'FL')
    lead_score = contractor.get('lead_score')
    phone = contractor.get('phone', 'N/A')
    website = contractor.get('website', 'N/A')
    specializations = contractor.get('specializations', 'N/A')
    enrichment_status = contractor.get('enrichment_status', 'pending')

    # Score badge color
    if lead_score:
        if lead_score >= 8:
            score_color = "green"
            score_icon = "🔥"
        elif lead_score >= 6:
            score_color = "blue"
            score_icon = "⭐"
        else:
            score_color = "orange"
            score_icon = "✓"
    else:
        score_color = "gray"
        score_icon = "—"

    # Enrichment status badge
    status_colors = {
        'completed': 'green',
        'pending': 'yellow',
        'failed': 'red'
    }

    return dmc.Card(
        children=[
            # Header with company name and score
            dmc.Group([
                dmc.Text(company_name, fw=700, size="lg", style={"flex": 1}),
                dmc.Badge(
                    f"{score_icon} {lead_score}/10" if lead_score else "Not Scored",
                    color=score_color,
                    variant="filled",
                    size="lg"
                )
            ], justify="space-between", style={"marginBottom": "10px"}),

            # Location
            dmc.Group([
                DashIconify(icon="solar:map-point-bold", width=16, color="#868e96"),
                dmc.Text(f"{city}, {state}", size="sm", c="dimmed")
            ], gap=5, style={"marginBottom": "8px"}),

            # Specializations
            dmc.Text(
                specializations[:80] + "..." if len(str(specializations)) > 80 else specializations,
                size="sm",
                c="dimmed",
                style={"marginBottom": "12px", "minHeight": "40px"}
            ),

            dmc.Divider(style={"margin": "12px 0"}),

            # Contact info
            dmc.Group([
                DashIconify(icon="solar:phone-bold", width=16, color="#868e96"),
                dmc.Text(phone if phone and phone != 'N/A' else "No phone", size="sm")
            ], gap=5, style={"marginBottom": "5px"}),

            dmc.Group([
                DashIconify(icon="solar:global-bold", width=16, color="#868e96"),
                dmc.Text(
                    (website[:35] + "...") if website and len(website) > 35 else (website if website != 'N/A' else "No website"),
                    size="sm",
                    truncate=True
                )
            ], gap=5, style={"marginBottom": "12px"}),

            # Status badge
            dmc.Badge(
                enrichment_status.title(),
                color=status_colors.get(enrichment_status, 'gray'),
                variant="light",
                size="sm",
                style={"marginBottom": "15px"}
            ),

            # Action button
            dmc.Button(
                "View Details",
                id={'type': 'view-detail-btn', 'index': contractor_id},
                variant="light",
                fullWidth=True,
                leftSection=DashIconify(icon="solar:eye-bold", width=18)
            )
        ],
        shadow="sm",
        padding="lg",
        radius="md",
        withBorder=True,
        style={
            "height": "100%",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
        },
        id={'type': 'contractor-card', 'index': contractor_id}
    )
