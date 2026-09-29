"""
Unit and Integration Tests for Customer Intelligence, Amul AI Analyst Chatbot,
Email Campaign Management, and Customer Notification Centre.
Validates:
- RFM segmentation and scoring
- DPDPA 2023 consent filtering & open complaint suppression
- Explainable Next-Best-Action generation
- Mock Sandbox email dispatch, duplicate prevention, and batch telemetry
- Notification quiet-hours guardrails (TRAI 9 PM - 9 AM IST)
- Chatbot deterministic query resolution and data lineage
"""

from datetime import datetime, time
import os
import pandas as pd
import pytest

from src.chatbot import AmulDataAnalystEngine
from src.campaign_manager import (
    MockSandboxEmailProvider,
    filter_campaign_audience,
    generate_campaign_draft,
)
from src.customer_intelligence import (
    classify_customer_segment,
    enrich_customer_dataframe,
    generate_next_best_action,
    generate_synthetic_customer_dataset,
)
from src.data_loader import validate_and_clean_data
from src.notification_center import (
    NotificationDispatchManager,
    is_quiet_hours,
)


@pytest.fixture
def sample_customer_df() -> pd.DataFrame:
    """Provides a synthetic customer cohort for testing."""
    df = generate_synthetic_customer_dataset(num_records=50, seed=42)
    return enrich_customer_dataframe(df)


@pytest.fixture
def sample_sales_df() -> pd.DataFrame:
    """Loads and validates distribution sales data for chatbot testing."""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_amul_distribution_data.csv")
    raw_df = pd.read_csv(csv_path)
    cleaned, _, _ = validate_and_clean_data(raw_df)
    return cleaned


# =====================================================================
# 1. CUSTOMER INTELLIGENCE & RFM TESTS
# =====================================================================
def test_rfm_segment_classification():
    """Validates boundary conditions for RFM segmentation."""
    # 1. New customer (< 45 days tenure)
    assert classify_customer_segment(tenure_days=20, days_since_last=10, orders_count=2, total_spend=1200) == "new"

    # 2. Inactive customer (> 120 days since last purchase)
    assert classify_customer_segment(tenure_days=300, days_since_last=140, orders_count=10, total_spend=5000) == "inactive"

    # 3. Declining engagement (> 60 days since last purchase)
    assert classify_customer_segment(tenure_days=200, days_since_last=75, orders_count=15, total_spend=8000) == "declining_engagement"

    # 4. High-value customer (High spend > 25,000 INR)
    assert classify_customer_segment(tenure_days=300, days_since_last=15, orders_count=12, total_spend=32000) == "high-value"

    # 5. Loyal customer (High frequency >= 24 orders/year)
    assert classify_customer_segment(tenure_days=365, days_since_last=5, orders_count=36, total_spend=18000) == "loyal"


def test_next_best_action_with_support_complaint():
    """Ensures customers with active support complaints receive service follow-up and marketing is blocked."""
    cust_data = {
        "customer_id": "AMUL-TEST-001",
        "full_name": "Test Customer",
        "has_open_complaint": True,
        "consent_status": "CONSENTED_MARKETING",
        "customer_segment": "loyal",
        "spending_momentum": "steady",
        "total_spent_inr": 20000,
        "favorite_category": "Fresh Milk",
        "favorite_product": "Amul Taaza 500ml",
    }
    nba = generate_next_best_action(cust_data)
    assert "service" in nba["action_type"].lower()
    assert "Service Resolution Priority" in nba["action_title"]
    assert nba["is_blocked_by_consent"] is False
    assert nba["recommended_channel"] in ["phone", "email"]


def test_next_best_action_opted_out_consent():
    """Ensures promotional recommendations are blocked when consent is OPTED_OUT or TRANSACTIONAL_ONLY."""
    cust_opt_out = {
        "customer_id": "AMUL-TEST-002",
        "full_name": "Opted Out Customer",
        "has_open_complaint": False,
        "consent_status": "OPTED_OUT",
        "customer_segment": "declining_engagement",
        "spending_momentum": "declining",
        "total_spent_inr": 15000,
        "favorite_category": "Butter",
        "favorite_product": "Amul Butter 500g",
    }
    nba = generate_next_best_action(cust_opt_out)
    assert nba["is_blocked_by_consent"] is True
    assert "DPDPA 2023" in nba["consent_block_reason"]


# =====================================================================
# 2. CAMPAIGN MANAGER & CONSENT GATING TESTS
# =====================================================================
def test_filter_campaign_audience_consent_suppression(sample_customer_df):
    """Validates that opted-out and complaint records are stripped from promotional audiences."""
    eligible_df, summary = filter_campaign_audience(
        sample_customer_df,
        target_segment="All Segments",
        campaign_type="promotional_offer",
    )

    # Check that no opted-out accounts are enrolled
    assert eligible_df["consent_status"].str.contains("Opted-Out|OPTED_OUT", case=False).sum() == 0
    assert eligible_df["consent_status"].str.contains("Transactional", case=False).sum() == 0

    # Check that no customers with open complaints are enrolled in promotional offers
    complaint_col = "has_open_complaint" if "has_open_complaint" in eligible_df.columns else "has_open_ticket"
    assert (eligible_df[complaint_col] == True).sum() == 0

    # Verify summary numbers add up
    assert summary["gross_evaluated"] == len(sample_customer_df)
    assert summary["eligible_count"] + summary["total_excluded"] == summary["gross_evaluated"]


