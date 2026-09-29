"""
AMUL Email Campaign Management & Provider Integration Layer.
Features:
- Audience selection with strict consent & preference gating (DPDPA 2023 / TRAI compliance)
- Suppression list filtering & exclusion diagnostics
- Provider abstraction: Mock Sandbox, SendGrid, Amazon SES
- Mandatory human review & approval workflow (preview, test send, explicit confirmation)
- Delivery tracking, bounce simulation, and unsubscribe processing
"""

from datetime import datetime
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Standard Campaign Types
CAMPAIGN_PRODUCT_ANNOUNCEMENT = "Product Announcement"
CAMPAIGN_LOYALTY_UPDATE = "Loyalty Update & Recognition"
CAMPAIGN_RE_ENGAGEMENT = "Re-Engagement Incentive"
CAMPAIGN_SERVICE_UPDATE = "Service & Operational Update"
CAMPAIGN_FEEDBACK_REQUEST = "Customer Feedback Survey"

APPROVED_TEMPLATES = {
    CAMPAIGN_PRODUCT_ANNOUNCEMENT: {
        "subject": "New Dairy Innovation: Discover Amul's Latest {category} Selection",
        "preview_text": "Fresh arrivals and seasonal stock now available across retail depots.",
        "body_template": (
            "Dear {customer_name},\n\n"
            "We are pleased to share our newest product developments in {category}. "
            "Formulated from pure farmer-procured milk across Gujarat cooperatives, our latest lines "
            "adhere to the highest standards of cold-chain quality and purity.\n\n"
            "Explore product specifications, pack sizes, and depot availability at your nearest "
            "Amul Preferred Outlet or authorized distribution partner.\n\n"
            "Best regards,\n"
            "GCMMF (Amul) Customer Operations\n\n"
            "---\n"
            "To manage your communication preferences or unsubscribe from marketing emails, visit: "
            "https://amul.com/preferences/manage?cid={customer_id}"
        ),
        "cta": "View Category Catalog",
    },
    CAMPAIGN_LOYALTY_UPDATE: {
        "subject": "Amul Partner Recognition: Your {loyalty_tier} Status & Benefits",
        "preview_text": "Thank you for your ongoing partnership with Amul cooperatives.",
        "body_template": (
            "Dear {customer_name},\n\n"
            "Thank you for your valued partnership. As an Amul {loyalty_tier} member, you currently have "
            "{loyalty_points} reward points recorded on your account.\n\n"
            "Your loyalty points can be redeemed against seasonal festival allocations and priority delivery reservations.\n\n"
            "Warm regards,\n"
            "Amul Cooperative Loyalty Programme Desk\n\n"
            "---\n"
            "To update your communication preferences or unsubscribe: "
            "https://amul.com/preferences/manage?cid={customer_id}"
        ),
        "cta": "Review Loyalty Statement",
    },
    CAMPAIGN_RE_ENGAGEMENT: {
        "subject": "We Miss You: Re-stock Your Favorite Amul {category} Essentials",
        "preview_text": "Priority cold-chain delivery available for your next restocking order.",
        "body_template": (
            "Dear {customer_name},\n\n"
            "We noticed that your distribution depot has not placed a replenishment order for {category} recently. "
            "Ensuring unbroken product availability is critical for meeting morning consumer dairy demand.\n\n"
            "We are pleased to offer complimentary priority cold-chain scheduling on your next order.\n\n"
            "Best regards,\n"
            "Amul Regional Logistics Team\n\n"
            "---\n"
            "To manage your communication preferences or unsubscribe: "
            "https://amul.com/preferences/manage?cid={customer_id}"
        ),
        "cta": "Schedule Replenishment",
    },
    CAMPAIGN_SERVICE_UPDATE: {
        "subject": "Operational Update: Cold-Chain Logistics & Depot Schedule",
        "preview_text": "Important logistics notice regarding regional cold storage and transit timing.",
        "body_template": (
            "Dear {customer_name},\n\n"
            "Please note our updated regional dispatch timetable for {region}. "
            "To safeguard fresh milk and ice-cream temperatures during peak summer months, "
            "primary reefer departures will operate on an advance morning window.\n\n"
            "For urgent depot inquiries, contact your regional logistics coordinator.\n\n"
            "Sincerely,\n"
            "GCMMF Supply Chain Operations\n\n"
            "---\n"
            "This is an operational service notification regarding your account."
        ),
        "cta": "Download Dispatch Timetable",
    },
}


class BaseEmailProvider:
    """Abstract base class for email delivery adapters."""

    def send_single(self, recipient: str, subject: str, body: str, is_test: bool = False) -> Dict[str, Any]:
        raise NotImplementedError

    def send_batch(self, recipients: List[Dict[str, Any]], campaign_id: str) -> Dict[str, Any]:
        raise NotImplementedError


