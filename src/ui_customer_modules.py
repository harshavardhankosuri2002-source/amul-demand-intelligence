"""
AMUL | AI Demand & Distribution Intelligence System
Customer-Centric & Interactive Modules UI Component
Implements:
1. Customer-Wise Intelligence & Solutions (RFM, Next-Best-Action, Human Approval)
2. Amul AI Analyst Chatbot (Natural Language Query Engine with Data Lineage)
3. Email Automation & Campaign Management (Audience Gating, Template Editor, Approval Gate, Mock Sandbox)
4. Customer Notification Centre (In-App Cards, Quiet Hours, PWA Web Push Architecture)
"""

from datetime import datetime
import json
import os
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.chatbot import AmulDataAnalystEngine
from src.campaign_manager import (
    MockSandboxEmailProvider,
    filter_campaign_audience,
    generate_campaign_draft,
)
try:
    from src.crm_models import (
        CRM_API_SCHEMAS,
        PRODUCTION_DATABASE_ARCHITECTURE,
    )
except ImportError:
    try:
        from src.crm_models import (
            CRM_API_SCHEMAS,
            PRODUCTION_DB_ARCHITECTURE_NOTE as PRODUCTION_DATABASE_ARCHITECTURE,
        )
    except Exception:
        CRM_API_SCHEMAS = {}
        PRODUCTION_DATABASE_ARCHITECTURE = """
### 🗄️ Recommended Production Database Architecture
1. **Relational Core (PostgreSQL 16+)**: Stores customers, consent records, campaigns, and audit logs with Row-Level Security.
2. **Time-Series Engine (TimescaleDB / ClickHouse)**: Ingests distribution transactions and sensor readings.
3. **In-Memory Cache (Redis Cluster)**: Real-time rate limiting, quiet hours checks, and suppression sets.
"""
from src.customer_intelligence import (
    classify_customer_segment,
    enrich_customer_dataframe,
    generate_next_best_action,
    generate_synthetic_customer_dataset,
)
from src.diagrams import DIAGRAM_G_MERMAID
from src.notification_center import (
    NotificationDispatchManager,
    is_quiet_hours,
    PWA_BROWSER_PUSH_ARCHITECTURE_GUIDE,
)
from src.visual_theme import (
    AMUL_AMBER,
    AMUL_BLUE,
    AMUL_GREEN,
    AMUL_NAVY,
    AMUL_NAVY_LIGHT,
    AMUL_RED,
    apply_amul_theme,
    format_inr,
    format_units,
)


def get_or_load_customer_data() -> pd.DataFrame:
    """Retrieves synthetic customer dataset from session state or CSV disk cache."""
    if "customer_df" not in st.session_state:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_customer_profiles.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = generate_synthetic_customer_dataset(num_records=120)
        st.session_state["customer_df"] = enrich_customer_dataframe(df)
    return st.session_state["customer_df"]


