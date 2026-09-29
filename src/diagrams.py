"""
AMUL Conceptual System Diagrams and Methodology Visuals.
Implements the 6 required diagrams:
1. Diagram A: Business Value Chain (Milk procurement -> Consumer + Data Feedback)
2. Diagram B: System Architecture (End-to-end data pipeline & on-demand refresh)
3. Diagram C: Demand Forecasting Workflow (Chronological split, baseline vs ML, monitoring)
4. Diagram D: Inventory Risk Matrix (Plotly 2x2 Quadrant scatter plot with configurable thresholds)
5. Diagram E: Root-Cause Fishbone (Ishikawa diagram across Demand, Inventory, Distribution, Product, Data)
6. Diagram F: Model Feedback Loop (Continuous learning cycle)
"""

import pandas as pd
import plotly.graph_objects as go
from src.visual_theme import AMUL_NAVY, AMUL_RED, AMUL_WHITE, apply_amul_theme

# Diagram A: Mermaid Value Chain
DIAGRAM_A_MERMAID = """
graph LR
    subgraph SCM["Physical Supply Chain Flow"]
        P1["1. Farmer Procurement<br/>& Village Societies"] --> P2["2. District Milk Unions<br/>& Processing Plants"]
        P2 --> P3["3. Mother Dairies &<br/>Central CFA Warehouses"]
        P3 --> P4["4. Wholesale Distributors<br/>& Cold Chain Logistics"]
        P4 --> P5["5. Retailers & APOs<br/>(Amul Preferred Outlets)"]
        P5 --> P6["6. End Consumer"]
    end

    subgraph DATA_FEEDBACK["Intelligence & Data Flow"]
        P5 -.->|"Point-of-Sale Data"| DS["Amul AI Intelligence Layer"]
        P4 -.->|"Distributor Depletion & Stock"| DS
        P3 -.->|"Batch Expiry & Capacity"| DS
        DS ==>|"Optimized Replenishment & Forecasts"| P3
        DS ==>|"Demand Signals"| P2
    end

    classDef amulNode fill:#FFFFFF,stroke:#C4122F,stroke-width:2px,color:#0B2545,font-family:sans-serif;
    classDef dataNode fill:#EFF6FF,stroke:#1E3A8A,stroke-width:2px,color:#1E3A8A,font-weight:bold;
    class P1,P2,P3,P4,P5,P6 amulNode;
    class DS dataNode;
"""

# Diagram B: Mermaid System Architecture
DIAGRAM_B_MERMAID = """
flowchart TD
    subgraph INGESTION["Data Ingestion Layer"]
        A1["Authorized Distributor ERP / REST API"] --> B["Data Validation & Sanity Engine"]
        A2["Manual CSV / Enterprise File Upload"] --> B
        B -->|"Null checks, Type coercions, Outlier flags"| C["Standardized Data Schema"]
    end

    subgraph ENGINE["Analytical Processing Core"]
        C --> D["Feature Engineering<br/>(Lags, Rolling Means, Calendar, Promotions)"]
        D --> E["Forecasting Pipeline<br/>(Chronological Split: Baseline vs ML)"]
        D --> F["Inventory & Cold-Chain Rules<br/>(Multi-temperature ROP, Safety Stock, DOC)"]
        E --> G["Risk & Recommendation Engine<br/>(Explainable Triggers & Prioritization)"]
        F --> G
    end

    subgraph CONSUMPTION["Enterprise Streamlit UI Layer"]
        G --> H["Executive Overview & KPIs"]
        G --> I["Demand Forecasting Workbench"]
        G --> J["Inventory & Replenishment Console"]
        G --> K["Distribution & Regional Intelligence"]
        G --> L["Expiry & Wastage Tracker"]
        G --> M["Decision-Support AI Action Queue"]
    end

    REFRESH(["On-Demand Refresh Trigger"]) -.->|"Invalidates cache & recalculates"| B

    classDef amulRed fill:#FEF2F2,stroke:#C4122F,stroke-width:2px,color:#C4122F;
    classDef amulNavy fill:#FFFFFF,stroke:#0B2545,stroke-width:2px,color:#0B2545;
    class A1,A2,C,D,E,F,G amulNavy;
    class REFRESH amulRed;
"""

# Diagram C: Mermaid Forecasting Workflow
DIAGRAM_C_MERMAID = """
flowchart LR
    D1["Historical Sales & Inventory Data"] --> D2["Data Quality & Hygiene Checks"]
    D2 --> D3["Chronological Train/Test Split<br/>(No Lookahead Data Leakage)"]
    D3 --> D4["Baseline Forecast<br/>(7-day Moving Avg / Seasonal Naive)"]
    D3 --> D5["Supervised ML Models<br/>(Gradient Boosting / Random Forest)"]
    D4 --> D6["Model Evaluation Gate<br/>(MAE, RMSE, WAPE Comparison)"]
    D5 --> D6
    D6 --> D7["Select Superior Model<br/>& Predict Future Horizon"]
    D7 --> D8["SKU Replenishment Orders<br/>& Out-of-Stock Alerts"]
    D8 --> D9["Post-Cycle Variance Monitoring"]
    
    classDef box fill:#FFFFFF,stroke:#0B2545,stroke-width:1.5px,color:#0B2545;
    class D1,D2,D3,D4,D5,D6,D7,D8,D9 box;
"""

