"""
Settings page with API usage tracking dashboard
"""
import streamlit as st
from modules.database import Database

st.set_page_config(page_title="Settings - Island Glass Leads", page_icon="⚙️", layout="wide")

# Initialize database
db = Database()

st.title("⚙️ Settings & API Usage")

# Create tabs for different settings sections
tab1, tab2 = st.tabs(["API Usage Dashboard", "Application Settings"])

with tab1:
    st.header("Claude API Usage Tracking")
    st.markdown("Track token usage and costs for Anthropic Claude API calls")

    # Get usage data
    total_usage = db.get_total_api_usage()
    monthly_usage = db.get_api_usage_this_month()
    top_contractors = db.get_top_contractors_by_usage(limit=10)

    # Overall metrics row
    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total API Calls",
            value=f"{total_usage['total_calls']:,}"
        )

    with col2:
        st.metric(
            label="Total Tokens Used",
            value=f"{total_usage['total_tokens']:,}"
        )

    with col3:
        st.metric(
            label="Total Cost (All Time)",
            value=f"${total_usage['total_cost']:.2f}"
        )

    with col4:
        st.metric(
            label="This Month Cost",
            value=f"${monthly_usage['cost']:.2f}",
            delta=f"{monthly_usage['calls']} calls"
        )

    # Cost alert
    if monthly_usage['cost'] > 50:
        st.warning(f"⚠️ Monthly spending is ${monthly_usage['cost']:.2f}. Consider reviewing API usage.")
    elif monthly_usage['cost'] > 100:
        st.error(f"🚨 Monthly spending is ${monthly_usage['cost']:.2f}. High API usage detected!")

    st.divider()

    # Breakdown by action type
    st.subheader("📈 Usage by Action Type")

    if total_usage['by_action']:
        col1, col2, col3 = st.columns(3)

        action_names = {
            'enrichment': '🔍 Enrichment',
            'email_generation': '📧 Email Generation',
            'script_generation': '📞 Script Generation'
        }

        for i, (action, data) in enumerate(total_usage['by_action'].items()):
            col = [col1, col2, col3][i % 3]

            with col:
                st.markdown(f"**{action_names.get(action, action.title())}**")
                st.metric(
                    label="Calls",
                    value=f"{data['calls']:,}"
                )
                st.metric(
                    label="Tokens",
                    value=f"{data['tokens']:,}"
                )
                st.metric(
                    label="Cost",
                    value=f"${data['cost']:.2f}"
                )
                st.markdown("---")
    else:
        st.info("No API usage data yet. Start enriching contractors or generating outreach materials.")

    st.divider()

    # Top contractors by API usage
    st.subheader("💰 Top Contractors by API Cost")

    if top_contractors:
        st.markdown("*Contractors that have used the most API tokens/costs*")

        # Create table data
        table_data = []
        for item in top_contractors:
            table_data.append({
                "Company Name": item.get('company_name', 'Unknown'),
                "API Calls": f"{item['calls']:,}",
                "Total Tokens": f"{item['tokens']:,}",
                "Total Cost": f"${item['cost']:.2f}",
                "Avg Cost/Call": f"${(item['cost'] / item['calls']):.3f}" if item['calls'] > 0 else "$0.000"
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No contractor-specific usage data yet.")

    st.divider()

    # Pricing information
    st.subheader("💵 Claude API Pricing")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Claude Sonnet 4 (claude-sonnet-4-20250514)**")
        st.markdown("- Input: **$3.00** per million tokens")
        st.markdown("- Output: **$15.00** per million tokens")

    with col2:
        st.markdown("**Typical Costs per Action:**")
        if total_usage['by_action']:
            for action, data in total_usage['by_action'].items():
                if data['calls'] > 0:
                    avg_cost = data['cost'] / data['calls']
                    action_name = {
                        'enrichment': 'Enrichment',
                        'email_generation': 'Email Generation',
                        'script_generation': 'Script Generation'
                    }.get(action, action.title())
                    st.markdown(f"- {action_name}: **${avg_cost:.3f}** per call")
        else:
            st.markdown("- Enrichment: ~$0.02-0.05 per contractor")
            st.markdown("- Email Generation: ~$0.01-0.03 per contractor")
            st.markdown("- Script Generation: ~$0.01-0.03 per contractor")

    st.divider()

    # Monthly tracking
    st.subheader("📅 Current Month Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="API Calls This Month",
            value=f"{monthly_usage['calls']:,}"
        )

    with col2:
        st.metric(
            label="Tokens This Month",
            value=f"{monthly_usage['tokens']:,}"
        )

    with col3:
        st.metric(
            label="Cost This Month",
            value=f"${monthly_usage['cost']:.2f}"
        )

    # Estimate remaining budget
    st.markdown("---")
    st.markdown("**💡 Budget Planning:**")

    budget_col1, budget_col2 = st.columns(2)

    with budget_col1:
        # If they have a monthly budget, show remaining
        monthly_budget = st.number_input(
            "Set Monthly Budget (USD)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=10.0,
            help="Your desired monthly spending limit for Claude API"
        )

    with budget_col2:
        remaining = monthly_budget - monthly_usage['cost']
        if remaining > 0:
            st.success(f"✅ Remaining budget: **${remaining:.2f}**")
            st.caption(f"You've used {(monthly_usage['cost'] / monthly_budget * 100):.1f}% of your monthly budget")
        else:
            st.error(f"⚠️ Over budget by **${abs(remaining):.2f}**")

with tab2:
    st.header("Application Settings")

    st.subheader("🔧 General Settings")

    # Future settings can go here
    st.info("Additional application settings will be added here in future updates.")

    st.markdown("---")

    st.subheader("📊 Database Statistics")

    stats = db.get_dashboard_stats()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Total Contractors",
            value=f"{stats['total_contractors']:,}"
        )

    with col2:
        st.metric(
            label="High Priority Leads (8+)",
            value=f"{stats['high_priority_leads']:,}"
        )

    st.markdown("---")

    st.subheader("ℹ️ About")
    st.markdown("""
    **Island Glass Leads v1.0**

    A contractor lead generation and outreach tool powered by Claude AI.

    **Features:**
    - Contractor discovery and data collection
    - AI-powered website enrichment and scoring
    - Automated email and call script generation
    - API usage tracking and cost monitoring
    - Bulk actions and CSV export

    **Tech Stack:**
    - Streamlit for UI
    - Supabase (PostgreSQL) for database
    - Anthropic Claude API for AI analysis
    - Python with asyncio for async operations
    """)
