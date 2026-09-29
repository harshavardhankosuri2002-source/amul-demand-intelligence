"""
AMUL Customer-Wise Intelligence and Solutions Engine.
Features:
- Structured data model for customer profile, consent, and transactions
- RFM (Recency, Frequency, Monetary) segmentation & spending velocity shifts
- Explainable next-best-action recommendation generation
- Human review and approval workflow
- Strict privacy adherence (DPDPA 2023 consent enforcement, no sensitive inferences)
- Clearly labeled synthetic customer demonstration dataset
"""

from datetime import datetime, timedelta
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Standard Customer Segments
SEGMENT_LOYAL = "Loyal High-Value"
SEGMENT_FREQUENT = "Frequent Regular"
SEGMENT_NEW = "Recent New Buyer"
SEGMENT_DECLINING = "Declining Engagement"
SEGMENT_DORMANT = "Inactive / Dormant"

# Approved Action Categories
ACTION_RE_ENGAGEMENT = "Re-Engagement Incentive"
ACTION_LOYALTY_UPGRADE = "Loyalty Reward / Tier Upgrade"
ACTION_CATEGORY_CROSS_SELL = "Category Educational Cross-Sell"
ACTION_SERVICE_FOLLOWUP = "Service Follow-Up (Priority Complaint)"
ACTION_CONSENT_SUPPRESSED = "Consent Blocked (No Marketing Permitted)"


def generate_synthetic_customer_dataset(num_customers: int = 120, seed: int = 42, **kwargs) -> pd.DataFrame:
    """
    Generates a reproducible, clearly labeled synthetic customer dataset.
    Note: Does NOT contain real consumer identities, phone numbers, or emails.
    All data is synthetic and engineered for academic demonstration.
    """
    num_customers = kwargs.get("num_records", num_customers)
    np.random.seed(seed)
    categories = [
        "Fresh Milk",
        "Curd & Fermented",
        "Butter",
        "Cheese",
        "Ice Cream",
        "Ghee",
        "Beverages",
        "Ambient Dairy",
        "Chocolates",
    ]
    regions = [
        "West Zone (Gujarat / MH)",
        "North Zone (Delhi NCR / PB)",
        "South Zone (KA / TN)",
        "East Zone (WB / Bihar)",
    ]
    languages = ["English", "Hindi", "Gujarati"]
    channels = ["Amul Preferred Outlet (APO)", "Retail Kirana", "Modern Trade / Supermarket", "Quick Commerce Direct"]

    base_date = datetime(2026, 9, 28)
    customers = []

    for i in range(1, num_customers + 1):
        cid = f"CUST-{1000 + i}"
        region = np.random.choice(regions, p=[0.40, 0.30, 0.18, 0.12])
        channel = np.random.choice(channels, p=[0.45, 0.30, 0.15, 0.10])
        pref_cat = np.random.choice(categories)
        pref_lang = np.random.choice(languages, p=[0.50, 0.30, 0.20])

        # Behavior archetype
        archetype = np.random.choice(["loyal", "frequent", "new", "declining", "dormant"], p=[0.25, 0.30, 0.15, 0.18, 0.12])

        if archetype == "loyal":
            recency = int(np.random.uniform(1, 10))
            frequency = int(np.random.uniform(25, 60))
            aov = round(float(np.random.uniform(650, 1800)), 2)
            loyalty_tier = np.random.choice(["Gold", "Platinum"], p=[0.7, 0.3])
            points = int(frequency * aov * 0.05)
            velocity_change = round(float(np.random.uniform(0.05, 0.25)), 2)
            has_ticket = np.random.rand() < 0.04
        elif archetype == "frequent":
            recency = int(np.random.uniform(5, 20))
            frequency = int(np.random.uniform(12, 28))
            aov = round(float(np.random.uniform(350, 850)), 2)
            loyalty_tier = np.random.choice(["Silver", "Gold"], p=[0.8, 0.2])
            points = int(frequency * aov * 0.04)
            velocity_change = round(float(np.random.uniform(-0.05, 0.10)), 2)
            has_ticket = np.random.rand() < 0.06
        elif archetype == "new":
            recency = int(np.random.uniform(1, 14))
            frequency = int(np.random.uniform(1, 4))
            aov = round(float(np.random.uniform(250, 600)), 2)
            loyalty_tier = "Bronze"
            points = int(frequency * aov * 0.02)
            velocity_change = 0.0
            has_ticket = False
        elif archetype == "declining":
            recency = int(np.random.uniform(25, 65))
            frequency = int(np.random.uniform(8, 20))
            aov = round(float(np.random.uniform(400, 950)), 2)
            loyalty_tier = np.random.choice(["Silver", "Gold"], p=[0.6, 0.4])
            points = int(frequency * aov * 0.03)
            velocity_change = round(float(np.random.uniform(-0.45, -0.20)), 2)
            has_ticket = np.random.rand() < 0.18
        else:  # dormant
            recency = int(np.random.uniform(70, 180))
            frequency = int(np.random.uniform(3, 10))
            aov = round(float(np.random.uniform(300, 700)), 2)
            loyalty_tier = "Bronze"
            points = int(frequency * aov * 0.01)
            velocity_change = round(float(np.random.uniform(-0.90, -0.60)), 2)
            has_ticket = np.random.rand() < 0.10

        last_purchase_dt = base_date - timedelta(days=recency)
        monetary = round(frequency * aov, 2)

        # Consent and communication preference (DPDPA 2023 compliance)
        # 75% opted-in for commercial communications, 15% transactional only, 10% completely opted-out
        consent_roll = np.random.rand()
        if consent_roll < 0.75:
            consent_status = "Opted-In (Promotional & Service)"
            marketing_allowed = True
        elif consent_roll < 0.90:
            consent_status = "Transactional & Service Only"
            marketing_allowed = False
        else:
            consent_status = "Opted-Out (Complete Suppression)"
            marketing_allowed = False

        email_pref = np.random.choice(["Weekly Digest", "Instant Alerts", "Monthly Statement"])
        comm_channel = np.random.choice(["Email", "In-App Notification", "SMS"], p=[0.55, 0.30, 0.15])

        # Support issue details
        if has_ticket:
            ticket_issue = np.random.choice([
                "Delayed Delivery from Local Depot",
                "Damaged Butter Carton in Transit",
                "Billing / Coupon Credit Discrepancy",
                "Product Temperature Concern at Retail",
            ])
            ticket_status = "Open / Pending Investigation"
        else:
            ticket_issue = "None"
            ticket_status = "Closed / No Active Ticket"

        # Synthetic mock contact attributes (clearly marked sandbox)
        synthetic_email = f"sandbox.retailer.{cid.lower()}@demo-amul.internal"
        phone_masked = f"+91-98XXX-{np.random.randint(10000, 99999)}"

        customers.append({
            "customer_id": cid,
            "region": region,
            "channel": channel,
            "preferred_category": pref_cat,
            "preferred_language": pref_lang,
            "recency_days": recency,
            "frequency_orders": frequency,
            "average_order_value_inr": aov,
            "monetary_total_inr": monetary,
            "last_purchase_date": last_purchase_dt.strftime("%Y-%m-%d"),
            "spending_velocity_change_pct": round(velocity_change * 100, 1),
            "loyalty_tier": loyalty_tier,
            "loyalty_points": points,
            "consent_status": consent_status,
            "marketing_allowed": marketing_allowed,
            "communication_channel": comm_channel,
            "email_preference": email_pref,
            "contact_email": synthetic_email,
            "phone_masked": phone_masked,
            "has_open_ticket": has_ticket,
            "support_issue": ticket_issue,
            "support_ticket_status": ticket_status,
            "campaign_interactions_count": int(np.random.poisson(4)),
            "approval_status": "Pending Review",
            "approved_by": None,
            "approval_timestamp": None,
            "data_source_flag": "SYNTHETIC_CUSTOMER_DEMO",
        })

    df = pd.DataFrame(customers)
    df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])
    return df