# Diagram E: Mermaid Ishikawa Fishbone
DIAGRAM_E_MERMAID = """
flowchart TD
    subgraph FISHBONE["Conceptual Ishikawa (Fishbone) Supply-Demand Variance Hypotheses"]
        D_CAUSE["DEMAND FACTORS<br/>- Unseasonable Weather Shifts<br/>- Unannounced Regional Festivals<br/>- Local Competitor Stockouts<br/>- Promo Price Elasticity Variance"]
        
        I_CAUSE["INVENTORY POLICIES<br/>- Inaccurate Physical Count Reconciliation<br/>- Rigid Reorder Points (No Seasonal Buffer)<br/>- Safety Stock Not Adjusted for Lead Time<br/>- High Minimum Order Quantities"]
        
        DIST_CAUSE["DISTRIBUTION LOGISTICS<br/>- Cold-Chain Reefer Truck Delays<br/>- Urban Ingress Restrictions<br/>- Primary Depot Transit Variance<br/>- Transshipment Bottlenecks"]
        
        PROD_CAUSE["PRODUCT CHARACTERISTICS<br/>- Ultra-Short Shelf Life (Fresh Milk: 48h)<br/>- Deep Freeze Sensitivity (-18°C Ice Cream)<br/>- Bulky Storage Footprint (UHT Milk)<br/>- Fragile Packaging Integrity"]
        
        DATA_CAUSE["DATA & VISIBILITY GAPS<br/>- Delayed Kirana Depletion Feeds<br/>- Inconsistent Master SKU Codes<br/>- Missing Promotional Calendar Inputs<br/>- Unreported Spoilage / Wastage Data"]
    end
    
    EFFECT["SUPPLY CHAIN VARIANCE<br/>(Avoidable Stockouts & Avoidable Spoilage)"]
    
    D_CAUSE --> EFFECT
    I_CAUSE --> EFFECT
    DIST_CAUSE --> EFFECT
    PROD_CAUSE --> EFFECT
    DATA_CAUSE --> EFFECT

    classDef effectBox fill:#FEF2F2,stroke:#C4122F,stroke-width:3px,color:#C4122F,font-weight:bold;
    classDef causeBox fill:#FFFFFF,stroke:#CBD5E1,stroke-width:1.5px,color:#0B2545;
    class EFFECT effectBox;
    class D_CAUSE,I_CAUSE,DIST_CAUSE,PROD_CAUSE,DATA_CAUSE causeBox;
"""

# Diagram F: Mermaid Model Feedback Loop
DIAGRAM_F_MERMAID = """
flowchart TD
    M1["1. Model Generates Demand Forecast & Intervals"] --> M2["2. Planners / Systems Place Replenishment Orders"]
    M2 --> M3["3. Logistics Dispatches Stock to Regional Depots"]
    M3 --> M4["4. Actual Sales, Stockouts & Spoilage Recorded at Retail"]
    M4 --> M5["5. Residual Error Analysis (Actual vs Forecasted WAPE/Bias)"]
    M5 --> M6["6. Feature Importance Recalibration & Model Retraining"]
    M6 --> M1
    
    classDef cycleNode fill:#FFFFFF,stroke:#1E3A8A,stroke-width:2px,color:#0B2545;
    class M1,M2,M3,M4,M5,M6 cycleNode;
"""

# Diagram G: Customer Campaign & Notification Workflow (Module 5)
DIAGRAM_G_MERMAID = """
flowchart TD
    G1["1. Authorized Customer & Transaction Data"] --> G2["2. Data Validation & Consent Verification (DPDPA)"]
    G2 --> G3["3. RFM Analysis & Customer Segmentation"]
    G3 --> G4["4. Next-Best-Action Prescriptive Engine"]
    G4 --> G5["5. AI-Generated Campaign / Notification Draft"]
    G5 --> G6["6. Eligible Audience Review & Suppression Filter"]
    G6 --> G7["7. Internal Test Send to Designated QA Email"]
    G7 --> G8{"8. Human Review & Operator Approval"}
    G8 -- Rejected --> G5
    G8 -- Approved --> G9["9. Multi-Channel Dispatch (Email / In-App)"]
    G9 --> G10["10. Delivery & Engagement Telemetry Tracking"]
    G10 --> G11["11. Campaign Performance Analysis"]
    G11 --> G1["12. Feedback Loop to Customer Insights"]

    classDef procNode fill:#FFFFFF,stroke:#0B2545,stroke-width:1.5px,color:#0B2545;
    classDef gateNode fill:#FEF2F2,stroke:#C4122F,stroke-width:2px,color:#C4122F,font-weight:bold;
    class G1,G2,G3,G4,G5,G6,G7,G9,G10,G11 procNode;
    class G8 gateNode;
"""


