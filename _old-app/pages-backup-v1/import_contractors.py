"""
Import Contractors Page
Manual entry and CSV upload functionality
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

# CSV template columns
CSV_TEMPLATE_COLUMNS = [
    "company_name", "phone", "email", "website", "address",
    "city", "state", "zip_code", "google_rating", "review_count"
]

layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Import Contractors", order=1),
        dmc.Badge("Add Data", color="teal", variant="light", leftSection=DashIconify(icon="solar:upload-minimalistic-bold"))
    ], justify="space-between"),

    dmc.Text("Add contractors manually or import from CSV", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Method selection
    dmc.SegmentedControl(
        id="import-method-selector",
        value="manual",
        data=[
            {"value": "manual", "label": "Manual Entry"},
            {"value": "csv", "label": "CSV Upload"},
        ],
        fullWidth=True,
        size="md"
    ),

    dmc.Space(h=10),

    # Manual entry container
    html.Div(id="import-manual-container"),

    # CSV upload container
    html.Div(id="import-csv-container", style={"display": "none"}),

    # Results container
    html.Div(id="import-results-container"),

], gap="md")


# Callback to toggle between manual and CSV
@callback(
    Output("import-manual-container", "style"),
    Output("import-csv-container", "style"),
    Input("import-method-selector", "value"),
)
def toggle_import_method(method):
    """Toggle between manual entry and CSV upload"""
    if method == "manual":
        return {"display": "block"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "block"}


# Callback to populate manual entry form
@callback(
    Output("import-manual-container", "children"),
    Input("import-method-selector", "value"),
)
def render_manual_form(_):
    """Render manual entry form"""
    return dmc.Paper([
        dmc.Stack([
            dmc.Text("Enter Contractor Details", size="lg", fw=600),
            dmc.Text("All fields except website and email are recommended", size="sm", c="dimmed"),

            dmc.Space(h=10),

            # Company info
            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="manual-company-name",
                        label="Company Name",
                        placeholder="ABC Construction",
                        required=True,
                        leftSection=DashIconify(icon="solar:buildings-bold")
                    )
                ], span=6),

                dmc.GridCol([
                    dmc.TextInput(
                        id="manual-phone",
                        label="Phone Number",
                        placeholder="(904) 555-0123",
                        required=True,
                        leftSection=DashIconify(icon="solar:phone-bold")
                    )
                ], span=6),
            ]),

            # Contact info
            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="manual-email",
                        label="Email",
                        placeholder="contact@company.com",
                        leftSection=DashIconify(icon="solar:letter-bold")
                    )
                ], span=6),

                dmc.GridCol([
                    dmc.TextInput(
                        id="manual-website",
                        label="Website",
                        placeholder="https://company.com",
                        leftSection=DashIconify(icon="solar:global-bold")
                    )
                ], span=6),
            ]),

            # Address
            dmc.TextInput(
                id="manual-address",
                label="Street Address",
                placeholder="123 Main St",
                leftSection=DashIconify(icon="solar:map-point-bold")
            ),

            # City, State, Zip
            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="manual-city",
                        label="City",
                        placeholder="Jacksonville",
                        required=True,
                        leftSection=DashIconify(icon="solar:city-bold")
                    )
                ], span=6),

                dmc.GridCol([
                    dmc.Select(
                        id="manual-state",
                        label="State",
                        placeholder="Select state",
                        data=["FL", "GA", "AL", "SC", "NC", "TN"],
                        value="FL",
                        searchable=True,
                        leftSection=DashIconify(icon="solar:map-bold")
                    )
                ], span=3),

                dmc.GridCol([
                    dmc.TextInput(
                        id="manual-zip",
                        label="ZIP Code",
                        placeholder="32256",
                        leftSection=DashIconify(icon="solar:mailbox-bold")
                    )
                ], span=3),
            ]),

            # Rating info (optional)
            dmc.Grid([
                dmc.GridCol([
                    dmc.NumberInput(
                        id="manual-rating",
                        label="Google Rating (Optional)",
                        placeholder="4.5",
                        min=0,
                        max=5,
                        step=0.1,
                        leftSection=DashIconify(icon="solar:star-bold")
                    )
                ], span=6),

                dmc.GridCol([
                    dmc.NumberInput(
                        id="manual-reviews",
                        label="Review Count (Optional)",
                        placeholder="42",
                        min=0,
                        leftSection=DashIconify(icon="solar:chat-round-bold")
                    )
                ], span=6),
            ]),

            dmc.Space(h=10),

            # Auto-enrich option
            dmc.Checkbox(
                id="manual-auto-enrich",
                label="Automatically enrich this contractor after saving (~$0.03)",
                checked=False,
                size="sm"
            ),

            dmc.Space(h=5),

            # Submit button
            dmc.Button(
                "Add Contractor",
                id="manual-submit-btn",
                fullWidth=True,
                size="lg",
                leftSection=DashIconify(icon="solar:add-circle-bold"),
                color="teal"
            )
        ], gap="md")
    ], p="md", withBorder=True)


# Callback to populate CSV upload form
@callback(
    Output("import-csv-container", "children"),
    Input("import-method-selector", "value"),
)
def render_csv_form(_):
    """Render CSV upload form"""
    return dmc.Stack([
        # Download template section
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:download-minimalistic-bold", width=24, color="blue"),
                    dmc.Text("Step 1: Download CSV Template", size="lg", fw=600)
                ], gap="sm"),

                dmc.Text("Start with our template to ensure your CSV has the correct format", size="sm", c="dimmed"),

                dmc.Button(
                    "Download CSV Template",
                    id="download-template-btn",
                    leftSection=DashIconify(icon="solar:download-minimalistic-bold"),
                    variant="light",
                    color="blue"
                ),

                dcc.Download(id="download-template")
            ], gap="sm")
        ], p="md", withBorder=True),

        # Upload section
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:upload-minimalistic-bold", width=24, color="teal"),
                    dmc.Text("Step 2: Upload Your CSV", size="lg", fw=600)
                ], gap="sm"),

                dmc.Text("Upload a CSV file with your contractor data", size="sm", c="dimmed"),

                dcc.Upload(
                    id="upload-csv",
                    children=dmc.Paper([
                        dmc.Stack([
                            DashIconify(icon="solar:cloud-upload-bold", width=48, color="gray"),
                            dmc.Text("Drag and Drop or Click to Select CSV File", fw=500),
                            dmc.Text("Maximum file size: 5MB", size="sm", c="dimmed")
                        ], align="center", gap="xs")
                    ], p="xl", withBorder=True, style={
                        "borderStyle": "dashed",
                        "textAlign": "center",
                        "cursor": "pointer"
                    }),
                    multiple=False,
                    accept=".csv"
                ),

                # Preview and import container
                html.Div(id="csv-preview-container")
            ], gap="md")
        ], p="md", withBorder=True),

        # Instructions
        dmc.Accordion([
            dmc.AccordionItem([
                dmc.AccordionControl(
                    "CSV Format Instructions",
                    icon=DashIconify(icon="solar:info-circle-bold", width=20)
                ),
                dmc.AccordionPanel([
                    dmc.Stack([
                        dmc.Text("Required Columns:", fw=600, size="sm"),
                        dmc.List([
                            dmc.ListItem("company_name - Name of the contractor"),
                            dmc.ListItem("phone - Phone number (used for duplicate detection)"),
                            dmc.ListItem("city - City location"),
                            dmc.ListItem("state - State (e.g., FL, GA)")
                        ], size="sm"),

                        dmc.Space(h=5),

                        dmc.Text("Optional Columns:", fw=600, size="sm"),
                        dmc.List([
                            dmc.ListItem("email - Contact email"),
                            dmc.ListItem("website - Company website URL"),
                            dmc.ListItem("address - Street address"),
                            dmc.ListItem("zip_code - ZIP code"),
                            dmc.ListItem("google_rating - Rating from 0-5"),
                            dmc.ListItem("review_count - Number of reviews")
                        ], size="sm"),

                        dmc.Space(h=5),

                        dmc.Alert(
                            "Duplicate Detection: Contractors with matching phone numbers will be skipped automatically",
                            color="blue",
                            variant="light",
                            icon=DashIconify(icon="solar:shield-check-bold")
                        )
                    ], gap="xs")
                ])
            ], value="instructions")
        ], value=None)
    ], gap="md")


# Callback to download CSV template
@callback(
    Output("download-template", "data"),
    Input("download-template-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_template(n_clicks):
    """Generate and download CSV template"""
    if not n_clicks:
        return dash.no_update

    # Create CSV template
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(CSV_TEMPLATE_COLUMNS)

    # Write example row
    writer.writerow([
        "ABC Construction",  # company_name
        "(904) 555-0123",    # phone
        "contact@abc.com",   # email
        "https://abc.com",   # website
        "123 Main St",       # address
        "Jacksonville",      # city
        "FL",                # state
        "32256",            # zip_code
        "4.5",              # google_rating
        "42"                # review_count
    ])

    return dict(
        content=output.getvalue(),
        filename=f"contractor_import_template_{datetime.now().strftime('%Y%m%d')}.csv"
    )


# Callback to handle manual entry submission
@callback(
    Output("import-results-container", "children"),
    Input("manual-submit-btn", "n_clicks"),
    State("manual-company-name", "value"),
    State("manual-phone", "value"),
    State("manual-email", "value"),
    State("manual-website", "value"),
    State("manual-address", "value"),
    State("manual-city", "value"),
    State("manual-state", "value"),
    State("manual-zip", "value"),
    State("manual-rating", "value"),
    State("manual-reviews", "value"),
    State("manual-auto-enrich", "checked"),
    prevent_initial_call=True
)
def submit_manual_entry(n_clicks, company_name, phone, email, website, address,
                       city, state, zip_code, rating, reviews, auto_enrich):
    """Handle manual contractor entry"""
    if not n_clicks:
        return dash.no_update

    # Validate required fields
    if not company_name or not phone or not city or not state:
        return dmc.Alert(
            "Please fill in all required fields: Company Name, Phone, City, and State",
            title="Validation Error",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        )

    # Check for duplicate by phone
    try:
        existing = db.client.table("contractors").select("company_name").eq("phone", phone).execute()
        if existing.data:
            return dmc.Alert(
                f"A contractor with phone number {phone} already exists: {existing.data[0]['company_name']}",
                title="Duplicate Found",
                color="yellow",
                icon=DashIconify(icon="solar:danger-triangle-bold")
            )
    except Exception as e:
        pass  # Continue if check fails

    # Prepare contractor data
    contractor_data = {
        "company_name": company_name,
        "phone": phone,
        "email": email or None,
        "website": website or None,
        "address": address or None,
        "city": city,
        "state": state,
        "zip_code": zip_code or None,
        "google_rating": rating if rating is not None else None,
        "review_count": int(reviews) if reviews is not None else None,
        "source": "manual_entry",
        "enrichment_status": "pending",
        "created_at": datetime.now().isoformat()
    }

    # Save to database
    try:
        result = db.client.table("contractors").insert(contractor_data).execute()

        if result.data:
            contractor_id = result.data[0]['id']

            # Auto-enrich if requested
            enrich_message = ""
            if auto_enrich and website:
                try:
                    from modules.enrichment import ContractorEnrichment
                    import asyncio
                    enricher = ContractorEnrichment()
                    enrich_result = asyncio.run(enricher.enrich_contractor(contractor_id))
                    if enrich_result and enrich_result.get('success'):
                        enrich_message = f" • Enriched with lead score: {enrich_result.get('lead_score', 'N/A')}/10"
                    else:
                        enrich_message = " • Enrichment failed (see Enrichment page for details)"
                except Exception as e:
                    enrich_message = f" • Enrichment error: {str(e)}"
            elif auto_enrich and not website:
                enrich_message = " • Skipped enrichment (no website provided)"

            return dmc.Stack([
                dmc.Alert(
                    f"Successfully added: {company_name}{enrich_message}",
                    title="Contractor Added",
                    color="green",
                    icon=DashIconify(icon="solar:check-circle-bold")
                ),
                dmc.Button(
                    "Add Another Contractor",
                    id="add-another-btn",
                    variant="light",
                    leftSection=DashIconify(icon="solar:add-circle-bold"),
                    mt="sm"
                ),
                dmc.Button(
                    "View in Contractors Page",
                    href="/contractors",
                    variant="light",
                    color="blue",
                    leftSection=DashIconify(icon="solar:eye-bold"),
                    mt="sm"
                )
            ], gap="sm")
        else:
            return dmc.Alert(
                "Failed to add contractor. Please try again.",
                title="Error",
                color="red",
                icon=DashIconify(icon="solar:danger-bold")
            )

    except Exception as e:
        return dmc.Alert(
            f"Database error: {str(e)}",
            title="Error",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        )


# Callback to handle CSV upload and preview
@callback(
    Output("csv-preview-container", "children"),
    Input("upload-csv", "contents"),
    State("upload-csv", "filename"),
    prevent_initial_call=True
)
def process_csv_upload(contents, filename):
    """Process uploaded CSV and show preview"""
    if not contents:
        return None

    try:
        # Decode the file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')

        # Parse CSV
        csv_data = list(csv.DictReader(io.StringIO(decoded)))

        if not csv_data:
            return dmc.Alert(
                "CSV file is empty",
                title="Empty File",
                color="red",
                icon=DashIconify(icon="solar:danger-bold")
            )

        # Validate required columns
        required_cols = ["company_name", "phone", "city", "state"]
        first_row_keys = list(csv_data[0].keys())
        missing_cols = [col for col in required_cols if col not in first_row_keys]

        if missing_cols:
            return dmc.Alert(
                f"Missing required columns: {', '.join(missing_cols)}",
                title="Invalid CSV Format",
                color="red",
                icon=DashIconify(icon="solar:danger-bold")
            )

        # Check for duplicates in database
        phones = [row.get('phone', '') for row in csv_data if row.get('phone')]
        existing_phones = set()
        try:
            for phone in phones:
                result = db.client.table("contractors").select("phone").eq("phone", phone).execute()
                if result.data:
                    existing_phones.add(phone)
        except:
            pass

        new_count = len([row for row in csv_data if row.get('phone') not in existing_phones])
        duplicate_count = len([row for row in csv_data if row.get('phone') in existing_phones])

        # Store the CSV data
        return dmc.Stack([
            dmc.Alert(
                f"File uploaded: {filename}",
                title="CSV Loaded",
                color="green",
                icon=DashIconify(icon="solar:check-circle-bold")
            ),

            dmc.Paper([
                dmc.SimpleGrid([
                    dmc.Stack([
                        dmc.Text("Total Rows", size="xs", c="dimmed"),
                        dmc.Text(str(len(csv_data)), size="xl", fw=700),
                    ], gap=0, align="center"),

                    dmc.Stack([
                        dmc.Text("New Contractors", size="xs", c="dimmed"),
                        dmc.Text(str(new_count), size="xl", fw=700, c="green"),
                    ], gap=0, align="center"),

                    dmc.Stack([
                        dmc.Text("Duplicates", size="xs", c="dimmed"),
                        dmc.Text(str(duplicate_count), size="xl", fw=700, c="gray"),
                    ], gap=0, align="center"),
                ], cols=3)
            ], p="md", withBorder=True),

            # Preview table (first 5 rows)
            dmc.Stack([
                dmc.Text("Preview (first 5 rows)", fw=600, size="sm"),
                dmc.Table([
                    html.Thead(html.Tr([
                        html.Th("Company"),
                        html.Th("Phone"),
                        html.Th("City"),
                        html.Th("State"),
                        html.Th("Status")
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(row.get('company_name', 'N/A')),
                            html.Td(row.get('phone', 'N/A')),
                            html.Td(row.get('city', 'N/A')),
                            html.Td(row.get('state', 'N/A')),
                            html.Td(
                                dmc.Badge(
                                    "Duplicate",
                                    color="gray",
                                    size="sm"
                                ) if row.get('phone') in existing_phones else dmc.Badge(
                                    "New",
                                    color="green",
                                    size="sm"
                                )
                            )
                        ]) for row in csv_data[:5]
                    ])
                ], striped=True, highlightOnHover=True, withTableBorder=True)
            ], gap="xs"),

            # Import button
            dmc.Button(
                f"Import {new_count} New Contractor(s)",
                id="csv-import-btn",
                fullWidth=True,
                size="lg",
                leftSection=DashIconify(icon="solar:upload-minimalistic-bold"),
                color="teal",
                disabled=new_count == 0
            ),

            # Hidden store for CSV data
            dcc.Store(id="csv-data-store", data=csv_data)

        ], gap="md")

    except Exception as e:
        return dmc.Alert(
            f"Error parsing CSV: {str(e)}",
            title="Parse Error",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        )


# Callback to import CSV data
@callback(
    Output("import-results-container", "children", allow_duplicate=True),
    Input("csv-import-btn", "n_clicks"),
    State("csv-data-store", "data"),
    prevent_initial_call=True
)
def import_csv_data(n_clicks, csv_data):
    """Import contractors from CSV"""
    if not n_clicks or not csv_data:
        return dash.no_update

    imported = 0
    skipped = 0
    errors = []

    for row in csv_data:
        # Check for duplicate
        phone = row.get('phone')
        if not phone:
            skipped += 1
            continue

        try:
            existing = db.client.table("contractors").select("id").eq("phone", phone).execute()
            if existing.data:
                skipped += 1
                continue
        except:
            pass

        # Prepare contractor data
        contractor_data = {
            "company_name": row.get('company_name'),
            "phone": phone,
            "email": row.get('email') or None,
            "website": row.get('website') or None,
            "address": row.get('address') or None,
            "city": row.get('city'),
            "state": row.get('state'),
            "zip_code": row.get('zip_code') or None,
            "google_rating": float(row.get('google_rating')) if row.get('google_rating') else None,
            "review_count": int(row.get('review_count')) if row.get('review_count') else None,
            "source": "csv_import",
            "enrichment_status": "pending",
            "created_at": datetime.now().isoformat()
        }

        # Import to database
        try:
            db.client.table("contractors").insert(contractor_data).execute()
            imported += 1
        except Exception as e:
            errors.append(f"{row.get('company_name')}: {str(e)}")

    # Build result message
    return dmc.Stack([
        dmc.Alert(
            f"Import complete! Added {imported} contractor(s). Skipped {skipped} duplicate(s).",
            title="Import Successful" if imported > 0 else "Import Complete",
            color="green" if imported > 0 else "yellow",
            icon=DashIconify(icon="solar:check-circle-bold")
        ),

        dmc.Paper([
            dmc.SimpleGrid([
                dmc.Stack([
                    dmc.Text("Imported", size="xs", c="dimmed"),
                    dmc.Text(str(imported), size="xl", fw=700, c="green"),
                ], gap=0, align="center"),

                dmc.Stack([
                    dmc.Text("Skipped", size="xs", c="dimmed"),
                    dmc.Text(str(skipped), size="xl", fw=700, c="gray"),
                ], gap=0, align="center"),

                dmc.Stack([
                    dmc.Text("Errors", size="xs", c="dimmed"),
                    dmc.Text(str(len(errors)), size="xl", fw=700, c="red"),
                ], gap=0, align="center"),
            ], cols=3)
        ], p="md", withBorder=True),

        dmc.Group([
            dmc.Button(
                "Import More",
                id="import-more-btn",
                variant="light",
                leftSection=DashIconify(icon="solar:upload-minimalistic-bold")
            ),
            dmc.Button(
                "View Contractors",
                href="/contractors",
                variant="light",
                color="blue",
                leftSection=DashIconify(icon="solar:eye-bold")
            ),
            dmc.Button(
                "Enrich New Contractors",
                href="/enrichment",
                variant="light",
                color="purple",
                leftSection=DashIconify(icon="solar:magic-stick-bold")
            ) if imported > 0 else None
        ], gap="sm"),

        dmc.Accordion([
            dmc.AccordionItem([
                dmc.AccordionControl(f"View Errors ({len(errors)})"),
                dmc.AccordionPanel(
                    dmc.Stack([
                        dmc.Text(error, size="sm") for error in errors
                    ], gap="xs")
                )
            ], value="errors")
        ], value=None) if errors else None

    ], gap="md")
