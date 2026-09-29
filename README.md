# AMUL | AI Demand & Distribution Intelligence System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-34%20Passing-brightgreen.svg)]()
[![ReportLab](https://img.shields.io/badge/ReportLab-Platypus%20PDF-orange.svg)]()
[![DPDPA 2023](https://img.shields.io/badge/Compliance-DPDPA%202023%20%7C%20TRAI-navy.svg)]()
[![License](https://img.shields.io/badge/License-Academic%20%2F%20Decision--Support-lightgrey.svg)]()

> **⚠️ ACADEMIC EVALUATION & SYNTHETIC DATA NOTICE:**  
> This platform is an academic decision-support prototype engineered for MBA capstone and faculty evaluation. All operational distribution records and individual customer profiles are **statistically realistic, explicitly labeled synthetic demonstration data**. This project does NOT represent an official GCMMF (Amul) production deployment or claim proof of real-world operational defect. All Amul trademarks and portfolio names are cited strictly for realistic educational demonstration. Real consumer contact details must never be scraped, fabricated, or targeted without authorized CRM integration and explicit DPDPA 2023 consent.

---

## 📌 Executive Overview & Core Problem

**Amul (Gujarat Cooperative Milk Marketing Federation - GCMMF)** is India's largest dairy cooperative federation, managing millions of liters of milk daily across a three-tier cooperative architecture:
1. **Village Dairy Cooperative Societies (VDCS)**: Primary farmer procurement
2. **District Milk Unions**: Chilling, processing, and packaging
3. **Apex Marketing Federation (GCMMF)**: State & national distribution, cold-chain logistics, and retail execution

### Multi-Temperature Dairy Supply Chain Complexity:
Unlike ambient FMCG manufacturers, Amul operates across **four distinct thermodynamic regimes**:
- **Fresh Dairy (2°C to 4°C)**: Ultra-short shelf life (48h for pouch milk, 10-14d for Dahi/Paneer). Overstocking causes immediate souring and returns; understocking creates morning retail stockouts.
- **Chilled Dairy (0°C to 4°C)**: Butter, cheese blocks, and cheese slices (180–240 day shelf life).
- **Deep Frozen (-18°C)**: Real ice creams, green peas, and snacks requiring uninterrupted sub-zero cold-chain transit.
- **Ambient Products**: Pure Cow Ghee, Kool flavoured milk, and sweetened condensed milk. Subject to massive festive demand spikes (e.g. Navratri/Diwali ghee consumption increases of 50-80%).

This platform integrates **machine learning demand forecasting**, **temperature-differentiated inventory optimization**, **customer-wise RFM intelligence**, an **evidence-based AI Data Analyst Chatbot**, **DPDPA-compliant email campaign automation**, and **multi-channel customer notifications**.

---

## 🚀 Key Modules Overview

### 1. Supply Chain & Inventory Intelligence (Modules 1–7)
- **Executive Overview**: Total velocity, run rate, valuation at factory transfer cost vs MRP, and inventory turnover.
- **Demand Forecasting**: Chronological time-series splitting (zero lookahead leakage), Gradient Boosting, Random Forest, and Ridge regression benchmarked against a 7-day Seasonal Naive baseline on strictly held-out test data. Includes 80% prediction intervals.
- **Inventory & Replenishment**: Storage-specific safety stock and reorder points (Fresh vs Chilled vs Frozen vs Ambient), configurable service levels (90% to 99%), and downloadable purchase orders.
- **Regional Distribution**: Geographic distribution volume, channel splits (APOs, Kirana, Modern Trade, Quick Commerce), and cross-regional SKU velocity heatmaps.
- **Wastage & Expiry Risk**: Cold-chain spoilage tracking and near-expiry lot watchlists (distinguishing recorded write-offs from forecast exposure).
- **Promotion Analysis**: Promotional uplift boxplots and category volume distributions with correlation vs causation disclaimers.
- **AI Recommendations**: Explainable prescriptive queue with severity badges, triggering metrics, affected locations, operational rationale, and concrete corrective directives.

### 2. Module 8: Customer-Wise Intelligence & Solutions
- **Synthetic Customer Cohort**: 120 synthetic customer records with complete RFM attributes, consent statuses, and interaction histories.
- **RFM Segmentation Engine**: Rule-based categorization into `loyal`, `high-value`, `new`, `declining_engagement`, and `inactive` segments.
- **Explainable Next-Best-Action**: Suggests personalized retention or product actions grounded in purchasing history and spending velocity.
- **Service Ticket & Consent Priority**: Customers with open support complaints automatically receive service resolution actions while promotional marketing is strictly suppressed. Opted-out accounts are blocked under DPDPA 2023.
- **Human-in-the-Loop Review Gate**: Authorized staff (Area Sales Manager, CRM Specialist, Compliance Officer) review and approve recommended actions before queuing, with a full session audit log.

### 3. Module 9: Amul AI Analyst (Chatbot)
- **Read-Only Deterministic Execution**: Conversational interface executing against audited, read-only Python calculation tools over currently loaded data.
- **Zero Hallucination Guarantee**: Directly computes regional stockout rates, lost sales figures, temperature elasticity correlations, replenishment priorities, and customer segment metrics.
- **Full Data Lineage**: Each response provides the finding, supporting figures, relevant dates, operational interpretation, recommended action, and explicit dataset columns used.
- **Clear Boundaries**: Explains when available data cannot answer a question (e.g. general financial market queries) rather than inventing unverified citations or causal claims.

### 4. Module 10: Email Campaign Centre
- **Audience Selection & Gating**: Filters by segment, geographic region, and category affinity.
- **DPDPA 2023 Consent Audit**: Excludes opted-out recipients, transactional-only accounts, customers with active support tickets, and global suppression lists.
- **Brand Template Engine**: Approved, editable templates for product announcements, loyalty recognitions, re-engagement offers, feedback surveys, and service advisories. Unsubscribe mechanisms are automatically enforced.
- **Mandatory Approval Workflow**: Complete message preview, audience sizing, internal test email dispatch to a sandbox address, explicit operator authorization checkbox, and final confirmation before execution.
- **Mock Sandbox Provider**: Telemetry tracking for dispatched, delivered, bounced, unsubscribed, and clicked events with documented denominators.

### 5. Module 11: Customer Notification Centre
- **Multi-Channel Architecture**: In-app notification cards, documented PWA/Service Worker browser push architecture, and email notifications.
- **TRAI Quiet Hours Enforcement**: Active guardrails pausing commercial and promotional communications between 9:00 PM and 9:00 AM IST. Service advisories bypass quiet hours.
- **Notification Feed & Queue**: Live in-app notification card feed with "Mark Read" functionality, frequency capping (max 2 alerts/day), and duplicate send prevention.
- **PWA / Service Worker Architecture Guide**: Full technical documentation detailing how client-side Web Push (VAPID key exchange, PushManager, service worker) bridges to consumer devices outside the internal Streamlit dashboard.

### 6. Module 12: CRM & REST API Schemas
- **Standardized Data Model**: Dataclass definitions for `customers`, `transactions`, `customer_preferences`, `consent_records`, `customer_segments`, `campaign_definitions`, `campaign_recipients`, `campaign_events`, `notification_preferences`, `notification_events`, `AI_recommendations`, and `audit_logs`.
- **Documented REST API Schemas**: JSON request/response schemas for `/api/v1/customers/{customer_id}`, `/api/v1/customers/consent`, `/api/v1/campaigns/dispatch`, `/api/v1/notifications/push`, and `/api/v1/analytics/rfm-segments`.
- **Production Architecture**: Architectural blueprint for migrating from session state to PostgreSQL with Row-Level Security (RLS) and Redis for rate-limiting.

### 7. Module 13 & 14: Data Quality & MBA-Grade PDF Report
- **Field Schema Audit & Hygiene Score**: Null frequencies, negative quantity clipping, and canonical alias mapping (`revenue_inr` $\rightarrow$ `revenue`, `stock_closing_units` $\rightarrow$ `stock_on_hand`).
- **Publication-Grade PDF Export**: Multi-page ReportLab Platypus report with running headers, "Page X of Y" footers, high-resolution embedded Matplotlib figures, customer segment distribution table, campaign consent audit summary, and clickable verified citations.

### 8. Module 15 & 16: Architecture & Academic Documentation
- **7 Conceptual Diagrams**:
  - Diagram A: Business Value Chain
  - Diagram B: System Architecture Pipeline
  - Diagram C: Demand Forecasting Workflow
  - Diagram D: 2x2 Multi-Temperature Inventory Risk Matrix
  - Diagram E: Ishikawa Fishbone Root-Cause Framework
  - Diagram F: Closed-Loop Model Retraining Feedback Loop
  - Diagram G: End-to-End Customer Campaign & Notification Workflow
- **Verified Sources**: Live HTTP-verified citations to official Amul, NDDB, DAHD, MoFPI, DPDPA 2023, and TRAI portals.

---

## 📂 Project Structure

```
amul-demand-intelligence/
├── .streamlit/
│   ├── config.toml                     # Enterprise Amul Red/Navy branding theme
│   └── secrets.toml.example            # Sample credentials template for production
├── assets/
│   └── amul_logo.svg                   # Verified official vector Amul logo asset
├── data/
│   ├── sample_amul_distribution_data.csv # 8,400-row synthetic operational dataset
│   └── sample_customer_profiles.csv    # 120 synthetic customer records with RFM/consent
├── src/
│   ├── __init__.py
│   ├── visual_theme.py                 # Enterprise CSS styling & Plotly template
│   ├── data_generator.py               # Multi-temperature synthetic simulation generator
│   ├── data_loader.py                  # Schema normalization, alias mapping & data quality audit
│   ├── forecasting.py                  # Time-series ML & baseline models, chronological split
│   ├── inventory.py                    # Multi-temperature inventory policies & ROP
│   ├── kpi.py                          # Executive KPI computations
│   ├── recommendations.py              # Explainable AI prescriptive recommendation engine
│   ├── insights_engine.py              # Dynamic data-driven insights & root cause correlations
│   ├── pdf_generator.py                # Publication-grade ReportLab Platypus PDF generator
│   ├── sources.py                      # Verified external citations and HTTP link verification
│   ├── api_client.py                   # REST API client with auth, retry, pagination & sandbox
│   ├── diagrams.py                     # Mermaid & Plotly architectural & conceptual diagrams
│   ├── customer_intelligence.py        # RFM segmentation & explainable Next-Best-Action
│   ├── chatbot.py                      # Amul AI Analyst deterministic query engine
│   ├── campaign_manager.py             # DPDPA consent gating, brand templates & email provider
│   ├── notification_center.py          # In-app cards, TRAI quiet hours & PWA push architecture
│   ├── crm_models.py                   # Dataclasses, JSON schemas & PostgreSQL RLS blueprint
│   └── ui_customer_modules.py          # Interactive Streamlit UI for customer modules
├── tests/
│   ├── __init__.py
│   ├── test_data_validation.py         # Schema mapping, negative clipping & storage inference
│   ├── test_forecasting.py             # Chronological split & zero-demand WAPE
│   ├── test_inventory.py               # Days of cover & safety stock formulas
│   ├── test_api_client.py              # Mock API, 401 unauthorized, and timeouts
│   ├── test_insights_and_pdf.py        # Alias resolution, insights engine & PDF build verification
│   └── test_customer_campaigns.py      # RFM segmentation, consent gating, chatbot & notifications
├── app.py                              # Main 16-module Streamlit dashboard
├── requirements.txt                    # Project dependencies (including reportlab & matplotlib)
├── README.md                           # Documentation, methodology & deployment manual
└── .gitignore                          # Git exclusions for secrets, caches, and venv
```

---

## 🧪 Automated Test Suite (34 Passing Tests)

The test suite validates data schemas, zero-demand WAPE edge cases, inventory risk calculations, API client mocks, insights computation, PDF compilation, RFM segmentation, DPDPA consent filtering, email duplicate prevention, quiet hours enforcement, and chatbot deterministic query lineage.

```powershell
# Run the complete test suite:
python -m pytest tests/ -v
```

**Test Execution Results:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\harsh\.gemini\antigravity-ide\scratch\amul-demand-intelligence
collected 34 items

tests/test_api_client.py::test_api_client_mock_mode PASSED               [  2%]
tests/test_api_client.py::test_api_client_handles_unauthorized_401 PASSED [  5%]
tests/test_api_client.py::test_api_client_handles_timeout PASSED         [  8%]
tests/test_api_client.py::test_api_client_handles_malformed_json PASSED  [ 11%]
tests/test_customer_campaigns.py::test_rfm_segment_classification PASSED [ 14%]
tests/test_customer_campaigns.py::test_next_best_action_with_support_complaint PASSED [ 17%]
tests/test_customer_campaigns.py::test_next_best_action_opted_out_consent PASSED [ 20%]
tests/test_customer_campaigns.py::test_filter_campaign_audience_consent_suppression PASSED [ 23%]
tests/test_customer_campaigns.py::test_email_template_generation PASSED  [ 26%]
tests/test_customer_campaigns.py::test_mock_email_provider_send_and_deduplication PASSED [ 29%]
tests/test_customer_campaigns.py::test_mock_email_provider_batch_telemetry PASSED [ 32%]
tests/test_customer_campaigns.py::test_quiet_hours_logic PASSED          [ 35%]
tests/test_customer_campaigns.py::test_notification_dispatch_manager PASSED [ 38%]
tests/test_customer_campaigns.py::test_chatbot_engine_deterministic_answers PASSED [ 41%]
tests/test_data_validation.py::test_validation_detects_missing_required_fields PASSED [ 44%]
tests/test_data_validation.py::test_validation_applies_column_mapping PASSED [ 47%]
tests/test_data_validation.py::test_validation_clips_negative_numbers PASSED [ 50%]
tests/test_data_validation.py::test_storage_type_inferred_when_missing PASSED [ 52%]
tests/test_forecasting.py::test_wape_zero_demand_returns_none PASSED     [ 55%]
tests/test_forecasting.py::test_wape_calculation_correctness PASSED      [ 58%]
tests/test_forecasting.py::test_evaluate_forecast_handles_empty_arrays PASSED [ 61%]
tests/test_forecasting.py::test_feature_engineering_creates_lags PASSED  [ 64%]
tests/test_forecasting.py::test_chronological_split_avoids_data_leakage PASSED [ 67%]
tests/test_insights_and_pdf.py::test_schema_mapping_revenue_inr_and_stock_closing PASSED [ 70%]
tests/test_insights_and_pdf.py::test_no_overwrite_existing_canonical_column PASSED [ 73%]
tests/test_insights_and_pdf.py::test_safe_daily_aggregation_does_not_throw_keyerror PASSED [ 76%]
tests/test_insights_and_pdf.py::test_data_quality_report PASSED          [ 79%]
tests/test_insights_and_pdf.py::test_insights_engine_computation PASSED  [ 82%]
tests/test_insights_and_pdf.py::test_pdf_generation PASSED               [ 85%]
tests/test_inventory.py::test_days_of_cover_zero_demand PASSED           [ 88%]
tests/test_inventory.py::test_days_of_cover_normal PASSED                [ 91%]
tests/test_inventory.py::test_safety_stock_formula PASSED                [ 94%]
tests/test_inventory.py::test_inventory_turnover_missing_cost_data PASSED [ 97%]
tests/test_inventory.py::test_storage_specific_stockout_flag PASSED      [100%]

======================= 34 passed in 4.30s ========================
```

---

## 🚀 How to Run the Dashboard Locally

1. **Navigate to the Project Directory:**
   ```powershell
   cd C:\Users\harsh\.gemini\antigravity-ide\scratch\amul-demand-intelligence
   ```

2. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit Application:**
   ```powershell
   streamlit run app.py
   ```

The application will launch in your browser at `http://localhost:8501`.

---

## 🌐 Deployment Guide: GitHub, Streamlit Community Cloud & Vercel

### 1. Push to GitHub
Your local repository is already initialized and committed on the `main` branch. To link and push to your GitHub account:

1. Create a new empty repository on [GitHub](https://github.com/new) (e.g., named `amul-demand-intelligence`). Do **not** initialize it with a README or .gitignore since we already have them.
2. In PowerShell, link your local repository and push:
   ```powershell
   cd C:\Users\harsh\.gemini\antigravity-ide\scratch\amul-demand-intelligence
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/amul-demand-intelligence.git
   git branch -M main
   git push -u origin main
   ```

---

### 2. Deploy Live Interactive Dashboard on Streamlit Community Cloud (Recommended)
Because Streamlit is an interactive Python application relying on persistent WebSocket connections (`_stcore/stream`), **Streamlit Community Cloud** is the official, zero-cost, native hosting platform:
1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `<YOUR_GITHUB_USERNAME>/amul-demand-intelligence`.
4. Branch: `main`
5. Main file path: `app.py`
6. (Optional) Under **Advanced settings**, set any environment secrets (e.g. `GEMINI_API_KEY`).
7. Click **"Deploy!"**. Your full 16-module interactive dashboard will be live on a public URL with automatic continuous deployment on every `git push`.

---

### 3. Deploy on Vercel
This repository includes [`vercel.json`](file:///C:/Users/harsh/.gemini/antigravity-ide/scratch/amul-demand-intelligence/vercel.json) and an Amul-branded landing portal [`index.html`](file:///C:/Users/harsh/.gemini/antigravity-ide/scratch/amul-demand-intelligence/index.html) configured for immediate Vercel deployment:

#### Method A: Via Vercel Web Dashboard (1-Click with GitHub)
1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **"Add New..."** -> **"Project"**.
3. Import your `amul-demand-intelligence` repository from GitHub.
4. Leave root directory as `./` and click **"Deploy"**.
5. Vercel will instantly build and host the high-performance showcase portal.

#### Method B: Via Vercel CLI
```powershell
# In PowerShell:
npx -y vercel deploy --prod
```

---

## 📑 How to Generate and Download the PDF Report

1. Open the application at `http://localhost:8501`.
2. In the sidebar, select **"14. Insights & PDF Report"**.
3. (Optional) Adjust your date range, product category, or regional filters in the sidebar.
4. Click the red button: **"Generate and Download PDF Analysis Report"**.
5. Once compiled, click **"⬇️ Download PDF Document"** to save the publication-grade PDF report directly to your machine.

---

## 🛡️ Privacy, DPDPA 2023 & Electronic Communications Compliance

1. **Digital Personal Data Protection Act (DPDPA), 2023**:
   - Explicit consent tracking (`consent_status`: `CONSENTED_MARKETING`, `TRANSACTIONAL_ONLY`, `OPTED_OUT`).
   - Purpose limitation: Transactional and service notices are strictly separated from commercial promotional emails.
   - Right to withdraw consent: Every marketing draft mandates a clear, single-click unsubscribe footer.
   - Suppression priority: Open consumer support tickets immediately suppress marketing campaigns in favor of service resolution.
2. **TRAI Commercial Communications (TCCCPR)**:
   - Quiet hours guardrails enforce no automated commercial messages between 21:00 and 09:00 IST.
   - Frequency capping prevents consumer fatigue (maximum 2 notifications per 24-hour window).
3. **Synthetic Demonstration Boundary**:
   - All customer profiles, email addresses, and phone numbers in this prototype are synthetic mock records. No real consumer data is used, stored, or contacted.