def classify_customer_segment(row: Any = None, **kwargs) -> str:
    """
    Computes rule-based customer segment from Recency, Frequency, and Monetary attributes.
    Supports row as pd.Series/dict or keyword arguments.
    """
    if row is None:
        data = kwargs
    elif isinstance(row, (pd.Series, dict)):
        data = dict(row)
        data.update(kwargs)
    else:
        data = kwargs

    r = data.get("recency_days", data.get("days_since_last", 30))
    f = data.get("frequency_orders", data.get("orders_count", 10))
    m = data.get("monetary_total_inr", data.get("total_spend", data.get("total_spent_inr", 5000)))
    tenure = data.get("tenure_days", 100)
    vel = data.get("spending_velocity_change_pct", data.get("spending_momentum", 0.0))

    if "tenure_days" in kwargs or "days_since_last" in kwargs:
        if tenure < 45:
            return "new"
        elif r > 120:
            return "inactive"
        elif r > 60 or (r > 30 and (vel <= -20.0 or vel == "declining")):
            return "declining_engagement"
        elif m > 25000:
            return "high-value"
        elif f >= 24 or (r <= 25 and f >= 15):
            return "loyal"
        else:
            return "loyal"

    if r <= 25 and f >= 25 and m >= 15000:
        return SEGMENT_LOYAL
    elif r <= 35 and f >= 10:
        return SEGMENT_FREQUENT
    elif r <= 20 and f < 5:
        return SEGMENT_NEW
    elif r > 30 and (vel <= -20.0 or vel == "declining"):
        return SEGMENT_DECLINING
    elif r > 60:
        return SEGMENT_DORMANT
    else:
        return SEGMENT_FREQUENT