# =====================================================================
# UI 1: CUSTOMER-WISE INTELLIGENCE & SOLUTIONS
# =====================================================================
def render_customer_intelligence_ui(filtered_sales_df: pd.DataFrame):
    """Renders Customer-Wise Intelligence page with RFM drilldown, Next-Best-Action, and Approval Gate."""
    st.markdown("### 👥 Customer-Wise Intelligence & Next-Best-Action Workbench")
    st.caption("Individual RFM behavioral profiling, consent-gated Next-Best-Action suggestions, and mandatory human review.")

    st.markdown(
        """
        <div style="background-color: #FEF2F2; border-left: 4px solid #C4122F; padding: 8px 14px; border-radius: 4px; margin-bottom: 14px;">
            <div style="font-weight: 700; color: #991B1B; font-size: 0.85rem;">
                ⚠️ SYNTHETIC CUSTOMER COHORT — STRICT PRIVACY BOUNDARIES
            </div>
            <div style="color: #7F1D1D; font-size: 0.78rem;">
                This dataset contains 120 synthetic consumer records created strictly for demonstrating RFM segmentation and DPDPA 2023 consent controls.
                Sensitive attributes (allergies, medical status, religion, income) are neither modeled nor permitted for targeting. Real-world activation requires connection to an authorized CRM API.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cust_df = get_or_load_customer_data()

    # Portfolio RFM Segmentation Summary Cards
    seg_counts = cust_df["customer_segment"].value_counts()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Loyal Customers", f"{seg_counts.get('loyal', 0)}", "High frequency & spend")
    c2.metric("High-Value", f"{seg_counts.get('high-value', 0)}", "Premium order basket")
    c3.metric("New Customers", f"{seg_counts.get('new', 0)}", "<45 days tenure")
    c4.metric("Declining Engagement", f"{seg_counts.get('declining_engagement', 0)}", "At-risk of churn")
    c5.metric("Inactive", f"{seg_counts.get('inactive', 0)}", ">120 days elapsed")

    tab_profile, tab_segments, tab_approval_log = st.tabs([
        "🔍 Individual Profile & Next-Best-Action",
        "📊 Portfolio RFM Distribution",
        "📝 Human Approvals Audit Log",
    ])

    with tab_profile:
        col_sel, col_stat = st.columns([6, 6])
        with col_sel:
            customer_options = [
                f"{row['customer_id']} — {row['full_name']} ({row['city']}, {row['region']})"
                for _, row in cust_df.iterrows()
            ]
            selected_option = st.selectbox("Select Customer to Inspect:", customer_options, index=0)
            selected_cid = selected_option.split(" — ")[0].strip()
            customer_row = cust_df[cust_df["customer_id"] == selected_cid].iloc[0]

        with col_stat:
            consent_val = customer_row.get("consent_status", "UNKNOWN")
            consent_color = "#16A34A" if consent_val == "CONSENTED_MARKETING" else ("#D97706" if consent_val == "TRANSACTIONAL_ONLY" else "#DC2626")
            has_ticket = customer_row.get("has_open_complaint", False)

            st.markdown(
                f"""
                <div class="amul-panel" style="padding: 10px 14px; margin-top: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #0B2545;">DPDPA Consent Status:</span>
                        <span style="background-color: {consent_color}20; color: {consent_color}; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem;">
                            {consent_val}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                        <span style="font-weight: 700; color: #0B2545;">Active Support Issue:</span>
                        <span style="color: {'#DC2626' if has_ticket else '#16A34A'}; font-weight: 600; font-size: 0.8rem;">
                            {'⚠️ OPEN TICKET (Marketing Suppressed)' if has_ticket else '✅ No Open Complaints'}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Customer Detail Cards
        prof_c1, prof_c2, prof_c3 = st.columns(3)

        with prof_c1:
            st.markdown(
                f"""
                <div class="amul-kpi-card" style="text-align: left; height: 100%;">
                    <div class="amul-kpi-title">Identity & Demographics</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0B2545; margin-top: 4px;">{customer_row['full_name']}</div>
                    <div style="font-size: 0.8rem; color: #475569; margin-top: 4px;">
                        <b>Email:</b> {customer_row['email']}<br/>
                        <b>Phone:</b> {customer_row['phone_masked']}<br/>
                        <b>Location:</b> {customer_row['city']}, {customer_row['region']}<br/>
                        <b>Preferred Language:</b> {customer_row.get('preferred_language', 'English')}<br/>
                        <b>Tenure:</b> {customer_row.get('tenure_days', 'N/A')} days
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with prof_c2:
            st.markdown(
                f"""
                <div class="amul-kpi-card" style="text-align: left; height: 100%;">
                    <div class="amul-kpi-title">RFM & Purchasing Behavior</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #C4122F; margin-top: 4px;">Segment: {customer_row['customer_segment'].upper()}</div>
                    <div style="font-size: 0.8rem; color: #475569; margin-top: 4px;">
                        <b>Annual Spend:</b> ₹{customer_row.get('total_spent_inr', 0):,}<br/>
                        <b>Order Frequency:</b> {customer_row.get('orders_count', 0)} orders/year<br/>
                        <b>Average Basket (AOV):</b> ₹{customer_row.get('average_order_value_inr', 0):,}<br/>
                        <b>Days Since Last Order:</b> {customer_row.get('days_since_last_purchase', 0)} days<br/>
                        <b>Momentum:</b> <span style="font-weight: 600; color: {'#16A34A' if customer_row.get('spending_momentum') == 'growing' else ('#DC2626' if customer_row.get('spending_momentum') == 'declining' else '#475569')}">{customer_row.get('spending_momentum', 'steady').upper()}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with prof_c3:
            st.markdown(
                f"""
                <div class="amul-kpi-card" style="text-align: left; height: 100%;">
                    <div class="amul-kpi-title">Affinity & Engagement</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0B2545; margin-top: 4px;">Tier: {customer_row.get('loyalty_tier', 'Bronze')}</div>
                    <div style="font-size: 0.8rem; color: #475569; margin-top: 4px;">
                        <b>Loyalty Points:</b> {customer_row.get('loyalty_points', 0):,} pts<br/>
                        <b>Favorite Category:</b> {customer_row.get('favorite_category', 'Dairy')}<br/>
                        <b>Preferred Product:</b> {customer_row.get('favorite_product', 'Amul Taaza')}<br/>
                        <b>Campaigns Received:</b> {customer_row.get('campaigns_received', 0)}<br/>
                        <b>Open Rate:</b> {customer_row.get('open_rate_pct', 0)}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Explainable Next-Best-Action Box
        nba = generate_next_best_action(customer_row.to_dict())
        status_banner = ""
        if nba.get("is_blocked_by_consent"):
            status_banner = f"<div style='background-color: #FEE2E2; border: 1px solid #F87171; border-radius: 4px; padding: 6px 12px; margin-bottom: 8px; color: #B91C1C; font-weight: 700; font-size: 0.8rem;'>⚠️ {nba.get('consent_block_reason')}</div>"

        st.markdown(
            f"""
            <div class="amul-panel" style="border-left: 5px solid {'#C4122F' if not nba.get('is_blocked_by_consent') else '#94A3B8'};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="font-weight: 700; color: #0B2545; font-size: 1.05rem;">
                        🎯 Next-Best-Action: {nba.get('action_title')}
                    </div>
                    <span class="amul-badge-alert" style="background-color: #0B2545; color: white;">Priority: {nba.get('priority')}</span>
                </div>
                {status_banner}
                <div style="font-size: 0.85rem; color: #334155; margin-bottom: 8px;">
                    {nba.get('description')}
                </div>
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 8px 12px; font-size: 0.8rem; color: #475569;">
                    <b>Explainable Rationale:</b> {nba.get('rationale')}<br/>
                    <b>Supporting Metrics:</b> {nba.get('supporting_metrics')}<br/>
                    <b>Suggested Product / Category:</b> {nba.get('suggested_product')} ({nba.get('suggested_category')})<br/>
                    <b>Recommended Delivery Channel:</b> {nba.get('recommended_channel').upper()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Human Review & Approval Action
        st.markdown("##### 🛡️ Human-in-the-Loop Review Gate")
        st.caption("In adherence to governance protocols, no promotional or service campaign is triggered without explicit authorized review.")

        if "approval_logs" not in st.session_state:
            st.session_state["approval_logs"] = []

        is_already_approved = any(
            log.get("customer_id") == selected_cid and log.get("action_title") == nba.get("action_title")
            for log in st.session_state["approval_logs"]
        )

        app_c1, app_c2 = st.columns([6, 6])
        with app_c1:
            reviewer_role = st.selectbox("Reviewer Role", ["Area Sales Manager", "CRM Specialist", "Compliance Officer", "Marketing Analyst"], index=0)
            approval_notes = st.text_input("Reviewer Audit Notes", value="Verified consent and purchase history fit.", max_chars=120)

        with app_c2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if nba.get("is_blocked_by_consent"):
                st.button("🔒 Action Blocked by Privacy Consent Rules", disabled=True, use_container_width=True)
            elif is_already_approved:
                st.success("✅ Action Already Approved and Queued in Campaign Pipeline!")
            else:
                if st.button("Approve Next-Best-Action for Dispatch Queue", use_container_width=True):
                    log_entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "customer_id": selected_cid,
                        "customer_name": customer_row["full_name"],
                        "segment": customer_row["customer_segment"],
                        "action_title": nba.get("action_title"),
                        "reviewer_role": reviewer_role,
                        "notes": approval_notes,
                        "channel": nba.get("recommended_channel"),
                        "status": "APPROVED_QUEUED",
                    }
                    st.session_state["approval_logs"].append(log_entry)
                    st.toast(f"Approved action for {customer_row['full_name']}!", icon="✅")
                    st.rerun()

    with tab_segments:
        st.markdown("#### 📊 Customer Cohort Distribution & Behavioral Characteristics")
        s_col1, s_col2 = st.columns([6, 6])

        with s_col1:
            fig_pie = px.pie(
                values=seg_counts.values,
                names=[s.replace("_", " ").title() for s in seg_counts.index],
                title="Customer Segment Share (N=120 Synthetic Cohort)",
                color_discrete_sequence=[AMUL_NAVY, AMUL_RED, AMUL_AMBER, AMUL_GREEN, "#64748B"],
            )
            apply_amul_theme(fig_pie, "Customer Segment Share", height=340)
            st.plotly_chart(fig_pie, use_container_width=True)

        with s_col2:
            seg_metrics = cust_df.groupby("customer_segment").agg({
                "total_spent_inr": "mean",
                "orders_count": "mean",
                "days_since_last_purchase": "mean",
                "customer_id": "count",
            }).reset_index().rename(columns={
                "customer_segment": "Segment",
                "total_spent_inr": "Avg Spend (₹)",
                "orders_count": "Avg Orders/Yr",
                "days_since_last_purchase": "Avg Recency (Days)",
                "customer_id": "Count",
            })
            seg_metrics["Avg Spend (₹)"] = seg_metrics["Avg Spend (₹)"].apply(lambda x: f"₹{x:,.0f}")
            seg_metrics["Avg Orders/Yr"] = seg_metrics["Avg Orders/Yr"].round(1)
            seg_metrics["Avg Recency (Days)"] = seg_metrics["Avg Recency (Days)"].round(0).astype(int)
            st.markdown("##### Segment Profiles & Benchmark Metrics")
            st.dataframe(seg_metrics, use_container_width=True)

    with tab_approval_log:
        st.markdown("#### 📝 Human Review & Campaign Authorization Audit Trail")
        st.caption("Immutable session record of operator-approved actions to satisfy compliance audit requirements.")
        if st.session_state["approval_logs"]:
            audit_df = pd.DataFrame(st.session_state["approval_logs"])
            st.dataframe(audit_df, use_container_width=True)
            csv_audit = audit_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Approval Audit Log (CSV)", csv_audit, "customer_approvals_audit.csv", "text/csv")
        else:
            st.info("No customer actions have been approved in this session yet. Inspect a profile above and click 'Approve Next-Best-Action'.")


# =====================================================================
# UI 2: AI DATA ANALYST CHATBOT
# =====================================================================
def render_chatbot_ui(filtered_sales_df: pd.DataFrame):
    """Renders Amul AI Analyst Chatbot with deterministic tool calculations, lineage, and suggested pills."""
    st.markdown("### 💬 Amul AI Analyst (Conversational Decision-Support)")
    st.caption("Evidence-based, read-only analytics assistant. Computes answers directly from loaded dataframe with full data lineage.")

    # Initialize chatbot engine
    cust_df = get_or_load_customer_data()
    engine = AmulDataAnalystEngine(sales_df=filtered_sales_df, customer_df=cust_df)

    if "chatbot_history" not in st.session_state:
        st.session_state["chatbot_history"] = [
            {
                "role": "assistant",
                "content": "Hello! I am **Amul AI Analyst**, your read-only decision-support companion for dairy demand and cold-chain intelligence. Ask me any empirical question about current stockouts, regional demand, lost sales, or customer segments.",
                "data_lineage": None,
            }
        ]

    # Pre-built prompt suggestions
    st.markdown("<b>Suggested Analytical Questions:</b>", unsafe_allow_html=True)
    suggested_queries = [
        "Which regions have the highest stockout rates?",
        "Why are stockouts occurring in this dataset?",
        "Which products have the highest estimated lost sales?",
        "How did demand change during warmer months?",
        "Are delivery delays associated with stockouts?",
        "Which products may require replenishment?",
        "What are the main findings in the generated PDF?",
        "Which customer segments have the highest churn or declining engagement?",
    ]

    pill_cols = st.columns(4)
    selected_suggestion = None
    for idx, query in enumerate(suggested_queries[:4]):
        with pill_cols[idx]:
            if st.button(f"💡 {query}", key=f"sugg_{idx}", use_container_width=True):
                selected_suggestion = query

    pill_cols2 = st.columns(4)
    for idx, query in enumerate(suggested_queries[4:]):
        with pill_cols2[idx]:
            if st.button(f"💡 {query}", key=f"sugg_{idx+4}", use_container_width=True):
                selected_suggestion = query

    c_clear, _ = st.columns([2, 10])
    with c_clear:
        if st.button("🗑️ Clear Chat History"):
            st.session_state["chatbot_history"] = [
                {
                    "role": "assistant",
                    "content": "Chat history cleared. How may I assist your supply chain analysis today?",
                    "data_lineage": None,
                }
            ]
            st.rerun()

    st.markdown("---")

    # Render Conversation Stream
    for msg in st.session_state["chatbot_history"]:
        with st.chat_message(msg["role"], avatar="🥛" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if msg.get("data_lineage"):
                lineage = msg["data_lineage"]
                with st.expander("🔍 Verified Data Lineage & Calculation Method", expanded=False):
                    st.markdown(f"**Supporting Dataset Columns:** `{', '.join(lineage.get('columns_used', []))}`")
                    st.markdown(f"**Underlying Formulation:** {lineage.get('formula_or_method', 'N/A')}")
                    st.markdown(f"**Evaluated Records:** {lineage.get('records_analyzed', 0):,} rows")

    # Chat Input Box
    user_query = st.chat_input("Ask about stockouts, lost sales, replenishment, customer segments...")
    query_to_run = selected_suggestion if selected_suggestion else user_query

    if query_to_run:
        # Append User Message
        st.session_state["chatbot_history"].append({"role": "user", "content": query_to_run, "data_lineage": None})

        # Execute Engine
        with st.spinner("Analyzing active data partitions and computing verification metrics..."):
            response = engine.answer_question(query_to_run)

        # Format Assistant Response
        assistant_text = f"""
### 📋 Empirical Finding: {response.headline}

{response.finding}

---
**📊 Supporting Metric Figures:**
"""
        for k, v in response.supporting_figures.items():
            assistant_text += f"- **{k.replace('_', ' ').title()}:** {v}\n"

        assistant_text += f"""
---
**💡 Operational Interpretation:** {response.interpretation}

**🛡️ Recommended Action:** {response.recommended_action}
"""
        st.session_state["chatbot_history"].append({
            "role": "assistant",
            "content": assistant_text,
            "data_lineage": {
                "columns_used": response.columns_used,
                "formula_or_method": response.calculation_method,
                "records_analyzed": response.records_analyzed,
            },
        })
        st.rerun()


# =====================================================================
# UI 3: EMAIL CAMPAIGN CENTRE
# =====================================================================
def render_campaign_centre_ui():
    """Renders Email Campaign Centre with DPDPA consent filtering, template generator, test send, and mandatory approval."""
    st.markdown("### 📧 Email Campaign Centre & Consent-Gated Automation")
    st.caption("End-to-end customer campaign management with strict DPDPA 2023 consent validation, editable templates, and human approval gates.")

    cust_df = get_or_load_customer_data()

    tab_audience, tab_compose, tab_dispatch, tab_analytics = st.tabs([
        "1. Audience Targeting & Consent Gating",
        "2. Template Drafting & Preview",
        "3. Mandatory Operator Approval Gate",
        "4. Provider Telemetry & Analytics",
    ])

    if "campaign_draft" not in st.session_state:
        st.session_state["campaign_draft"] = {
            "campaign_type": "re_engagement",
            "target_segment": "declining_engagement",
            "target_region": "All Regions",
            "subject": "We Miss You at Amul — Enjoy Fresh Quality Delivered to Your Doorstep",
            "preview_text": "Special fresh milk & dairy re-engagement offer inside.",
            "body": "Dear {{first_name}},\n\nWe noticed you haven't ordered your favorite {{favorite_category}} recently. As a valued customer, we are committed to delivering farm-fresh quality right to your doorstep.\n\nExplore our latest deliveries and reconnect with Amul's trusted dairy range today.",
            "cta_text": "Rediscover Fresh Dairy",
            "cta_url": "https://amul.com/reconnect",
            "offer_details": "10% privilege discount on select fresh milk products.",
            "is_test_sent": False,
            "is_approved": False,
        }

    with tab_audience:
        st.markdown("#### 🎯 Audience Selection & Privacy Filtering")
        st.caption("Apply DPDPA 2023 consent filters and operational suppression lists before audience enrollment.")

        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            segment_choice = st.selectbox(
                "Target Customer Segment",
                ["declining_engagement", "loyal", "high-value", "new", "inactive", "All Segments"],
                index=0,
            )
        with f_c2:
            region_choice = st.selectbox(
                "Target Geographic Region",
                ["All Regions", "North", "West", "South", "East"],
                index=0,
            )
        with f_c3:
            category_choice = st.selectbox(
                "Product Interest Affinity",
                ["All Categories", "Fresh Milk", "Beverages", "Ice Cream", "Butter & Spreads", "Cheese", "Paneer"],
                index=0,
            )

        camp_type_choice = st.selectbox(
            "Campaign Communication Type",
            [
                "re_engagement",
                "product_announcement",
                "loyalty_update",
                "feedback_request",
                "service_update",
                "promotional_offer",
            ],
            index=0,
        )

        # Run Audience Gating Filter
        filtered_audience, exclusion_summary = filter_campaign_audience(
            cust_df,
            target_segment=segment_choice,
            target_region=region_choice,
            product_category_interest=category_choice,
            campaign_type=camp_type_choice,
        )

        st.session_state["filtered_audience"] = filtered_audience
        st.session_state["exclusion_summary"] = exclusion_summary

        # KPI Summary Cards
        st.markdown("##### 👥 Audience Eligibility Breakdown")
        a_c1, a_c2, a_c3, a_c4 = st.columns(4)
        a_c1.metric("Gross Evaluated Cohort", f"{exclusion_summary['gross_evaluated']} profiles")
        a_c2.metric("Eligible Recipients", f"{exclusion_summary['eligible_count']} approved", f"{(exclusion_summary['eligible_count'] / max(exclusion_summary['gross_evaluated'], 1))*100:.1f}% enrollment rate")
        a_c3.metric("Excluded Under Consent/Policy", f"{exclusion_summary['total_excluded']} blocked", delta=f"-{exclusion_summary['total_excluded']}", delta_color="inverse")
        a_c4.metric("Invalid Email Format", f"{exclusion_summary['invalid_email_format']} invalid")

        st.markdown("##### 🛡️ Reason Breakdown for Exclusions (Compliance Audit)")
        ex_cols = st.columns(4)
        ex_cols[0].info(f"🚫 **Opted Out (DPDPA):** {exclusion_summary.get('opted_out_count', 0)}")
        ex_cols[1].warning(f"🔒 **Transactional Only:** {exclusion_summary.get('transactional_only_count', 0)}")
        ex_cols[2].error(f"⚠️ **Open Support Complaint:** {exclusion_summary.get('open_complaint_suppressed', 0)}")
        ex_cols[3].info(f"🛑 **Global Suppression List:** {exclusion_summary.get('suppression_list_match', 0)}")

        if not filtered_audience.empty:
            with st.expander(f"Inspect Enrolled Audience List ({len(filtered_audience)} Recipients)", expanded=False):
                st.dataframe(
                    filtered_audience[["customer_id", "full_name", "email", "city", "region", "customer_segment", "consent_status"]],
                    use_container_width=True,
                )

    with tab_compose:
        st.markdown("#### ✍️ Editable Message Drafting & Brand Template Engine")
        st.caption("Standardized campaign templates aligned with Amul communication guidelines. Unsubscribe footer is automatically mandated.")

        if st.button("🔄 Regenerate Approved Brand Template Draft"):
            sample_cust = filtered_audience.iloc[0].to_dict() if not filtered_audience.empty else cust_df.iloc[0].to_dict()
            new_draft = generate_campaign_draft(
                campaign_type=camp_type_choice,
                segment_name=segment_choice,
                sample_customer=sample_cust,
                offer_details="10% privileged discount on select fresh dairy products.",
            )
            st.session_state["campaign_draft"]["subject"] = new_draft.subject
            st.session_state["campaign_draft"]["preview_text"] = new_draft.preview_text
            st.session_state["campaign_draft"]["body"] = new_draft.body_text
            st.session_state["campaign_draft"]["cta_text"] = new_draft.call_to_action_text
            st.session_state["campaign_draft"]["cta_url"] = new_draft.call_to_action_url
            st.session_state["campaign_draft"]["offer_details"] = new_draft.offer_details
            st.toast("Brand draft updated!", icon="✨")

        d_col1, d_col2 = st.columns([6, 6])
        with d_col1:
            st.session_state["campaign_draft"]["subject"] = st.text_input(
                "Subject Line",
                value=st.session_state["campaign_draft"]["subject"],
            )
            st.session_state["campaign_draft"]["preview_text"] = st.text_input(
                "Preview Header Text",
                value=st.session_state["campaign_draft"]["preview_text"],
            )
            st.session_state["campaign_draft"]["body"] = st.text_area(
                "Email Body (Markdown / Plain Text)",
                value=st.session_state["campaign_draft"]["body"],
                height=220,
            )
            st.session_state["campaign_draft"]["cta_text"] = st.text_input(
                "CTA Button Label",
                value=st.session_state["campaign_draft"]["cta_text"],
            )

        with d_col2:
            st.markdown("##### 📱 Live Email Client Preview")
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <div style="background-color: #0B2545; color: white; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF; letter-spacing: 0.05em;">Amul</span>
                        <span style="font-size: 0.72rem; color: #94A3B8;">Customer Communications Centre</span>
                    </div>
                    <div style="padding: 16px 20px;">
                        <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 4px;">Subject: <b>{st.session_state['campaign_draft']['subject']}</b></div>
                        <div style="font-size: 0.72rem; color: #94A3B8; margin-bottom: 14px;">Preview: {st.session_state['campaign_draft']['preview_text']}</div>
                        <div style="font-size: 0.88rem; color: #1E293B; line-height: 1.5; white-space: pre-line; margin-bottom: 18px;">
                            {st.session_state['campaign_draft']['body'].replace('{{first_name}}', 'Priya').replace('{{favorite_category}}', 'Fresh Milk')}
                        </div>
                        <div style="text-align: center; margin-bottom: 18px;">
                            <a href="{st.session_state['campaign_draft']['cta_url']}" style="background-color: #C4122F; color: white; padding: 8px 18px; border-radius: 4px; text-decoration: none; font-weight: 700; font-size: 0.85rem;">
                                {st.session_state['campaign_draft']['cta_text']}
                            </a>
                        </div>
                        <div style="border-top: 1px solid #E2E8F0; padding-top: 10px; font-size: 0.68rem; color: #94A3B8; text-align: center;">
                            You received this message because you have consented to product updates under DPDPA 2023.<br/>
                            Gujarat Co-operative Milk Marketing Federation (GCMMF), Anand, Gujarat, India.<br/>
                            <a href="#" style="color: #64748B; text-decoration: underline;">Manage Preferences</a> | <a href="#" style="color: #C4122F; text-decoration: underline;">Unsubscribe Instantly</a>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_dispatch:
        st.markdown("#### 🛡️ Step 3: Pre-Send Test & Mandatory Human Approval")
        st.caption("Bulk transmission is strictly gated behind an internal test send and authorized human confirmation.")

        st.markdown(
            f"""
            <div class="amul-panel" style="background-color: #F8FAFC;">
                <div style="font-weight: 700; color: #0B2545; font-size: 0.95rem; margin-bottom: 4px;">
                    Review Summary Before Approval
                </div>
                <div style="font-size: 0.82rem; color: #475569;">
                    • <b>Target Segment:</b> {segment_choice}<br/>
                    • <b>Eligible Audience:</b> {len(filtered_audience)} verified recipients<br/>
                    • <b>Excluded / Suppressed:</b> {exclusion_summary['total_excluded']} profiles<br/>
                    • <b>Scheduled Dispatch:</b> Immediate Batch Execution (Sandbox Mode)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        test_col1, test_col2 = st.columns([6, 6])
        with test_col1:
            st.markdown("##### A. Internal Test Send")
            test_addr = st.text_input("Internal Test Recipient", value="compliance-qa@amul-demo.internal")
            if st.button("Send Single Test Email"):
                with st.spinner("Connecting to mock email sandbox provider..."):
                    provider = MockSandboxEmailProvider(is_sandbox_mode=True)
                    sample_r = filtered_audience.iloc[0].to_dict() if not filtered_audience.empty else {"email": test_addr, "customer_id": "TEST-001", "full_name": "Test Operator"}
                    res = provider.send_single_email(
                        recipient_email=test_addr,
                        subject=f"[TEST] {st.session_state['campaign_draft']['subject']}",
                        body_html=st.session_state["campaign_draft"]["body"],
                        customer_id=sample_r.get("customer_id", "TEST-001"),
                        campaign_id="CAMP-TEST-001",
                    )
                    if res["success"]:
                        st.session_state["campaign_draft"]["is_test_sent"] = True
                        st.success(f"Test transmission delivered to {test_addr}! Message ID: `{res['message_id']}`")
                    else:
                        st.error(res.get("error", "Test transmission failed."))

        with test_col2:
            st.markdown("##### B. Mandatory Operator Authorization")
            is_confirmed = st.checkbox(
                "I explicitly confirm that this campaign has been reviewed against DPDPA 2023 consent policies, internal suppression lists have been audited, and I authorize bulk sandbox dispatch.",
                value=False,
            )
            authorized_by = st.text_input("Authorized Operator Identity / ID", value="OP-AMUL-9204")

            if not st.session_state["campaign_draft"]["is_test_sent"]:
                st.warning("⚠️ You must perform an internal test send before authorizing bulk dispatch.")
            elif not is_confirmed:
                st.info("ℹ️ Check the compliance confirmation box above to unlock bulk send execution.")
            else:
                if st.button("🚀 Approve & Execute Bulk Campaign Dispatch", type="primary", use_container_width=True):
                    with st.spinner(f"Dispatching to {len(filtered_audience)} eligible recipients via Sandbox Provider..."):
                        provider = MockSandboxEmailProvider(is_sandbox_mode=True)
                        recipients = filtered_audience.to_dict(orient="records")
                        camp_id = f"CAMP-{datetime.now().strftime('%Y%m%d%H%M')}"
                        telemetry = provider.send_batch_campaign(
                            campaign_id=camp_id,
                            template_id="AMUL-STD-V1",
                            recipients=recipients,
                            subject=st.session_state["campaign_draft"]["subject"],
                            body_html=st.session_state["campaign_draft"]["body"],
                            authorized_by=authorized_by,
                        )
                        st.session_state["last_campaign_telemetry"] = telemetry
                        st.session_state["campaign_draft"]["is_approved"] = True
                        st.success(f"Bulk campaign {camp_id} successfully executed! {telemetry['sent_count']} emails dispatched.")

    with tab_analytics:
        st.markdown("#### 📈 Provider Campaign Telemetry & Delivery Analytics")
        if "last_campaign_telemetry" in st.session_state:
            telem = st.session_state["last_campaign_telemetry"]
            st.markdown(f"**Active Campaign ID:** `{telem['campaign_id']}` | **Authorized By:** `{telem['authorized_by']}`")

            t_c1, t_c2, t_c3, t_c4, t_c5 = st.columns(5)
            t_c1.metric("Dispatched", f"{telem['sent_count']}")
            t_c2.metric("Delivered", f"{telem['delivered_count']}", f"{(telem['delivered_count']/max(telem['sent_count'],1))*100:.1f}%")
            t_c3.metric("Bounced", f"{telem['bounced_count']}", delta=f"-{telem['bounced_count']}", delta_color="inverse")
            t_c4.metric("Unsubscribed", f"{telem['unsubscribed_count']}", delta=f"-{telem['unsubscribed_count']}", delta_color="inverse")
            t_c5.metric("Clicks / Actions", f"{telem['clicked_count']}", f"CTR: {(telem['clicked_count']/max(telem['delivered_count'],1))*100:.1f}%")

            st.caption("Note: Per industry best practices, email opens are not treated as a deterministic engagement metric due to automated mail privacy protection (Apple MPP). Delivery and click rates use verified provider events.")
        else:
            st.info("No bulk campaigns have been executed in this session yet. Complete Step 3 to view telemetry.")


# =====================================================================
# UI 4: CUSTOMER NOTIFICATION CENTRE
# =====================================================================
def render_notification_centre_ui():
    """Renders Customer Notification Centre with In-App Cards, Quiet Hours Enforcement, and PWA Architecture."""
    st.markdown("### 🔔 Customer Notification Centre & Quiet Hours Guardrails")
    st.caption("Multi-channel notification management enforcing TRAI commercial communication quiet hours (9:00 PM – 9:00 AM IST) and frequency capping.")

    cust_df = get_or_load_customer_data()

    # Quiet Hours Banner
    quiet_active = is_quiet_hours()
    q_badge = (
        '<span style="background-color: #FEE2E2; color: #991B1B; font-weight: 700; padding: 4px 10px; border-radius: 4px;">🌙 QUIET HOURS ACTIVE (9:00 PM – 9:00 AM IST) — Promotional Push Suspended</span>'
        if quiet_active
        else '<span style="background-color: #DCFCE7; color: #166534; font-weight: 700; padding: 4px 10px; border-radius: 4px;">☀️ ACTIVE COMM HOURS (9:00 AM – 9:00 PM IST) — Delivery Permitted</span>'
    )
    st.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 6px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.85rem; font-weight: 700; color: #0B2545;">TRAI Commercial Communications Status:</span>
            {q_badge}
        </div>
        """,
        unsafe_allow_html=True,
    )

    notif_tab1, notif_tab2, notif_tab3 = st.tabs([
        "📱 In-App Notification Feed",
        "⚡ Enqueue Test Notification",
        "🌐 PWA & Web Push Architecture Guide",
    ])

    if "notifications_list" not in st.session_state:
        st.session_state["notifications_list"] = [
            {
                "id": "NOTIF-001",
                "customer_id": "AMUL-CUST-0001",
                "customer_name": "Aarav Sharma",
                "category": "RESTOCK_ALERT",
                "title": "Amul Taaza Fresh Milk Restocked in Indiranagar!",
                "message": "Your morning favorite is back in stock at your nearby Amul Preferred Outlet.",
                "timestamp": "10 minutes ago",
                "priority": "HIGH",
                "read": False,
            },
            {
                "id": "NOTIF-002",
                "customer_id": "AMUL-CUST-0002",
                "customer_name": "Diya Patel",
                "category": "LOYALTY_REMINDER",
                "title": "You have 1,450 Amul Loyalty Points!",
                "message": "Redeem your points for fresh paneer or butter cookies on your next order.",
                "timestamp": "2 hours ago",
                "priority": "MEDIUM",
                "read": False,
            },
            {
                "id": "NOTIF-003",
                "customer_id": "AMUL-CUST-0005",
                "customer_name": "Ishaan Verma",
                "category": "SERVICE_UPDATE",
                "title": "Cold-Chain Reefer Vehicle Dispatched",
                "message": "Your scheduled dairy subscription batch is in transit under certified 2°C chilled refrigeration.",
                "timestamp": "Yesterday",
                "priority": "MEDIUM",
                "read": True,
            },
        ]

    with notif_tab1:
        st.markdown("#### 📱 Active In-App Notification Feed (Consumer View Demo)")
        st.caption("Demonstrates interactive in-app notification cards rendered inside consumer mobile or web application sessions.")

        for idx, notif in enumerate(st.session_state["notifications_list"]):
            bg_card = "#FFFFFF" if not notif["read"] else "#F8FAFC"
            border_left = "#C4122F" if notif["priority"] == "HIGH" else "#0B2545"

            c_card, c_act = st.columns([10, 2])
            with c_card:
                st.markdown(
                    f"""
                    <div style="background-color: {bg_card}; border: 1px solid #CBD5E1; border-left: 5px solid {border_left}; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 700; color: #0B2545; font-size: 0.95rem;">{notif['title']}</span>
                            <span style="font-size: 0.72rem; color: #94A3B8;">{notif['timestamp']}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #334155; margin-bottom: 6px;">
                            {notif['message']}
                        </div>
                        <div style="font-size: 0.72rem; color: #64748B;">
                            Recipient: <b>{notif['customer_name']}</b> ({notif['customer_id']}) | Category: <code>{notif['category']}</code>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_act:
                if not notif["read"]:
                    if st.button("Mark Read", key=f"read_{notif['id']}"):
                        notif["read"] = True
                        st.rerun()
                else:
                    st.caption("✅ Read")

    with notif_tab2:
        st.markdown("#### ⚡ Enqueue Consumer Notification")
        st.caption("Test dispatching a notification through the priority queue and verifying quiet-hours compliance.")

        n_col1, n_col2 = st.columns([6, 6])
        with n_col1:
            target_c_opt = st.selectbox(
                "Target Recipient",
                [f"{row['customer_id']} — {row['full_name']}" for _, row in cust_df.iterrows()[:15]],
            )
            target_cid = target_c_opt.split(" — ")[0]
            target_cname = target_c_opt.split(" — ")[1]
            n_category = st.selectbox(
                "Notification Category",
                ["RESTOCK_ALERT", "PRODUCT_UPDATE", "SERVICE_UPDATE", "LOYALTY_REMINDER", "PROMOTIONAL_OFFER"],
            )
            n_priority = st.selectbox("Priority Level", ["HIGH", "MEDIUM", "LOW"], index=1)

        with n_col2:
            n_title = st.text_input("Notification Headline", value="Amul Cow Ghee Available at Special Price")
            n_body = st.text_area("Message Body", value="Stock up on authentic Amul pure ghee today with free doorstep delivery.", height=100)

            if st.button("Enqueue Notification", use_container_width=True):
                manager = NotificationDispatchManager()
                result = manager.dispatch_notification(
                    customer_id=target_cid,
                    channel="in_app",
                    category=n_category,
                    title=n_title,
                    body=n_body,
                    priority=n_priority,
                )
                if result["status"] == "DELIVERED":
                    st.session_state["notifications_list"].insert(0, {
                        "id": f"NOTIF-{len(st.session_state['notifications_list'])+1:03d}",
                        "customer_id": target_cid,
                        "customer_name": target_cname,
                        "category": n_category,
                        "title": n_title,
                        "message": n_body,
                        "timestamp": "Just now",
                        "priority": n_priority,
                        "read": False,
                    })
                    st.success(f"Notification queued and delivered in-app! Notification ID: `{result['notification_id']}`")
                elif result["status"] == "DEFERRED_QUIET_HOURS":
                    st.warning(f"Notification deferred! Reason: {result.get('reason')}. Scheduled for 9:00 AM IST.")
                else:
                    st.error(f"Dispatch failed: {result.get('reason')}")

    with notif_tab3:
        st.markdown("#### 🌐 Progressive Web App (PWA) & Web Push Architecture")
        st.caption("Technical implementation specifications for integrating Web Push API and Service Workers in consumer-facing applications.")

        st.markdown(
            """
            <div style="background-color: #FEF2F2; border-left: 4px solid #C4122F; padding: 10px 14px; border-radius: 4px; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #991B1B; font-size: 0.85rem;">
                    ⚠️ ARCHITECTURAL BOUNDARY: STREAMLIT VS. CONSUMER PUSH
                </div>
                <div style="color: #7F1D1D; font-size: 0.78rem;">
                    Streamlit is an internal administrative dashboard, not a consumer device app. Browser push notifications cannot and should not be faked using internal Streamlit toasts. True device push requires a Progressive Web App (PWA) or native Android/iOS application with service worker registration and VAPID key exchange as documented below.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(PWA_BROWSER_PUSH_ARCHITECTURE_GUIDE)


# =====================================================================
# UI 5: CRM & REST API SCHEMAS
# =====================================================================
def render_crm_integration_ui():
    """Renders documented CRM integration endpoints, JSON schemas, and production architecture."""
    st.markdown("### 🔌 CRM & REST API Integration Architecture")
    st.caption("Standardized JSON schemas and persistent database recommendations for production enterprise deployment.")

    st.markdown("#### 📑 Standardized CRM REST API Endpoints")
    for endpoint, details in CRM_API_SCHEMAS.items():
        with st.expander(f"📍 `{details['method']}` {endpoint} — {details['description']}", expanded=False):
            st.markdown(f"**Required Headers:** `{details.get('headers', {})}`")
            st.markdown(f"**Query / Path Parameters:** `{details.get('parameters', {})}`")
            st.markdown(f"**Expected Request Payload:**")
            st.code(json.dumps(details.get("request_body_schema", {}), indent=2), language="json")
            st.markdown(f"**Response Schema (HTTP 200):**")
            st.code(json.dumps(details.get("response_schema", {}), indent=2), language="json")

    st.markdown("#### 🏛️ Production Database Architecture (PostgreSQL + Redis)")
    st.caption("Architectural guidance for moving beyond in-memory session state into production-grade enterprise persistence.")
    st.markdown(PRODUCTION_DATABASE_ARCHITECTURE)

    st.markdown("#### 🔄 Diagram G: End-to-End Customer Campaign & Notification Workflow")
    st.caption("Visual representation of data validation, RFM segmentation, Next-Best-Action, human approval, and dispatch.")
    st.markdown(f"```mermaid\n{DIAGRAM_G_MERMAID}\n```")
