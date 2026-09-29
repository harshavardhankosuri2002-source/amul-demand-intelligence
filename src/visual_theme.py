"""
AMUL Visual Theme and Design System.
Defines official color tokens, enterprise CSS injection, and Plotly figure styling.
Adheres strictly to Amul brand identity:
- Primary Red: #C4122F (Amul Red accent)
- Deep Navy: #0B2545 (Enterprise text & headers)
- Secondary Blue: #1E3A8A
- Pure White: #FFFFFF
- Subtle Slate Borders: #E2E8F0
- Background Neutral: #F8FAFC
"""

import plotly.graph_objects as go
import plotly.io as pio

# Color Tokens
AMUL_RED = "#C4122F"
AMUL_RED_LIGHT = "#FEF2F2"
AMUL_RED_HOVER = "#A50E26"
AMUL_NAVY = "#0B2545"
AMUL_NAVY_LIGHT = "#1E3A8A"
AMUL_WHITE = "#FFFFFF"
AMUL_BG = "#F8FAFC"
AMUL_BORDER = "#E2E8F0"
AMUL_TEXT_MUTED = "#64748B"
AMUL_GREEN = "#16A34A"
AMUL_AMBER = "#D97706"
AMUL_BLUE = "#2563EB"

CUSTOM_CSS = """
<style>
    /* Global font and background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0B2545;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }
    
    /* Header brand banner */
    .amul-header-banner {
        background: #FFFFFF;
        border-bottom: 2px solid #C4122F;
        padding: 0.85rem 1.5rem;
        margin-bottom: 1.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(11, 37, 69, 0.05);
    }
    
    /* KPI Card styling */
    .amul-kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 2px rgba(11, 37, 69, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 0.75rem;
    }
    
    .amul-kpi-card:hover {
        box-shadow: 0 4px 6px -1px rgba(11, 37, 69, 0.08);
        border-color: #CBD5E1;
    }
    
    .amul-kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.35rem;
    }
    
    .amul-kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0B2545;
        line-height: 1.2;
    }
    
    .amul-kpi-subtext {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 0.35rem;
    }
    
    .amul-badge-alert {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #FEF2F2;
        color: #C4122F;
        border: 1px solid #FCA5A5;
    }
    
    .amul-badge-success {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #F0FDF4;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    
    .amul-badge-warning {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #FFFBEB;
        color: #D97706;
        border: 1px solid #FDE68A;
    }
    
    .amul-badge-info {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #EFF6FF;
        color: #2563EB;
        border: 1px solid #BFDBFE;
    }
    
    /* Status banner */
    .status-pill-demo {
        background-color: #FEF2F2;
        color: #C4122F;
        border: 1px solid #F87171;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    
    .status-pill-live {
        background-color: #F0FDF4;
        color: #15803D;
        border: 1px solid #4ADE80;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    
    /* Table headers and rows */
    .dataframe {
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
    }
    
    /* Streamlit buttons */
    div.stButton > button:first-child {
        background-color: #C4122F;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.45rem 1rem;
        transition: all 0.15s ease;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #A50E26;
        color: white;
        border: none;
        box-shadow: 0 2px 4px rgba(196, 18, 47, 0.25);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        color: #64748B;
        font-weight: 500;
        border-bottom: 2px solid transparent;
        padding-left: 0.25rem;
        padding-right: 0.25rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #C4122F !important;
        border-bottom-color: #C4122F !important;
        font-weight: 600;
    }
    
    /* Card panel container */
    .amul-panel {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 2px rgba(11, 37, 69, 0.03);
    }
    
    .amul-panel-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0B2545;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #F1F5F9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
"""


def apply_amul_theme(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """
    Applies clean enterprise Amul brand styling to a Plotly figure.
    Removes visual noise, formats grid lines, and enforces legible typography.
    """
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Inter, sans-serif", size=15, color=AMUL_NAVY),
            x=0.01,
            y=0.96,
        ),
        font=dict(family="Inter, sans-serif", size=12, color=AMUL_NAVY),
        paper_bgcolor=AMUL_WHITE,
        plot_bgcolor=AMUL_WHITE,
        height=height,
        margin=dict(l=45, r=25, t=48 if title else 25, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=False,
            showline=True,
            linecolor="#CBD5E1",
            tickfont=dict(color=AMUL_TEXT_MUTED, size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=False,
            showline=True,
            linecolor="#CBD5E1",
            tickfont=dict(color=AMUL_TEXT_MUTED, size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=AMUL_NAVY),
            bgcolor="rgba(255,255,255,0.7)",
        ),
        hoverlabel=dict(
            bgcolor=AMUL_NAVY,
            font_size=12,
            font_family="Inter, sans-serif",
            font_color=AMUL_WHITE,
        ),
    )
    return fig


def format_inr(value: float, decimals: int = 0) -> str:
    """Formats a float as Indian Rupee (INR) currency string with proper numbering."""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    
    is_neg = value < 0
    value = abs(value)
    
    if value >= 10_000_000:
        val_str = f"₹{value / 10_000_000:.2f} Cr"
    elif value >= 100_000:
        val_str = f"₹{value / 100_000:.2f} Lakh"
    elif value >= 1_000:
        val_str = f"₹{value:,.{decimals}f}"
    else:
        val_str = f"₹{value:.{decimals}f}"
        
    return f"-{val_str}" if is_neg else val_str


def format_units(value: float) -> str:
    """Formats large unit numbers cleanly (Lakhs, Thousands, or Integer)."""
    if value is None or (isinstance(value, float) and value != value):
        return "N/A"
    if value >= 100_000:
        return f"{value / 100_000:.2f} L units"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k units"
    else:
        return f"{int(value):,} units"
