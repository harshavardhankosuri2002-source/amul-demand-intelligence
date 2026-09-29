"""
AMUL CRM, Customer Data Model & API Schema Definitions.
Implements the 12 production entities:
1. Customer
2. Transaction
3. CustomerPreference
4. ConsentRecord
5. CustomerSegment
6. CampaignDefinition
7. CampaignRecipient
8. CampaignEvent
9. NotificationPreference
10. NotificationEvent
11. AIRecommendation
12. AuditLog

Provides documented API endpoint specifications, JSON schemas,
and production database architecture recommendations (PostgreSQL + RLS + Redis).
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd


@dataclass
class ConsentRecord:
    consent_id: str
    customer_id: str
    consent_type: str  # "promotional_email", "sms_alert", "push_notification", "analytics"
    status: str        # "OPTED_IN", "OPTED_OUT", "WITHDRAWN"
    notice_version: str
    opt_in_timestamp: str
    opt_out_timestamp: Optional[str]
    ip_address_masked: str
    collected_via: str # "PWA_Prompt", "Retail_Form", "Web_Portal"


@dataclass
class CustomerPreference:
    customer_id: str
    preferred_category: str
    preferred_channel: str
    preferred_language: str
    frequency_cap_per_week: int
    quiet_hours_enabled: bool
    email_digest_frequency: str


@dataclass
class AuditLog:
    log_id: str
    user_role: str       # "Analyst", "Campaign Reviewer", "Administrator"
    user_id: str
    action: str          # "CAMPAIGN_APPROVED", "CONSENT_UPDATED", "EXPORT_PDF", "DATA_REFRESH"
    resource_type: str
    resource_id: str
    timestamp: str
    details: str


CRM_API_SCHEMAS = {
    "/api/v1/crm/customers": {
        "method": "POST / GET",
        "description": "Ingests or retrieves customer account profiles with masked PII.",
        "request_schema": {
            "type": "object",
            "required": ["customer_id", "region", "channel", "consent_status"],
            "properties": {
                "customer_id": {"type": "string", "example": "CUST-1042"},
                "region": {"type": "string", "example": "West Zone (Gujarat / MH)"},
                "channel": {"type": "string", "example": "Amul Preferred Outlet (APO)"},
                "preferred_category": {"type": "string", "example": "Butter"},
                "preferred_language": {"type": "string", "enum": ["English", "Hindi", "Gujarati"]},
                "consent_status": {"type": "string", "enum": ["OPTED_IN", "OPTED_OUT", "TRANSACTIONAL_ONLY"]},
            },
        },
    },
    "/api/v1/crm/consent/update": {
        "method": "POST",
        "description": "Records DPDPA 2023 consent grants, updates, or immediate revocations.",
        "request_schema": {
            "type": "object",
            "required": ["customer_id", "consent_type", "action", "timestamp"],
            "properties": {
                "customer_id": {"type": "string"},
                "consent_type": {"type": "string", "enum": ["commercial_marketing", "push_alerts", "service_updates"]},
                "action": {"type": "string", "enum": ["GRANT", "WITHDRAW", "RENEW"]},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        },
    },
    "/api/v1/campaigns/approve-dispatch": {
        "method": "POST",
        "description": "Requires dual-operator cryptographic approval to dispatch approved campaign batch.",
        "request_schema": {
            "type": "object",
            "required": ["campaign_id", "reviewer_id", "reviewer_role", "approval_token"],
            "properties": {
                "campaign_id": {"type": "string", "example": "CMP-2026-09-001"},
                "reviewer_id": {"type": "string", "example": "OPERATOR-MGR-04"},
                "reviewer_role": {"type": "string", "enum": ["Campaign Reviewer", "Administrator"]},
                "test_send_verified": {"type": "boolean"},
            },
        },
    },
}

PRODUCTION_DB_ARCHITECTURE_NOTE = """
### 🗄️ Recommended Production Database Architecture

While this prototype utilizes in-memory DataFrames and Streamlit session state for rapid demonstration,
a production multi-echelon deployment at GCMMF scale requires:

1. **Relational Core (PostgreSQL 16+)**:
   - Stores `customers`, `consent_records`, `campaign_definitions`, and `audit_logs`.
   - **Row-Level Security (RLS)**: Enforces tenant isolation and masks PII (phone/email) from unauthorized analyst roles.
   - **Audit Table Partitioning**: Monthly range partitioning on `audit_logs` for immutable regulatory compliance.

2. **Time-Series Engine (TimescaleDB / ClickHouse)**:
   - Ingests high-frequency distribution transactions, cold-chain sensor readings, and distributor depletion streams.

3. **In-Memory Cache & Frequency Capping (Redis Cluster)**:
   - Enforces real-time rate limiting (e.g. max 1 promotional email per customer per 7 days).
   - Manages global suppression sets with O(1) membership lookups prior to campaign queue generation.
"""

PRODUCTION_DATABASE_ARCHITECTURE = PRODUCTION_DB_ARCHITECTURE_NOTE