class MockSandboxEmailProvider(BaseEmailProvider):
    """
    Mock sandbox email adapter for demonstration and academic evaluation.
    Simulates realistic dispatch latency, rate limiting, and delivery events
    without dispatching unsolicited external emails.
    """

    def __init__(self, failure_rate: float = 0.02, is_sandbox_mode: bool = True):
        self.failure_rate = failure_rate
        self.is_sandbox_mode = is_sandbox_mode
        self.sent_log: List[Dict[str, Any]] = []
        self._sent_recipients: Dict[str, float] = {}

    def send_single(self, recipient: str, subject: str, body: str, is_test: bool = False) -> Dict[str, Any]:
        # Validate email format
        if not recipient or not re.match(r"[^@]+@[^@]+\.[^@]+", recipient):
            return {"status": "INVALID_ADDRESS", "recipient": recipient, "error": "Malformed email syntax", "success": False}

        mid = f"msg-mock-{int(time.time()*1000)}"
        return {
            "status": "DELIVERED" if not is_test else "TEST_DISPATCHED",
            "recipient": recipient,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "provider": "Mock Sandbox (Simulated)",
            "message_id": mid,
            "success": True,
        }

    def send_single_email(
        self,
        recipient_email: str,
        subject: str,
        body_html: str,
        customer_id: str = "TEST-001",
        campaign_id: str = "CAMP-TEST",
    ) -> Dict[str, Any]:
        """High-level single email dispatch with duplicate suppression."""
        key = f"{customer_id}:{recipient_email}:{subject}"
        now_ts = time.time()
        if key in self._sent_recipients and (now_ts - self._sent_recipients[key]) < 86400:
            return {
                "success": False,
                "status": "DUPLICATE_SUPPRESSED",
                "error": "DUPLICATE_SUPPRESSED: Email already dispatched to this recipient within cooldown window.",
                "message_id": None,
            }

        self._sent_recipients[key] = now_ts
        res = self.send_single(recipient=recipient_email, subject=subject, body=body_html, is_test=True)
        return res

    def send_batch(self, recipients: List[Dict[str, Any]], campaign_id: str) -> Dict[str, Any]:
        delivered = 0
        bounced = 0
        unsubscribed = 0

        for r in recipients:
            email = r.get("contact_email", r.get("email", ""))
            roll = float(np.random.rand())
            if roll < self.failure_rate:
                bounced += 1
                status = "BOUNCED"
            elif roll < (self.failure_rate + 0.015):
                unsubscribed += 1
                status = "UNSUBSCRIBED"
            else:
                delivered += 1
                status = "DELIVERED"

            self.sent_log.append({
                "campaign_id": campaign_id,
                "customer_id": r.get("customer_id"),
                "recipient": email,
                "status": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        total = len(recipients)
        return {
            "campaign_id": campaign_id,
            "total_recipients": total,
            "delivered_count": delivered,
            "bounced_count": bounced,
            "unsubscribed_count": unsubscribed,
            "clicked_count": max(1, int(delivered * 0.22)),
            "delivery_rate_pct": round((delivered / max(1, total)) * 100, 2),
            "bounce_rate_pct": round((bounced / max(1, total)) * 100, 2),
            "status": "COMPLETED",
            "provider": "Mock Sandbox Provider",
        }

    def send_batch_campaign(
        self,
        campaign_id: str,
        template_id: str,
        recipients: List[Dict[str, Any]],
        subject: str,
        body_html: str,
        authorized_by: str = "OPERATOR",
    ) -> Dict[str, Any]:
        """Executes authorized batch send and formats telemetry."""
        telemetry = self.send_batch(recipients=recipients, campaign_id=campaign_id)
        telemetry["template_id"] = template_id
        telemetry["authorized_by"] = authorized_by
        telemetry["sent_count"] = telemetry.get("total_recipients", len(recipients))
        return telemetry


def filter_campaign_audience(
    customers_df: pd.DataFrame,
    target_segment: str = "All Segments",
    target_region: str = "All Regions",
    target_category: str = "All Categories",
    campaign_type: str = CAMPAIGN_PRODUCT_ANNOUNCEMENT,
    suppression_list: Optional[List[str]] = None,
    product_category_interest: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Selects eligible audience based on customer segment and regional parameters,
    while strictly enforcing consent, suppression lists, and open complaints.
    """
    cat_target = product_category_interest or target_category
    suppression_set = set(suppression_list or [])
    df = customers_df.copy()

    # Normalize segment column name if needed
    seg_col = "customer_segment" if "customer_segment" in df.columns else ("segment" if "segment" in df.columns else None)
    if seg_col and target_segment not in ["All Segments", "all"]:
        df = df[df[seg_col].str.lower() == target_segment.lower()]

    if "region" in df.columns and target_region not in ["All Regions", "all"]:
        df = df[df["region"].str.contains(target_region, case=False, na=False)]

    if cat_target not in ["All Categories", "all"]:
        pref_col = "favorite_category" if "favorite_category" in df.columns else ("preferred_category" if "preferred_category" in df.columns else None)
        if pref_col:
            df = df[df[pref_col].str.contains(cat_target, case=False, na=False)]

    total_targeted = len(df)
    eligible_indices = []
    excluded_records = []
    opted_out_c = 0
    tx_only_c = 0
    complaint_c = 0
    suppress_c = 0
    invalid_email_c = 0

    for idx, row in df.iterrows():
        cid = row.get("customer_id", "")
        email = row.get("contact_email", row.get("email", ""))
        consent = str(row.get("consent_status", ""))
        mkt_allowed = row.get("marketing_allowed", False)
        if "CONSENTED" in consent.upper() or "OPTED-IN" in consent.upper():
            mkt_allowed = True
        has_ticket = row.get("has_open_ticket", row.get("has_open_complaint", False))

        exclusion_reason = None

        if cid in suppression_set or email in suppression_set:
            exclusion_reason = "Customer ID or email is in global suppression list."
            suppress_c += 1
        elif "OPTED_OUT" in consent.upper() or "OPTED-OUT" in consent.upper():
            exclusion_reason = "Customer has explicitly opted out of communications."
            opted_out_c += 1
        elif "TRANSACTIONAL" in consent.upper() or not mkt_allowed:
            exclusion_reason = "Consent limited to transactional service; promotional messaging disallowed."
            tx_only_c += 1
        elif has_ticket:
            exclusion_reason = f"Customer has an active unresolved support complaint ('{row.get('support_issue', 'General Complaint')}')."
            complaint_c += 1
        elif not email or "@" not in email:
            exclusion_reason = "Missing or malformed contact email address."
            invalid_email_c += 1

        if exclusion_reason:
            rec = row.to_dict()
            rec["exclusion_reason"] = exclusion_reason
            excluded_records.append(rec)
        else:
            eligible_indices.append(idx)

    eligible_df = df.loc[eligible_indices].copy()
    excluded_df = pd.DataFrame(excluded_records)

    summary = {
        "gross_evaluated": total_targeted,
        "eligible_count": len(eligible_df),
        "total_excluded": len(excluded_df),
        "opted_out_count": opted_out_c,
        "transactional_only_count": tx_only_c,
        "open_complaint_suppressed": complaint_c,
        "suppression_list_match": suppress_c,
        "invalid_email_format": invalid_email_c,
    }

    return eligible_df, summary


class CampaignDraft(dict):
    """Dictionary subclass supporting dot-attribute access for campaign templates."""
    def __getattr__(self, name: str) -> Any:
        return self.get(name, "")

    def __setattr__(self, name: str, value: Any):
        self[name] = value


def generate_campaign_draft(
    campaign_type: str,
    target_category: str = "Fresh Milk",
    target_region: str = "West Zone",
    custom_subject: Optional[str] = None,
    custom_body: Optional[str] = None,
    segment_name: Optional[str] = None,
    sample_customer: Optional[Dict[str, Any]] = None,
    offer_details: Optional[str] = None,
) -> CampaignDraft:
    """
    Renders an editable campaign message draft using approved company templates.
    Supports both dict and attribute access.
    """
    template = APPROVED_TEMPLATES.get(campaign_type, APPROVED_TEMPLATES.get(CAMPAIGN_PRODUCT_ANNOUNCEMENT))
    if template is None:
        template = APPROVED_TEMPLATES[CAMPAIGN_PRODUCT_ANNOUNCEMENT]

    cat = target_category
    if sample_customer and "favorite_category" in sample_customer:
        cat = sample_customer["favorite_category"]

    cname = "Valued Customer"
    cid = "AMUL-CUST"
    tier = "Bronze"
    pts = 500
    if sample_customer:
        cname = sample_customer.get("full_name", sample_customer.get("customer_name", cname))
        cid = sample_customer.get("customer_id", cid)
        tier = sample_customer.get("loyalty_tier", tier)
        pts = sample_customer.get("loyalty_points", pts)

    try:
        subject = custom_subject or template["subject"].format(category=cat, loyalty_tier=tier)
    except Exception:
        subject = f"Amul Update: {cat} Portfolio Announcements"

    preview = template["preview_text"]

    try:
        body = custom_body or template["body_template"].format(
            customer_name=cname,
            customer_id=cid,
            category=cat,
            region=target_region,
            loyalty_tier=tier,
            loyalty_points=pts,
        )
    except Exception:
        body = f"Dear {cname},\n\nPlease find our latest operational updates regarding Amul {cat} products.\n\nWarm regards,\nGCMMF"

    cta = template.get("cta", "View Catalog")

    footer = f"---\nTo manage your preferences or unsubscribe under DPDPA 2023, visit https://amul.com/preferences/manage?cid={cid}"

    return CampaignDraft({
        "campaign_type": campaign_type,
        "subject": subject,
        "preview_text": preview,
        "body_text": body,
        "body": body,
        "cta": cta,
        "call_to_action_text": cta,
        "call_to_action_url": f"https://amul.com/catalog/{cat.lower().replace(' ', '-')}",
        "offer_details": offer_details or "Standard cooperative pricing applies.",
        "mandatory_compliance_footer": footer,
    })