def build_inventory_risk_matrix_chart(inventory_df: pd.DataFrame) -> go.Figure:
    """
    Renders Diagram D: Interactive 2x2 Inventory Risk Matrix.
    X-axis: Days of Cover (Excess Risk -> High Days of Cover)
    Y-axis: Estimated Stockout Probability (Inverse of stock relative to reorder point)
    """
    if inventory_df.empty:
        fig = go.Figure()
        return apply_amul_theme(fig, "Inventory Risk Matrix (No Data)")
        
    df = inventory_df.copy()
    
    # Calculate synthetic risk coordinates for standard quadrant plotting
    # Stockout Risk Index (0 to 100): High when current_stock < ROP
    df["stockout_risk_score"] = np.clip(
        (1.0 - (df["current_stock"] / df["reorder_point"].replace(0, 1))) * 100, 0, 100
    )
    
    # Excess / Spoilage Score (0 to 100): High when DOC is large or days_to_expiry is short
    doc_safe = df["days_of_cover"].fillna(0)
    df["excess_risk_score"] = np.clip((doc_safe / 40.0) * 100, 0, 100)
    
    color_map = {
        "Fresh": "#C4122F",      # Amul Red for fresh
        "Chilled": "#2563EB",    # Blue
        "Frozen": "#0284C7",     # Cyan
        "Ambient": "#D97706",    # Amber
    }
    
    fig = go.Figure()
    
    for storage_type in ["Fresh", "Chilled", "Frozen", "Ambient"]:
        subset = df[df["storage_type"] == storage_type]
        if not subset.empty:
            fig.add_trace(
                go.Scatter(
                    x=subset["excess_risk_score"],
                    y=subset["stockout_risk_score"],
                    mode="markers+text",
                    name=f"{storage_type} Products",
                    marker=dict(
                        size=14,
                        color=color_map.get(storage_type, "#64748B"),
                        line=dict(width=1.5, color=AMUL_WHITE),
                        opacity=0.88,
                    ),
                    text=subset["sku_id"].apply(lambda s: s[-3:]),
                    textposition="top center",
                    textfont=dict(size=10, color=AMUL_NAVY),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "SKU: %{customdata[1]}<br>"
                        "Region: %{customdata[2]}<br>"
                        "Current Stock: %{customdata[3]:,} units<br>"
                        "Days of Cover: %{customdata[4]} days<br>"
                        "Reorder Point: %{customdata[5]:,} units<br>"
                        "Status: %{customdata[6]}<extra></extra>"
                    ),
                    customdata=subset[[
                        "product_name",
                        "sku_id",
                        "region",
                        "current_stock",
                        "days_of_cover",
                        "reorder_point",
                        "risk_label",
                    ]].values,
                )
            )
            
    # Add Quadrant Reference Lines
    fig.add_shape(
        type="line", x0=50, y0=0, x1=50, y1=100,
        line=dict(color="#CBD5E1", width=1.5, dash="dash"),
    )
    fig.add_shape(
        type="line", x0=0, y0=50, x1=100, y1=50,
        line=dict(color="#CBD5E1", width=1.5, dash="dash"),
    )
    
    # Quadrant Annotations
    fig.add_annotation(
        x=25, y=85, text="<b>QUADRANT I: CRITICAL STOCKOUT RISK</b><br>Low Cover, Immediate Replenishment Required",
        showarrow=False, font=dict(color="#C4122F", size=10), bgcolor="rgba(254, 242, 242, 0.75)",
    )
    fig.add_annotation(
        x=75, y=85, text="<b>QUADRANT II: VOLATILE / ANOMALOUS</b><br>High Discrepancy (Review Stock Records)",
        showarrow=False, font=dict(color="#D97706", size=10), bgcolor="rgba(255, 251, 235, 0.75)",
    )
    fig.add_annotation(
        x=25, y=15, text="<b>QUADRANT III: OPTIMAL ZONE</b><br>Balanced Stock, Safe Reorder Buffer",
        showarrow=False, font=dict(color="#16A34A", size=10), bgcolor="rgba(240, 253, 244, 0.75)",
    )
    fig.add_annotation(
        x=75, y=15, text="<b>QUADRANT IV: EXCESS / EXPIRY RISK</b><br>High Cover, Working Capital Locked / Spoilage",
        showarrow=False, font=dict(color="#2563EB", size=10), bgcolor="rgba(239, 246, 255, 0.75)",
    )

    fig.update_layout(
        xaxis=dict(title="Excess Inventory / Spoilage Risk Score (0-100)", range=[-2, 102]),
        yaxis=dict(title="Stockout Risk Probability Score (0-100)", range=[-2, 102]),
    )
    return apply_amul_theme(fig, "Diagram D: Conceptual Multi-Temperature Inventory Risk Matrix", height=480)