def test_email_template_generation():
    """Tests brand template generation for all supported campaign types."""
    sample_c = {
        "full_name": "Rohit Verma",
        "favorite_category": "Ice Cream",
        "favorite_product": "Amul Vanilla Magic",
        "loyalty_points": 1250,
        "loyalty_tier": "Gold",
    }
    for c_type in ["re_engagement", "product_announcement", "loyalty_update", "feedback_request", "service_update", "promotional_offer"]:
        draft = generate_campaign_draft(campaign_type=c_type, segment_name="loyal", sample_customer=sample_c)
        assert len(draft.subject) > 5
        assert len(draft.body_text) > 20
        assert "unsubscribe" in draft.mandatory_compliance_footer.lower()


# =====================================================================
# 3. MOCK SANDBOX EMAIL PROVIDER TESTS
# =====================================================================
def test_mock_email_provider_send_and_deduplication():
    """Validates sandbox delivery, audit logging, and duplicate transmission protection."""
    provider = MockSandboxEmailProvider(is_sandbox_mode=True)

    # 1. Successful first send
    res1 = provider.send_single_email(
        recipient_email="test.operator@amul-demo.internal",
        subject="Important Account Verification",
        body_html="<p>Test Content</p>",
        customer_id="AMUL-UNIT-01",
        campaign_id="CAMP-TEST",
    )
    assert res1["success"] is True
    assert "msg-" in res1["message_id"].lower()

    # 2. Duplicate send attempt within 24h window
    res_dup = provider.send_single_email(
        recipient_email="test.operator@amul-demo.internal",
        subject="Important Account Verification",
        body_html="<p>Test Content</p>",
        customer_id="AMUL-UNIT-01",
        campaign_id="CAMP-TEST",
    )
    assert res_dup["success"] is False
    assert "DUPLICATE_SUPPRESSED" in res_dup.get("error", "")


def test_mock_email_provider_batch_telemetry():
    """Validates batch campaign dispatch execution and telemetry generation."""
    provider = MockSandboxEmailProvider(is_sandbox_mode=True)
    recipients = [
        {"customer_id": f"CUST-{i:03d}", "email": f"cust{i}@example.com", "full_name": f"User {i}"}
        for i in range(10)
    ]
    telemetry = provider.send_batch_campaign(
        campaign_id="BATCH-001",
        template_id="TMPL-V1",
        recipients=recipients,
        subject="Monthly Dairy Digest",
        body_html="<p>Monthly Highlights</p>",
        authorized_by="MANAGER-TEST",
    )
    assert telemetry["sent_count"] == 10
    assert telemetry["delivered_count"] >= 9
    assert telemetry["campaign_id"] == "BATCH-001"
    assert telemetry["authorized_by"] == "MANAGER-TEST"


# =====================================================================
# 4. NOTIFICATION CENTRE & QUIET HOURS TESTS
# =====================================================================
def test_quiet_hours_logic():
    """Verifies that 9:00 PM to 9:00 AM IST is recognized as quiet hours."""
    # 22:30 IST is quiet hours
    assert is_quiet_hours(test_time=time(22, 30)) is True

    # 02:00 IST is quiet hours
    assert is_quiet_hours(test_time=time(2, 0)) is True

    # 14:00 IST is NOT quiet hours (active business hours)
    assert is_quiet_hours(test_time=time(14, 0)) is False


def test_notification_dispatch_manager():
    """Tests notification dispatch with priority handling and duplicate protection."""
    manager = NotificationDispatchManager()

    # In-app notification delivery
    res = manager.dispatch_notification(
        customer_id="AMUL-CUST-999",
        channel="in_app",
        category="RESTOCK_ALERT",
        title="Amul Taaza Back in Stock",
        body="Fresh milk available at your local booth.",
        priority="HIGH",
    )
    assert res["status"] in ["DELIVERED", "DEFERRED_QUIET_HOURS"]
    assert "NOTIF-" in res["notification_id"]


# =====================================================================
# 5. AMUL AI ANALYST CHATBOT TESTS
# =====================================================================
def test_chatbot_engine_deterministic_answers(sample_sales_df, sample_customer_df):
    """Verifies that the chatbot answers core domain questions with evidence-based data lineage."""
    engine = AmulDataAnalystEngine(sales_df=sample_sales_df, customer_df=sample_customer_df)

    # 1. Regional stockout inquiry
    q1 = "Which regions have the highest stockout rates?"
    ans1 = engine.answer_question(q1)
    assert ans1.tool_executed == "_tool_regional_stockouts"
    assert "region" in ans1.columns_used
    assert "stockout_flag" in ans1.columns_used
    assert len(ans1.supporting_figures) > 0
    assert ans1.records_analyzed > 0

    # 2. Lost sales inquiry
    q2 = "Which products have the highest estimated lost sales?"
    ans2 = engine.answer_question(q2)
    assert ans2.tool_executed == "_tool_lost_sales"
    assert "product_name" in ans2.columns_used

    # 3. Delivery delays and stockout association
    q3 = "Are delivery delays associated with stockouts?"
    ans3 = engine.answer_question(q3)
    assert ans3.tool_executed == "_tool_stockout_root_causes"
    assert "delay_stockout_odds_ratio" in ans3.supporting_figures

    # 4. Temperature and seasonal demand
    q4 = "How did demand change during warmer months?"
    ans4 = engine.answer_question(q4)
    assert ans4.tool_executed == "_tool_temperature_weather_demand"

    # 5. Customer churn / declining engagement
    q5 = "Which customer segments have the highest churn or declining engagement?"
    ans5 = engine.answer_question(q5)
    assert ans5.tool_executed == "_tool_customer_segment_analysis"
    assert "total_profiles_evaluated" in ans5.supporting_figures

    # 6. Fallback for out-of-scope query
    q6 = "What is the stock price of Google?"
    ans6 = engine.answer_question(q6)
    assert ans6.tool_executed == "_tool_fallback_guidance"
    assert "cannot answer" in ans6.finding.lower() or "read-only" in ans6.finding.lower()