def generate_next_best_action(customer: Any) -> Dict[str, Any]:
    """
    Generates explainable personalized Next-Best-Action recommendation.
    Prioritizes customer support and legal consent above promotional offers.
    Supports pd.Series or dict inputs.
    """
    cust_dict = dict(customer) if isinstance(customer, (pd.Series, dict)) else {}

    cid = cust_dict.get("customer_id", "UNKNOWN")
    consent_ok = cust_dict.get("marketing_allowed", False)
    c_stat = str(cust_dict.get("consent_status", "")).upper()
    if "CONSENTED" in c_stat or "OPTED-IN" in c_stat:
        consent_ok = True
    elif "OPTED_OUT" in c_stat or "OPTED-OUT" in c_stat or "TRANSACTIONAL" in c_stat:
        consent_ok = False

    has_ticket = cust_dict.get("has_open_ticket", cust_dict.get("has_open_complaint", False))
    seg = cust_dict.get("segment", cust_dict.get("customer_segment", classify_customer_segment(cust_dict)))
    cat = cust_dict.get("preferred_category", cust_dict.get("favorite_category", "Fresh Milk"))
    fav_prod = cust_dict.get("favorite_product", "Amul Taaza 500ml")
    recency = cust_dict.get("recency_days", cust_dict.get("days_since_last_purchase", 15))
    vel_change = cust_dict.get("spending_velocity_change_pct", 0.0)
    loyalty_tier = cust_dict.get("loyalty_tier", "Standard")
    channel = str(cust_dict.get("communication_channel", "email")).lower()
    issue = cust_dict.get("support_issue", "Recent Delivery Concern")

    # RULE 1: Support Ticket Priority (Customer Service over Marketing)
    if has_ticket:
        title_str = f"Service Resolution Priority: Follow-Up on '{issue}'"
        return {
            "customer_id": cid,
            "action_type": ACTION_SERVICE_FOLLOWUP,
            "priority": "Critical",
            "recommended_channel": "email",
            "title": title_str,
            "action_title": title_str,
            "description": f"Customer has an active unresolved support complaint ('{issue}'). Marketing suppressed under service rule.",
            "reason": (
                f"Active unresolved support complaint ('{issue}'). Per DPDPA service guidelines, promotional "
                f"marketing must be suppressed until resolution."
            ),
            "rationale": f"Unresolved complaint '{issue}' supersedes promotional communications.",
            "suggested_message": (
                f"Dear Customer, our logistics support team is actively reviewing your recent inquiry "
                f"regarding {issue}. A customer resolution specialist will contact you shortly."
            ),
            "offer_details": "No promotional offer. Issue priority escalation.",
            "metrics_trigger": f"Open Support Ticket: True | Issue: {issue}",
            "supporting_metrics": f"Open Support Ticket: True | Issue: {issue}",
            "suggested_product": "N/A (Service Resolution)",
            "suggested_category": "Customer Support",
            "is_blocked_by_consent": False,
            "requires_approval": True,
        }

    # RULE 2: Consent Enforcement (DPDPA 2023 / TRAI Regulations)
    if not consent_ok:
        title_str = "Marketing Communications Prohibited"
        return {
            "customer_id": cid,
            "action_type": ACTION_CONSENT_SUPPRESSED,
            "priority": "Suppressed",
            "recommended_channel": "None (Suppressed)",
            "title": title_str,
            "action_title": title_str,
            "description": "Commercial promotional communications are blocked by consent policy.",
            "reason": (
                f"Customer consent status is '{cust_dict.get('consent_status')}'. "
                f"Commercial promotional messages are strictly blocked in compliance with "
                f"the Digital Personal Data Protection Act, 2023."
            ),
            "rationale": "DPDPA 2023 Consent restriction. Commercial messages prohibited.",
            "consent_block_reason": f"Blocked by DPDPA 2023 Privacy Policy ({cust_dict.get('consent_status')})",
            "suggested_message": "N/A — Message delivery suppressed by consent policy.",
            "offer_details": "None (Consent blocked).",
            "metrics_trigger": f"Consent Status: {cust_dict.get('consent_status')} | Marketing Allowed: False",
            "supporting_metrics": f"Consent Status: {cust_dict.get('consent_status')} | Marketing Allowed: False",
            "suggested_product": "N/A",
            "suggested_category": "N/A",
            "is_blocked_by_consent": True,
            "requires_approval": False,
        }

    # RULE 3: Declining Engagement / At-Risk Churn
    if seg in [SEGMENT_DECLINING, "declining_engagement"] or vel_change <= -25.0:
        title_str = f"Win-Back Re-Engagement: {cat} Replenishment"
        return {
            "customer_id": cid,
            "action_type": ACTION_RE_ENGAGEMENT,
            "priority": "High",
            "recommended_channel": channel,
            "title": title_str,
            "action_title": title_str,
            "description": f"Purchase velocity declined by {abs(vel_change):.1f}% over the last 60 days.",
            "reason": (
                f"Purchase velocity has declined by {abs(vel_change):.1f}% over the last 60 days, "
                f"with {recency} days elapsed since the last order. Re-engagement incentive recommended."
            ),
            "rationale": f"Declining purchasing velocity ({vel_change:.1f}%) requires retention offer.",
            "suggested_message": (
                f"We noticed you haven't stocked up on your favorite {cat} products recently! "
                f"Enjoy free priority cold-chain delivery on your next distribution order."
            ),
            "offer_details": "Free cold-chain delivery waiver on next order over ₹500.",
            "metrics_trigger": f"Velocity Change: {vel_change:.1f}% | Recency: {recency}d | Category: {cat}",
            "supporting_metrics": f"Velocity Change: {vel_change:.1f}% | Recency: {recency}d | Category: {cat}",
            "suggested_product": fav_prod,
            "suggested_category": cat,
            "is_blocked_by_consent": False,
            "requires_approval": True,
        }

    # RULE 4: Loyal High-Value Customer (Appreciation & Tier Recognition)
    if seg in [SEGMENT_LOYAL, "loyal", "high-value"]:
        title_str = f"VIP Loyalty Recognition ({loyalty_tier} Partner)"
        return {
            "customer_id": cid,
            "action_type": ACTION_LOYALTY_UPGRADE,
            "priority": "Medium",
            "recommended_channel": channel,
            "title": title_str,
            "action_title": title_str,
            "description": f"Top-quartile customer with {cust_dict.get('frequency_orders', 20)} lifetime orders.",
            "reason": (
                f"Consistent top-quartile customer with {cust_dict.get('frequency_orders', 20)} lifetime orders "
                f"and total spend of ₹{cust_dict.get('monetary_total_inr', cust_dict.get('total_spent_inr', 15000)):,.0f}."
            ),
            "rationale": "High lifetime value and purchase frequency warrants VIP allocation.",
            "suggested_message": (
                f"Thank you for being a valued Amul {loyalty_tier} partner! You have earned "
                f"{cust_dict.get('loyalty_points', 1200):,} loyalty points. Enjoy early access to our seasonal ghee & butter releases."
            ),
            "offer_details": "Early reservation access for festive bulk bookings + 500 bonus reward points.",
            "metrics_trigger": f"Orders: {cust_dict.get('frequency_orders', 20)} | Tier: {loyalty_tier}",
            "supporting_metrics": f"Orders: {cust_dict.get('frequency_orders', 20)} | Tier: {loyalty_tier}",
            "suggested_product": fav_prod,
            "suggested_category": cat,
            "is_blocked_by_consent": False,
            "requires_approval": True,
        }

    # RULE 5: Category Cross-Sell / Educational Product Announcement
    title_str = f"Relevant Category Information: Complementary to {cat}"
    return {
        "customer_id": cid,
        "action_type": ACTION_CATEGORY_CROSS_SELL,
        "priority": "Low",
        "recommended_channel": channel,
        "title": title_str,
        "action_title": title_str,
        "description": f"Customer orders regularly within {cat}. Highlight complementary product variants.",
        "reason": f"Customer orders regularly within {cat}. Suggest new product variants matching their cold-chain profile.",
        "rationale": f"High category affinity for {cat}.",
        "suggested_message": f"Explore our latest dairy innovations in {cat}! Discover certified organic variants.",
        "offer_details": "Informational catalog highlight + sample pack on qualifying replenishment.",
        "metrics_trigger": f"Category: {cat} | AOV: ₹{cust_dict.get('average_order_value_inr', 500):,.0f}",
        "supporting_metrics": f"Category: {cat} | AOV: ₹{cust_dict.get('average_order_value_inr', 500):,.0f}",
        "suggested_product": fav_prod,
        "suggested_category": cat,
        "is_blocked_by_consent": False,
        "requires_approval": True,
    }


def enrich_customer_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes RFM segment, Next-Best-Action, and supporting decision metrics.
    """
    enriched = df.copy()
    if "segment" not in enriched.columns:
        enriched["segment"] = enriched.apply(classify_customer_segment, axis=1)

    actions = []
    action_types = []
    priorities = []
    reasons = []

    for _, row in enriched.iterrows():
        nba = generate_next_best_action(row)
        actions.append(nba["suggested_message"])
        action_types.append(nba["action_type"])
        priorities.append(nba["priority"])
        reasons.append(nba["reason"])

    enriched["next_best_action"] = actions
    enriched["action_type"] = action_types
    enriched["action_priority"] = priorities
    enriched["recommendation_reason"] = reasons

    return enriched
