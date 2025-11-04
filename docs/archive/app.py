"""
Island Glass Leads - Contractor Lead Generation & Outreach Tool
Main Streamlit Application
"""
import streamlit as st
from modules.database import Database
import os

# Page configuration
st.set_page_config(
    page_title="Island Glass Leads",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "styles", "crm_theme.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize database connection
@st.cache_resource
def init_database():
    """Initialize database connection (cached)"""
    try:
        return Database()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.info("Make sure you've created a .env file with SUPABASE_URL and SUPABASE_KEY")
        st.stop()

db = init_database()

# Sidebar navigation
st.sidebar.title("Island Glass Leads")
st.sidebar.caption("CRM System")
st.sidebar.markdown("---")

# Check if programmatic navigation is requested (from View button, etc.)
if 'navigate_to' in st.session_state:
    default_page = st.session_state.navigate_to
    del st.session_state['navigate_to']  # Clear after use
else:
    default_page = "Dashboard"

# Get page list
page_options = [
    "Dashboard",
    "Contractor Discovery",
    "Website Enrichment",
    "Contractor Directory",
    "Contractor Detail",
    "Bulk Actions",
    "Add/Import Contractors",
    "Settings"
]

# Calculate default index for programmatic navigation
default_index = page_options.index(default_page) if default_page in page_options else 0

page = st.sidebar.radio(
    "Navigation",
    page_options,
    index=default_index
)

st.sidebar.markdown("---")
st.sidebar.caption("Jacksonville Glazing Contractor Database")

# Main content area
if page == "Dashboard":
    st.title("Dashboard")

    # Get dashboard stats
    stats = db.get_dashboard_stats()

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Contractors", stats["total_contractors"])

    with col2:
        st.metric("High Priority Leads", stats["high_priority_leads"])

    with col3:
        st.metric("This Week", "0")  # Placeholder

    st.markdown("---")

    # Display test contractor
    st.subheader("Test Database Connection")

    contractors = db.get_all_contractors()

    if contractors:
        st.success(f"Connected to Supabase! Found {len(contractors)} contractor(s)")

        # Display first contractor
        contractor = contractors[0]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Contact Information")
            st.write(f"**Company:** {contractor['company_name']}")
            st.write(f"**Contact:** {contractor.get('contact_person', 'N/A')}")
            st.write(f"**Phone:** {contractor.get('phone', 'N/A')}")
            st.write(f"**Email:** {contractor.get('email', 'N/A')}")
            st.write(f"**Website:** {contractor.get('website', 'N/A')}")
            st.write(f"**City:** {contractor.get('city', 'N/A')}, {contractor.get('state', 'N/A')}")

        with col2:
            st.markdown("### Lead Information")
            st.write(f"**Lead Score:** {contractor.get('lead_score', 'N/A')}/10")
            st.write(f"**Company Type:** {contractor.get('company_type', 'N/A')}")
            st.write(f"**Specializations:** {contractor.get('specializations', 'N/A')}")
            st.write(f"**Glazing Opportunities:** {contractor.get('glazing_opportunity_types', 'N/A')}")
            st.write(f"**Source:** {contractor.get('source', 'N/A')}")

        with st.expander("Profile Notes"):
            st.write(contractor.get('profile_notes', 'No notes available'))

        with st.expander("Outreach Angle"):
            st.write(contractor.get('outreach_angle', 'No outreach angle available'))

    else:
        st.warning("No contractors found. Run the SQL schema to insert test data.")

elif page == "Contractor Discovery":
    st.title("Contractor Discovery")
    st.markdown("Search for contractors on Google Maps and save them to your database")

    # Initialize search query in session state if not exists
    if 'search_query' not in st.session_state:
        st.session_state.search_query = "bathroom remodeling Jacksonville FL"

    # Search configuration
    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input(
            "Search Query",
            value=st.session_state.search_query,
            help="Enter a search term as you would search on Google Maps"
        )

    with col2:
        max_results = st.number_input(
            "Max Results",
            min_value=5,
            max_value=50,
            value=20,
            help="Maximum number of results to retrieve"
        )

    # Predefined search templates
    st.subheader("Quick Search Templates")
    template_cols = st.columns(4)

    templates = [
        "bathroom remodeling Jacksonville FL",
        "kitchen renovation Jacksonville FL",
        "custom home builder Jacksonville FL",
        "general contractor Jacksonville FL"
    ]

    for idx, template in enumerate(templates):
        with template_cols[idx]:
            if st.button(template, key=f"template_{idx}"):
                st.session_state.search_query = template
                st.rerun()

    st.markdown("---")

    # Search button
    if st.button("Search for Contractors", type="primary", use_container_width=True):
        with st.spinner(f"Searching Google Maps for: {search_query}..."):
            try:
                # Import scraper module
                from modules.scraper import run_scraper

                # Run the scraper
                results = run_scraper(search_query, max_results, db)

                # Display results with better duplicate messaging
                st.success(f"Search complete!")

                # Show notification if duplicates were found
                if results['duplicates'] > 0:
                    st.info(f"Found {results['duplicates']} duplicate(s) already in database - showing only NEW contractors below")

                # Show metrics
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("Total Found", results['total_found'], help="Total results from Google Places")
                with metric_cols[1]:
                    st.metric("New Contractors", len(results['contractors']), help="New contractors (not duplicates)")
                with metric_cols[2]:
                    st.metric("Saved", results['saved'], help="Successfully saved to database")
                with metric_cols[3]:
                    st.metric("Duplicates Skipped", results['duplicates'], help="Already in database")

                st.markdown("---")

                # Show discovered contractors (only new ones)
                if results['contractors']:
                    st.subheader(f"{len(results['contractors'])} New Contractor(s)")

                    if results['duplicates'] > 0:
                        st.caption(f"Showing only new contractors • {results['duplicates']} duplicates were automatically skipped")

                    for idx, contractor in enumerate(results['contractors'], 1):
                        with st.expander(f"{idx}. {contractor.get('company_name', 'Unknown')} {contractor.get('google_rating', 'N/A')}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write(f"**Phone:** {contractor.get('phone', 'N/A')}")
                                st.write(f"**Address:** {contractor.get('address', 'N/A')}")
                                st.write(f"**City:** {contractor.get('city', 'N/A')}")

                            with col2:
                                st.write(f"**Rating:** {contractor.get('google_rating', 'N/A')} ({contractor.get('review_count', 0)} reviews)")
                                st.write(f"**Website:** {contractor.get('website', 'N/A')}")
                                st.write(f"**Source:** Google Places API")

                elif results['duplicates'] > 0:
                    st.warning(f"All {results['duplicates']} result(s) were duplicates! Try a different search or increase max results.")
                else:
                    st.warning("No contractors found. Try a different search query.")

            except Exception as e:
                st.error(f"Error during search: {e}")
                st.info("Note: Google Maps scraping may require additional setup or API access. Consider using Google Places API for production use.")

    # Recent searches
    st.markdown("---")
    st.subheader("Tips for Better Results")
    st.markdown("""
    **Search Strategy:**
    - Include location (city + state) in your search
    - Use specific trade terms: "bathroom remodeling", "kitchen renovation", "custom cabinets"
    - Try different variations: "general contractor", "home builder", "remodeling contractor"

    **Pagination & Duplicates:**
    - The system fetches up to 60 results (3 pages) from Google Places
    - Duplicates are automatically filtered - only NEW contractors are shown
    - If all results are duplicates, try varying your search query
    - Increase "Max Results" to fetch more contractors

    **Best Practices:**
    - Each search respects Google's rate limits (2s delay between pages)
    - Contractors are saved with phone, website, ratings, and review counts
    """)

elif page == "Website Enrichment":
    st.title("Website Enrichment with Claude AI")
    st.markdown("Analyze contractor websites to extract key information and generate lead scores")

    # Import enrichment module
    from modules.enrichment import ContractorEnrichment
    import asyncio

    enricher = ContractorEnrichment()

    # Get pending enrichments
    pending_contractors = enricher.get_pending_enrichments(limit=50)

    # Display stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pending Enrichment", len(pending_contractors))

    with col2:
        # Count enriched
        try:
            enriched = db.client.table("contractors").select("*", count="exact").eq("enrichment_status", "completed").execute()
            enriched_count = enriched.count if hasattr(enriched, 'count') else len(enriched.data)
            st.metric("Enriched", enriched_count)
        except:
            st.metric("Enriched", "N/A")

    with col3:
        # Count failed
        try:
            failed = db.client.table("contractors").select("*", count="exact").eq("enrichment_status", "failed").execute()
            failed_count = failed.count if hasattr(failed, 'count') else len(failed.data)
            st.metric("Failed", failed_count)
        except:
            st.metric("Failed", "N/A")

    st.markdown("---")

    # Show pending contractors
    if pending_contractors:
        st.subheader(f"Contractors Pending Enrichment ({len(pending_contractors)})")

        # Selection options
        enrich_option = st.radio(
            "Select contractors to enrich:",
            ["Enrich first 5", "Enrich first 10", "Enrich all pending", "Select specific contractors"],
            horizontal=True
        )

        # Get contractor IDs based on selection
        selected_ids = []

        if enrich_option == "Enrich first 5":
            selected_ids = [c['id'] for c in pending_contractors[:5]]
            st.info(f"Will enrich {len(selected_ids)} contractors")

        elif enrich_option == "Enrich first 10":
            selected_ids = [c['id'] for c in pending_contractors[:10]]
            st.info(f"Will enrich {len(selected_ids)} contractors")

        elif enrich_option == "Enrich all pending":
            selected_ids = [c['id'] for c in pending_contractors]
            st.warning(f"Will enrich all {len(selected_ids)} contractors. This may take several minutes.")

        elif enrich_option == "Select specific contractors":
            # Show contractor selection
            st.markdown("**Select contractors:**")
            for contractor in pending_contractors[:20]:  # Limit display to 20
                checkbox_col, info_col = st.columns([1, 5])
                with checkbox_col:
                    if st.checkbox("", key=f"select_{contractor['id']}"):
                        selected_ids.append(contractor['id'])
                with info_col:
                    website_display = contractor.get('website', 'No website')
                    st.write(f"**{contractor['company_name']}** - {contractor.get('city', 'Unknown')} - {website_display}")

            if len(pending_contractors) > 20:
                st.info(f"Showing first 20 of {len(pending_contractors)} pending contractors")

        # Display selected contractors
        with st.expander("View Pending Contractors", expanded=False):
            for idx, contractor in enumerate(pending_contractors[:10], 1):
                st.write(f"{idx}. **{contractor['company_name']}** - {contractor.get('city', 'N/A')} - Website: {contractor.get('website', 'No website')}")

            if len(pending_contractors) > 10:
                st.caption(f"... and {len(pending_contractors) - 10} more")

        st.markdown("---")

        # Enrichment button
        if st.button("Start Enrichment", type="primary", disabled=len(selected_ids) == 0, use_container_width=True):
            if selected_ids:
                st.info(f"Starting enrichment for {len(selected_ids)} contractor(s)...")

                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()

                results = []

                # Process each contractor
                for idx, contractor_id in enumerate(selected_ids):
                    # Update progress
                    progress = (idx) / len(selected_ids)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing contractor {idx + 1} of {len(selected_ids)}...")

                    # Run enrichment
                    result = asyncio.run(enricher.enrich_contractor(contractor_id))
                    results.append(result)

                    # Show intermediate result
                    with results_container:
                        if result['success']:
                            st.success(f"{result['message']}")
                        else:
                            st.warning(f"{result['message']}")

                # Complete progress
                progress_bar.progress(1.0)
                status_text.text("Enrichment complete!")

                st.markdown("---")

                # Display summary
                st.subheader("Enrichment Summary")

                summary_col1, summary_col2, summary_col3 = st.columns(3)

                successful = sum(1 for r in results if r['success'])
                failed = len(results) - successful

                with summary_col1:
                    st.metric("Total Processed", len(results))
                with summary_col2:
                    st.metric("Successful", successful)
                with summary_col3:
                    st.metric("Failed", failed)

                # Show detailed results
                with st.expander("Detailed Results", expanded=True):
                    for result in results:
                        if result['success'] and result.get('enrichment_data'):
                            data = result['enrichment_data']
                            st.markdown(f"**Contractor ID {result['contractor_id']}**")
                            st.write(f"- Score: {data.get('glazing_opportunity_score', 'N/A')}/10")
                            st.write(f"- Company Type: {data.get('company_type', 'N/A')}")
                            st.write(f"- Specializations: {', '.join(data.get('specializations', []))}")
                            st.write(f"- Glazing Opportunities: {', '.join(data.get('glazing_opportunity_types', []))}")
                            st.write(f"- Outreach Angle: {data.get('outreach_angle', 'N/A')}")
                            st.markdown("---")

                st.balloons()

    else:
        st.info("No contractors pending enrichment!")
        st.markdown("""
        All contractors with websites have been enriched. To enrich more contractors:
        1. Go to "Contractor Discovery" to find new contractors
        2. Make sure they have website URLs
        3. Return here to run enrichment
        """)

    # Manual enrichment section
    st.markdown("---")
    st.subheader("Re-enrich Specific Contractor")

    contractor_id_input = st.number_input(
        "Enter Contractor ID",
        min_value=1,
        value=1,
        help="Enter the ID of a contractor to re-run enrichment"
    )

    if st.button("Re-enrich This Contractor"):
        with st.spinner(f"Re-enriching contractor {contractor_id_input}..."):
            result = asyncio.run(enricher.enrich_contractor(contractor_id_input))

            if result['success']:
                st.success(result['message'])
                if result.get('enrichment_data'):
                    st.json(result['enrichment_data'])
            else:
                st.error(result['message'])

    # Tips section
    st.markdown("---")
    st.subheader("About Website Enrichment")
    st.markdown("""
    **What it does:**
    - Fetches content from contractor websites
    - Analyzes with Claude AI to extract key business information
    - Generates lead scores (1-10) based on glazing service fit
    - Identifies best outreach angles

    **Lead Scoring:**
    - **9-10:** Bathroom remodelers, shower specialists, commercial storefront
    - **7-8:** Kitchen remodelers, custom home builders, office renovation
    - **5-6:** Deck builders, pool contractors, custom furniture
    - **Below 5:** Not relevant (HVAC, roofing, electrical, etc.) - automatically filtered

    **Note:** Only contractors with score ≥5 are kept in the database.
    """)

elif page == "Contractor Directory":
    st.title("Contractor Directory")
    st.markdown("Search, filter, and browse all contractors in your database")

    # Get all contractors
    all_contractors = db.get_all_contractors()

    if not all_contractors:
        st.warning("No contractors found. Go to 'Contractor Discovery' to add contractors.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Contractors", len(all_contractors))

        with col2:
            enriched_count = len([c for c in all_contractors if c.get('enrichment_status') == 'completed'])
            st.metric("Enriched", enriched_count)

        with col3:
            high_score_count = len([c for c in all_contractors if c.get('lead_score') and c.get('lead_score') >= 8])
            st.metric("High Priority (8+)", high_score_count)

        with col4:
            pending_count = len([c for c in all_contractors if c.get('enrichment_status') == 'pending'])
            st.metric("Pending", pending_count)

        st.markdown("---")

        # Search and Filters
        st.subheader("Search & Filter")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            search_term = st.text_input("Search company name", placeholder="Enter company name...")

        with filter_col2:
            city_filter = st.multiselect(
                "Filter by City",
                options=sorted(list(set([c.get('city', 'Unknown') for c in all_contractors if c.get('city')]))),
                default=[]
            )

        with filter_col3:
            status_filter = st.multiselect(
                "Enrichment Status",
                options=["pending", "completed", "failed"],
                default=[]
            )

        # Additional filters
        filter_col4, filter_col5, filter_col6 = st.columns(3)

        with filter_col4:
            company_type_filter = st.multiselect(
                "Company Type",
                options=["residential", "commercial", "both"],
                default=[]
            )

        with filter_col5:
            min_score = st.number_input("Min Lead Score", min_value=0, max_value=10, value=0)

        with filter_col6:
            sort_by = st.selectbox(
                "Sort By",
                options=["Company Name", "Lead Score (High to Low)", "Lead Score (Low to High)", "City", "Date Added (Newest)", "Date Added (Oldest)"]
            )

        # Apply filters
        filtered_contractors = all_contractors.copy()

        # Search term filter
        if search_term:
            filtered_contractors = [
                c for c in filtered_contractors
                if search_term.lower() in c.get('company_name', '').lower()
            ]

        # City filter
        if city_filter:
            filtered_contractors = [
                c for c in filtered_contractors
                if c.get('city') in city_filter
            ]

        # Status filter
        if status_filter:
            filtered_contractors = [
                c for c in filtered_contractors
                if c.get('enrichment_status') in status_filter
            ]

        # Company type filter
        if company_type_filter:
            filtered_contractors = [
                c for c in filtered_contractors
                if c.get('company_type') in company_type_filter
            ]

        # Score filter
        filtered_contractors = [
            c for c in filtered_contractors
            if not c.get('lead_score') or c.get('lead_score', 0) >= min_score
        ]

        # Sort contractors
        if sort_by == "Company Name":
            filtered_contractors.sort(key=lambda x: x.get('company_name', '').lower())
        elif sort_by == "Lead Score (High to Low)":
            filtered_contractors.sort(key=lambda x: x.get('lead_score', 0), reverse=True)
        elif sort_by == "Lead Score (Low to High)":
            filtered_contractors.sort(key=lambda x: x.get('lead_score', 0))
        elif sort_by == "City":
            filtered_contractors.sort(key=lambda x: x.get('city', '').lower())
        elif sort_by == "Date Added (Newest)":
            filtered_contractors.sort(key=lambda x: x.get('date_added', ''), reverse=True)
        elif sort_by == "Date Added (Oldest)":
            filtered_contractors.sort(key=lambda x: x.get('date_added', ''))

        st.markdown("---")

        # Results count
        st.subheader(f"Results: {len(filtered_contractors)} contractor(s)")

        if filtered_contractors:
            # Display as cards with key info
            for contractor in filtered_contractors:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                    with col1:
                        st.markdown(f"**{contractor.get('company_name', 'Unknown')}**")
                        st.caption(f"{contractor.get('city', 'Unknown')}, {contractor.get('state', 'FL')}")

                    with col2:
                        score = contractor.get('lead_score')
                        if score:
                            if score >= 8:
                                st.success(f"Score: {score}/10 High Priority")
                            elif score >= 6:
                                st.info(f"Score: {score}/10")
                            else:
                                st.warning(f"Score: {score}/10")
                        else:
                            st.write("Score: Not scored")

                    with col3:
                        status = contractor.get('enrichment_status', 'unknown')
                        if status == 'completed':
                            st.success("Enriched")
                        elif status == 'pending':
                            st.warning("Pending")
                        else:
                            st.error("Failed")

                    with col4:
                        # View details button - navigate to detail page
                        if st.button("View", key=f"view_{contractor['id']}"):
                            st.session_state['selected_contractor_id'] = contractor['id']
                            st.session_state['navigate_to'] = "Contractor Detail"
                            st.rerun()

                    # Additional info in expander
                    with st.expander("Quick Info"):
                        info_col1, info_col2 = st.columns(2)

                        with info_col1:
                            st.write(f"**Phone:** {contractor.get('phone', 'N/A')}")
                            st.write(f"**Email:** {contractor.get('email', 'N/A')}")
                            st.write(f"**Website:** {contractor.get('website', 'N/A')}")

                        with info_col2:
                            st.write(f"**Type:** {contractor.get('company_type', 'N/A')}")
                            specializations = contractor.get('specializations', 'N/A')
                            if specializations and specializations != 'N/A':
                                st.write(f"**Specializations:** {specializations[:50]}...")
                            else:
                                st.write(f"**Specializations:** {specializations}")

                    st.markdown("---")

        else:
            st.info("No contractors match your filters. Try adjusting your search criteria.")

        # Quick actions
        st.markdown("---")
        st.subheader("Quick Actions")

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("Export All to CSV", use_container_width=True):
                st.info("Go to 'Bulk Actions' page for export functionality")

        with action_col2:
            if st.button("Add New Contractor", use_container_width=True):
                st.info("Go to 'Add/Import Contractors' page")

elif page == "Contractor Detail":
    st.title("Contractor Detail")

    # Import outreach module
    from modules.outreach import OutreachGenerator

    outreach_gen = OutreachGenerator()

    # Get all contractors
    all_contractors = db.get_all_contractors()

    if not all_contractors:
        st.warning("No contractors found. Please add contractors first.")
    else:
        # Contractor selector
        contractor_options = {
            f"{c['company_name']} (ID: {c['id']})": c['id']
            for c in all_contractors
        }

        # Check if a contractor was selected from Directory
        default_index = 0
        if 'selected_contractor_id' in st.session_state:
            selected_id = st.session_state['selected_contractor_id']
            # Find the index of this contractor in the options
            for idx, (name, cid) in enumerate(contractor_options.items()):
                if cid == selected_id:
                    default_index = idx
                    break

        selected_name = st.selectbox(
            "Select Contractor",
            options=list(contractor_options.keys()),
            index=default_index
        )

        contractor_id = contractor_options[selected_name]
        contractor = db.get_contractor_by_id(contractor_id)

        if contractor:
            st.markdown("---")

            # Two column layout for contractor info
            info_col1, info_col2 = st.columns(2)

            with info_col1:
                st.markdown("### Contact Information")
                st.write(f"**Company:** {contractor['company_name']}")
                st.write(f"**Contact:** {contractor.get('contact_person', 'N/A')}")

                # Phone with copy
                phone = contractor.get('phone', 'N/A')
                if phone != 'N/A':
                    st.write(f"**Phone:** {phone}")
                    if st.button("Copy Phone", key="copy_phone"):
                        st.code(phone)
                else:
                    st.write(f"**Phone:** {phone}")

                # Email with copy
                email = contractor.get('email', 'N/A')
                if email != 'N/A':
                    st.write(f"**Email:** {email}")
                    if st.button("Copy Email", key="copy_email"):
                        st.code(email)
                else:
                    st.write(f"**Email:** {email}")

                website = contractor.get('website', 'N/A')
                if website != 'N/A':
                    st.write(f"**Website:** [{website}]({website})")
                else:
                    st.write(f"**Website:** {website}")

                st.write(f"**Address:** {contractor.get('address', 'N/A')}")
                st.write(f"**City:** {contractor.get('city', 'N/A')}, {contractor.get('state', 'FL')}")

            with info_col2:
                st.markdown("### Company Profile")

                # Lead score with color
                score = contractor.get('lead_score')
                if score:
                    if score >= 8:
                        st.success(f"**Lead Score:** {score}/10 High Priority")
                    elif score >= 6:
                        st.info(f"**Lead Score:** {score}/10")
                    else:
                        st.warning(f"**Lead Score:** {score}/10")
                else:
                    st.write(f"**Lead Score:** Not scored")

                st.write(f"**Company Type:** {contractor.get('company_type', 'N/A')}")
                st.write(f"**Enrichment Status:** {contractor.get('enrichment_status', 'N/A')}")

                # Specializations as tags
                specializations = contractor.get('specializations', '')
                if specializations:
                    st.write("**Specializations:**")
                    for spec in specializations.split(','):
                        st.caption(f"• {spec.strip()}")

                # Glazing opportunities
                opportunities = contractor.get('glazing_opportunity_types', '')
                if opportunities:
                    st.write("**Glazing Opportunities:**")
                    for opp in opportunities.split(','):
                        st.caption(f"• {opp.strip()}")

            # Profile notes and outreach angle
            col1, col2 = st.columns(2)

            with col1:
                with st.expander("Profile Notes", expanded=False):
                    st.write(contractor.get('profile_notes', 'No notes available'))

            with col2:
                with st.expander("Outreach Angle", expanded=False):
                    st.write(contractor.get('outreach_angle', 'No outreach angle available'))

            st.markdown("---")

            # Outreach Materials Section
            st.markdown("### Outreach Materials")

            # Check if contractor has outreach materials
            materials = outreach_gen.get_outreach_materials(contractor_id)

            has_materials = len(materials['emails']) > 0 or len(materials['scripts']) > 0

            if not has_materials:
                st.info("No outreach materials generated yet for this contractor.")

                # Generate button
                if contractor.get('enrichment_status') == 'completed':
                    if st.button("Generate Outreach Materials", type="primary", use_container_width=True):
                        with st.spinner("Generating personalized outreach materials..."):
                            result = outreach_gen.generate_all_outreach(contractor_id)

                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
                else:
                    st.warning("Contractor must be enriched before generating outreach materials.")
                    st.info("Go to 'Website Enrichment' page to enrich this contractor first.")

            else:
                # Display outreach materials in tabs
                outreach_tab1, outreach_tab2 = st.tabs(["Email Templates", "Call Scripts"])

                with outreach_tab1:
                    st.markdown("#### Email Templates")

                    if materials['emails']:
                        for idx, email in enumerate(materials['emails'], 1):
                            with st.expander(f"Email {idx}: {email.get('subject', 'No subject')}", expanded=idx==1):
                                st.markdown(f"**Subject:** {email.get('subject', 'N/A')}")
                                st.markdown("**Body:**")
                                st.text_area(
                                    "Email body",
                                    value=email.get('body', ''),
                                    height=200,
                                    key=f"email_{email['id']}",
                                    label_visibility="collapsed"
                                )

                                # Copy buttons
                                copy_col1, copy_col2 = st.columns(2)
                                with copy_col1:
                                    if st.button(f"Copy Subject", key=f"copy_subj_{email['id']}"):
                                        st.code(email.get('subject', ''))
                                with copy_col2:
                                    if st.button(f"Copy Body", key=f"copy_body_{email['id']}"):
                                        st.code(email.get('body', ''))
                    else:
                        st.info("No email templates available")

                with outreach_tab2:
                    st.markdown("#### Call Scripts")

                    if materials['scripts']:
                        for idx, script in enumerate(materials['scripts'], 1):
                            script_num = script['type'].split('_')[1]
                            with st.expander(f"Call Script {script_num}", expanded=idx==1):
                                st.text_area(
                                    "Script content",
                                    value=script.get('content', ''),
                                    height=300,
                                    key=f"script_{script['id']}",
                                    label_visibility="collapsed"
                                )

                                if st.button(f"Copy Script", key=f"copy_script_{script['id']}"):
                                    st.code(script.get('content', ''))
                    else:
                        st.info("No call scripts available")

                # Regenerate button
                st.markdown("---")
                if st.button("Regenerate All Outreach Materials", key="regenerate_outreach"):
                    with st.spinner("Regenerating outreach materials..."):
                        result = outreach_gen.regenerate_outreach(contractor_id)

                        if result['success']:
                            st.success("Outreach materials regenerated!")
                            st.rerun()
                        else:
                            st.error(f"{result['message']}")

            # Interaction tracking section
            st.markdown("---")
            st.markdown("### Interaction Tracking")

            track_col1, track_col2 = st.columns([2, 1])

            with track_col1:
                status = st.selectbox(
                    "Status",
                    ["Not Contacted", "Called - No Answer", "Called - Connected",
                     "Email Sent", "Follow-up Scheduled", "Meeting Booked", "Won", "Lost"],
                    key="interaction_status"
                )

            with track_col2:
                user_name = st.text_input("Your Name", key="user_name")

            notes = st.text_area("Notes", key="interaction_notes", height=100)

            if st.button("Log Interaction", type="primary"):
                if db.log_interaction(contractor_id, status, notes, user_name):
                    st.success("Interaction logged successfully!")
                else:
                    st.error("Failed to log interaction")

            # Interaction history
            with st.expander("Interaction History", expanded=False):
                history = db.get_interaction_history(contractor_id)

                if history:
                    for interaction in history:
                        st.markdown(f"**{interaction.get('status', 'N/A')}** - {interaction.get('timestamp', 'N/A')}")
                        if interaction.get('user_name'):
                            st.caption(f"By: {interaction['user_name']}")
                        if interaction.get('notes'):
                            st.write(f"Notes: {interaction['notes']}")
                        st.markdown("---")
                else:
                    st.info("No interactions logged yet")

elif page == "Bulk Actions":
    st.title("Bulk Actions")
    st.markdown("Export data and perform bulk operations on contractors")

    # Get all contractors
    all_contractors = db.get_all_contractors()

    if not all_contractors:
        st.warning("No contractors found. Add contractors first.")
    else:
        # Summary
        st.subheader(f"Database Summary: {len(all_contractors)} contractors")

        col1, col2, col3 = st.columns(3)

        with col1:
            enriched = len([c for c in all_contractors if c.get('enrichment_status') == 'completed'])
            st.metric("Enriched", enriched)

        with col2:
            pending = len([c for c in all_contractors if c.get('enrichment_status') == 'pending'])
            st.metric("Pending Enrichment", pending)

        with col3:
            high_priority = len([c for c in all_contractors if c.get('lead_score') and c.get('lead_score') >= 8])
            st.metric("High Priority (8+)", high_priority)

        st.markdown("---")

        # CSV Export Section
        st.subheader("Export to CSV")

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            export_type = st.radio(
                "Export Type",
                ["All Contractors", "Enriched Only", "High Priority Only (8+)", "By Lead Score Range"],
                horizontal=False
            )

        with export_col2:
            if export_type == "By Lead Score Range":
                score_min = st.number_input("Min Score", 0, 10, 5)
                score_max = st.number_input("Max Score", 0, 10, 10)

            include_outreach = st.checkbox("Include Outreach Materials", value=False, help="Note: This will create a larger file with email templates and scripts")

        # Prepare export data
        if st.button("Generate CSV", type="primary", use_container_width=True):
            import pandas as pd
            from io import StringIO

            # Filter contractors based on selection
            export_contractors = all_contractors.copy()

            if export_type == "Enriched Only":
                export_contractors = [c for c in export_contractors if c.get('enrichment_status') == 'completed']
            elif export_type == "High Priority Only (8+)":
                export_contractors = [c for c in export_contractors if c.get('lead_score') and c.get('lead_score') >= 8]
            elif export_type == "By Lead Score Range":
                export_contractors = [c for c in export_contractors if c.get('lead_score') and score_min <= c.get('lead_score') <= score_max]

            if not export_contractors:
                st.warning("No contractors match your export criteria")
            else:
                # Prepare data for CSV
                export_data = []

                for contractor in export_contractors:
                    row = {
                        "ID": contractor.get('id'),
                        "Company Name": contractor.get('company_name'),
                        "Contact Person": contractor.get('contact_person', ''),
                        "Phone": contractor.get('phone', ''),
                        "Email": contractor.get('email', ''),
                        "Website": contractor.get('website', ''),
                        "Address": contractor.get('address', ''),
                        "City": contractor.get('city', ''),
                        "State": contractor.get('state', 'FL'),
                        "ZIP": contractor.get('zip', ''),
                        "Lead Score": contractor.get('lead_score', ''),
                        "Company Type": contractor.get('company_type', ''),
                        "Specializations": contractor.get('specializations', ''),
                        "Glazing Opportunities": contractor.get('glazing_opportunity_types', ''),
                        "Profile Notes": contractor.get('profile_notes', ''),
                        "Outreach Angle": contractor.get('outreach_angle', ''),
                        "Uses Subcontractors": contractor.get('uses_subcontractors', ''),
                        "Enrichment Status": contractor.get('enrichment_status', ''),
                        "Source": contractor.get('source', ''),
                        "Google Rating": contractor.get('google_rating', ''),
                        "Review Count": contractor.get('review_count', ''),
                        "Date Added": contractor.get('date_added', '')
                    }

                    if include_outreach:
                        # Get outreach materials
                        from modules.outreach import OutreachGenerator
                        outreach_gen = OutreachGenerator()
                        materials = outreach_gen.get_outreach_materials(contractor.get('id'))

                        # Add email subjects
                        for i, email in enumerate(materials.get('emails', []), 1):
                            row[f"Email {i} Subject"] = email.get('subject', '')
                            row[f"Email {i} Body"] = email.get('body', '')

                        # Add scripts
                        for i, script in enumerate(materials.get('scripts', []), 1):
                            row[f"Call Script {i}"] = script.get('content', '')

                    export_data.append(row)

                # Create DataFrame
                df = pd.DataFrame(export_data)

                # Convert to CSV
                csv = df.to_csv(index=False)

                # Download button
                st.success(f"CSV generated with {len(export_contractors)} contractor(s)")

                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"contractors_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                # Preview
                with st.expander("Preview Data (first 5 rows)"):
                    st.dataframe(df.head())

        st.markdown("---")

        # Bulk Enrichment Section
        st.subheader("Bulk Enrichment")

        pending_enrichment = [c for c in all_contractors if c.get('enrichment_status') == 'pending' and c.get('website')]

        st.write(f"**{len(pending_enrichment)} contractors** pending enrichment with websites")

        if pending_enrichment:
            bulk_enrich_count = st.number_input(
                "Number of contractors to enrich",
                min_value=1,
                max_value=len(pending_enrichment),
                value=min(5, len(pending_enrichment))
            )

            if st.button(f"Enrich {bulk_enrich_count} Contractors", type="primary"):
                st.info("Go to 'Website Enrichment' page for bulk enrichment functionality")

        st.markdown("---")

        # Bulk Outreach Generation
        st.subheader("Bulk Outreach Generation")

        enriched_no_outreach = [c for c in all_contractors if c.get('enrichment_status') == 'completed']

        if enriched_no_outreach:
            st.write(f"**{len(enriched_no_outreach)} enriched contractors** available for outreach generation")

            if st.button("Generate Outreach for All Enriched", type="primary"):
                from modules.outreach import OutreachGenerator
                outreach_gen = OutreachGenerator()

                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()

                success_count = 0
                fail_count = 0

                for idx, contractor in enumerate(enriched_no_outreach):
                    progress = (idx + 1) / len(enriched_no_outreach)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{len(enriched_no_outreach)}: {contractor.get('company_name')}")

                    # Check if already has outreach
                    materials = outreach_gen.get_outreach_materials(contractor['id'])
                    if materials['emails'] or materials['scripts']:
                        with results_container:
                            st.info(f"Skipped {contractor.get('company_name')} (already has outreach)")
                        continue

                    # Generate outreach
                    result = outreach_gen.generate_all_outreach(contractor['id'])

                    if result['success']:
                        success_count += 1
                        with results_container:
                            st.success(f"{contractor.get('company_name')}")
                    else:
                        fail_count += 1
                        with results_container:
                            st.error(f"{contractor.get('company_name')}: {result['message']}")

                progress_bar.progress(1.0)
                status_text.text(f"Complete! {success_count} successful, {fail_count} failed")

                st.balloons()
        else:
            st.info("No enriched contractors available. Enrich contractors first.")

        st.markdown("---")

        # Database Stats
        st.subheader("Database Statistics")

        stats_col1, stats_col2, stats_col3 = st.columns(3)

        with stats_col1:
            cities = set([c.get('city') for c in all_contractors if c.get('city')])
            st.metric("Unique Cities", len(cities))

        with stats_col2:
            with_websites = len([c for c in all_contractors if c.get('website')])
            st.metric("With Websites", with_websites)

        with stats_col3:
            avg_score = sum([c.get('lead_score', 0) for c in all_contractors if c.get('lead_score')]) / max(len([c for c in all_contractors if c.get('lead_score')]), 1)
            st.metric("Avg Lead Score", f"{avg_score:.1f}")

elif page == "Add/Import Contractors":
    st.title("Add/Import Contractors")
    st.markdown("Manually add contractors or import from CSV file")

    tab1, tab2 = st.tabs(["Manual Entry", "CSV Upload"])

    with tab1:
        st.subheader("Add Single Contractor")

        with st.form("add_contractor_form"):
            col1, col2 = st.columns(2)

            with col1:
                company_name = st.text_input("Company Name *", placeholder="ABC Remodeling")
                contact_person = st.text_input("Contact Person", placeholder="John Smith")
                phone = st.text_input("Phone", placeholder="(904) 123-4567")
                email = st.text_input("Email", placeholder="contact@company.com")

            with col2:
                website = st.text_input("Website", placeholder="https://company.com")
                address = st.text_input("Address", placeholder="123 Main St")
                city = st.text_input("City *", placeholder="Jacksonville")
                state = st.text_input("State", value="FL")

            # Additional fields
            col3, col4 = st.columns(2)

            with col3:
                zip_code = st.text_input("ZIP Code", placeholder="32256")
                company_type = st.selectbox("Company Type", ["", "residential", "commercial", "both"])

            with col4:
                source = st.text_input("Source", value="manual_entry")

            submit = st.form_submit_button("Add Contractor", use_container_width=True, type="primary")

            if submit:
                if not company_name or not city:
                    st.error("Company Name and City are required")
                else:
                    # Prepare contractor data
                    contractor_data = {
                        "company_name": company_name,
                        "contact_person": contact_person if contact_person else None,
                        "phone": phone if phone else None,
                        "email": email if email else None,
                        "website": website if website else None,
                        "address": address if address else None,
                        "city": city,
                        "state": state,
                        "zip": zip_code if zip_code else None,
                        "company_type": company_type if company_type else None,
                        "enrichment_status": "pending",
                        "source": source
                    }

                    # Insert contractor
                    result = db.insert_contractor(contractor_data)

                    if result:
                        st.success(f"Added {company_name} successfully! (ID: {result['id']})")
                        st.info("Go to 'Website Enrichment' to enrich this contractor")

                        # Option to add another
                        if st.button("Add Another Contractor"):
                            st.rerun()
                    else:
                        st.error("Failed to add contractor. Please try again.")

    with tab2:
        st.subheader("Import from CSV")

        st.markdown("""
        **CSV Format Requirements:**
        - Required columns: `company_name`, `city`
        - Optional columns: `contact_person`, `phone`, `email`, `website`, `address`, `state`, `zip`, `company_type`
        - First row should be column headers
        """)

        # Download template
        if st.button("Download CSV Template"):
            import pandas as pd

            template_data = {
                "company_name": ["Example Remodeling Co", "Another Builder Inc"],
                "contact_person": ["John Smith", "Jane Doe"],
                "phone": ["(904) 123-4567", "(904) 987-6543"],
                "email": ["john@example.com", "jane@another.com"],
                "website": ["https://example.com", "https://another.com"],
                "address": ["123 Main St", "456 Oak Ave"],
                "city": ["Jacksonville", "Jacksonville Beach"],
                "state": ["FL", "FL"],
                "zip": ["32256", "32250"],
                "company_type": ["residential", "commercial"]
            }

            df_template = pd.DataFrame(template_data)
            csv_template = df_template.to_csv(index=False)

            st.download_button(
                label="Download Template CSV",
                data=csv_template,
                file_name="contractor_import_template.csv",
                mime="text/csv"
            )

        st.markdown("---")

        # File uploader
        uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                import pandas as pd

                # Read CSV
                df = pd.read_csv(uploaded_file)

                st.success(f"File uploaded! Found {len(df)} rows")

                # Preview data
                with st.expander("Preview Data"):
                    st.dataframe(df.head(10))

                # Validate required columns
                required_cols = ["company_name", "city"]
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                else:
                    # Options
                    import_col1, import_col2 = st.columns(2)

                    with import_col1:
                        auto_enrich = st.checkbox("Auto-enrich after import", value=False, help="Automatically run enrichment on contractors with websites")

                    with import_col2:
                        skip_duplicates = st.checkbox("Skip duplicates", value=True, help="Skip contractors with matching company name")

                    # Import button
                    if st.button("Import Contractors", type="primary", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        imported_count = 0
                        skipped_count = 0
                        error_count = 0

                        results_container = st.container()

                        for idx, row in df.iterrows():
                            progress = (idx + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {idx + 1}/{len(df)}: {row.get('company_name', 'Unknown')}")

                            # Check for duplicates
                            if skip_duplicates:
                                existing = db.client.table("contractors").select("id").eq("company_name", row['company_name']).execute()
                                if existing.data:
                                    skipped_count += 1
                                    with results_container:
                                        st.warning(f"Skipped {row['company_name']} (duplicate)")
                                    continue

                            # Prepare contractor data
                            contractor_data = {
                                "company_name": row['company_name'],
                                "city": row['city'],
                                "contact_person": row.get('contact_person') if pd.notna(row.get('contact_person')) else None,
                                "phone": row.get('phone') if pd.notna(row.get('phone')) else None,
                                "email": row.get('email') if pd.notna(row.get('email')) else None,
                                "website": row.get('website') if pd.notna(row.get('website')) else None,
                                "address": row.get('address') if pd.notna(row.get('address')) else None,
                                "state": row.get('state', 'FL') if pd.notna(row.get('state')) else 'FL',
                                "zip": row.get('zip') if pd.notna(row.get('zip')) else None,
                                "company_type": row.get('company_type') if pd.notna(row.get('company_type')) else None,
                                "enrichment_status": "pending",
                                "source": "csv_import"
                            }

                            # Insert contractor
                            result = db.insert_contractor(contractor_data)

                            if result:
                                imported_count += 1
                                with results_container:
                                    st.success(f"Imported {row['company_name']}")

                                # Auto-enrich if requested
                                if auto_enrich and contractor_data['website']:
                                    from modules.enrichment import ContractorEnrichment
                                    import asyncio

                                    enricher = ContractorEnrichment()
                                    enrich_result = asyncio.run(enricher.enrich_contractor(result['id']))

                                    if enrich_result['success']:
                                        with results_container:
                                            st.info(f"  Enriched: Score {enrich_result['enrichment_data'].get('glazing_opportunity_score', 'N/A')}/10")
                            else:
                                error_count += 1
                                with results_container:
                                    st.error(f"Failed to import {row['company_name']}")

                        progress_bar.progress(1.0)
                        status_text.text("Import complete!")

                        # Summary
                        st.markdown("---")
                        st.subheader("Import Summary")

                        summary_col1, summary_col2, summary_col3 = st.columns(3)

                        with summary_col1:
                            st.metric("Imported", imported_count)
                        with summary_col2:
                            st.metric("Skipped", skipped_count)
                        with summary_col3:
                            st.metric("Errors", error_count)

                        st.balloons()

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                st.info("Make sure your CSV file is properly formatted with column headers")

elif page == "Settings":
    st.title("Settings")
    st.info("Coming in Step 8: View API usage and system configuration")

    # Show connection status
    st.subheader("Database Connection")
    try:
        test_query = db.get_all_contractors()
        st.success("Supabase connection active")
    except Exception as e:
        st.error(f"Database error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Built for Island Glass Company")
st.sidebar.caption("Jacksonville, FL")
