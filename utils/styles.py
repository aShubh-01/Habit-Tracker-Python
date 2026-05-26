"""
utils/styles.py — Core CSS injected once on app load.
Philosophy: warm light theme, minimal Notion-like feel.
"""
import streamlit as st

MAIN_CSS = """
<style>
/* ── Fonts ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Global Background (Warm Off-white) ──────────────── */
.stApp {
    background-color: #FAFAF8 !important;
    color: #1C1C1E !important;
}

/* ── Hide Streamlit chrome ───────────────────────────── */
#MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }

[data-testid="stSidebar"] {
    background-color: #F4F4F2 !important;
    border-right: 1px solid #E5E5E0 !important;
    color: #4A4A4A !important;
}
[data-testid="stSidebar"] label {
    color: #4A4A4A !important;
}

/* ── Sidebar Radio → nav style ───────────────────────── */
[data-testid="stSidebar"] .stRadio > div { gap: 4px !important; }
[data-testid="stSidebar"] .stRadio label {
    border-radius: 8px !important;
    padding: 8px 14px !important;
    cursor: pointer !important;
    font-size: 0.9rem !important;
    transition: all 0.15s ease !important;
    color: #4A4A4A !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #EBEBE8 !important;
    color: #1C1C1E !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #FFFFFF !important;
    color: #6366F1 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    border-left: 3px solid #6366F1 !important;
}

/* ── Main content area ───────────────────────────────── */
.main .block-container {
    padding: 2.5rem 3rem 3rem !important;
    max-width: 1100px;
}

/* ── Metrics ─────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    transition: all 0.2s ease !important;
}
[data-testid="metric-container"]:hover {
    border-color: #6366F1 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}
[data-testid="stMetricValue"] { color: #1C1C1E !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #6B7280 !important; font-size: 0.8rem !important; }
[data-testid="stMetricDelta"] svg { display: none !important; }

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button, .stFormSubmitButton > button, [data-testid="stFormSubmitButton"] button {
    background: #6366F1 !important;
    color: #FFFFFF !important;
    border: 1px solid #4F46E5 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: #4F46E5 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2) !important;
    color: #FFFFFF !important;
}
.stButton > button:active, .stFormSubmitButton > button:active, [data-testid="stFormSubmitButton"] button:active { transform: translateY(0) !important; }

/* Secondary button style via key-based approach */
button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #374151 !important;
    border: 1px solid #D1D5DB !important;
}
button[kind="secondary"]:hover {
    background: #F9FAFB !important;
    border-color: #C7D2FE !important;
    color: #4F46E5 !important;
}

/* ── Inputs ──────────────────────────────────────────── */
div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stNumberInput"] div[data-baseweb="input"],
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stMultiSelect"] div[data-baseweb="select"],
.stTextInput div[data-baseweb="input"],
.stNumberInput div[data-baseweb="input"],
.stTextArea textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
    color: #1C1C1E !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
.stTextInput input,
.stNumberInput input,
input,
textarea {
    color: #1C1C1E !important;
    background-color: #FFFFFF !important;
    -webkit-text-fill-color: #1C1C1E !important;
}
div[data-baseweb="input"]:focus-within, textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
}

/* ── Tabs ────────────────────────────────────────────── */
[role="tab"] { color: #6B7280 !important; font-weight: 500 !important; }
[role="tab"][aria-selected="true"] { color: #6366F1 !important; font-weight: 700 !important; }

/* ── Progress bars ───────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366F1, #8B5CF6) !important;
    border-radius: 10px !important;
}
.stProgress > div > div > div {
    background: #E5E7EB !important;
    border-radius: 10px !important;
}

/* ── Expander ────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    margin-bottom: 0.75rem !important;
}
[data-testid="stExpander"] details summary {
    background-color: #FFFFFF !important;
    color: #1C1C1E !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stExpander"] details summary:hover {
    background-color: #F9FAFB !important;
}
[data-testid="stExpander"] details summary * {
    color: #1C1C1E !important;
}
[data-testid="stExpander"] details summary:hover * {
    color: #6366F1 !important;
}
[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid #E5E7EB !important;
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
}

/* ── BaseWeb Popups & Portals Overrides ─────────────── */
div[data-baseweb="popover"] *, div[role="listbox"] *, div[data-baseweb="calendar"] * {
    background-color: #FFFFFF !important;
    color: #1C1C1E !important;
}
div[data-baseweb="popover"] button:hover, div[role="listbox"] li:hover, div[data-baseweb="calendar"] [role="gridcell"]:hover {
    background-color: #F3F4F6 !important;
    color: #6366F1 !important;
}
div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    color: #1C1C1E !important;
    border-color: #D1D5DB !important;
}
div[data-baseweb="input"] input {
    color: #1C1C1E !important;
    background-color: transparent !important;
}

/* ── Dividers ────────────────────────────────────────── */

hr { border-color: #E5E7EB !important; }

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #6366F1; }

/* ── Label text ──────────────────────────────────────── */
label, .stRadio label p, .stCheckbox label p {
    color: #4B5563 !important;
    font-size: 0.85rem !important;
}

/* ── Checkbox ────────────────────────────────────────── */
.stCheckbox input:checked + label::before { background: #6366F1 !important; }

/* ── Animations ──────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.3s ease-out; }
</style>
"""

# ── Reusable HTML snippets ────────────────────────────────────────────────────

import re

def clean_html(html_str: str) -> str:
    """Helper to convert multiline indented HTML into a clean single line."""
    # Convert newlines to spaces
    html_str = html_str.replace("\n", " ")
    # Replace multiple spaces with a single space
    html_str = re.sub(r'\s+', ' ', html_str)
    return html_str.strip()

def st_html(text: str):
    """Safely render HTML in Streamlit without code-block formatting glitches."""
    st.html(clean_html(text))

def card(content: str, color_accent: str = "#6366F1", padding: str = "1.25rem") -> str:
    """Render a light card with optional left-border accent."""
    raw = f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E5E7EB;
        border-left:4px solid {color_accent};
        border-radius:10px;
        padding:{padding};
        margin-bottom:0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.01);
        transition: all 0.2s ease;
    " class="fade-up">
        {content}
    </div>
    """
    return clean_html(raw)

def xp_bar(pct: int, xp_in: int, xp_for: int) -> str:
    """Animated XP progress bar for light theme."""
    raw = f"""
    <div style="margin:0.5rem 0 0.25rem;">
        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6B7280;margin-bottom:4px;">
            <span>{xp_in} XP</span>
            <span>{xp_for} XP for next level</span>
        </div>
        <div style="background:#E5E7EB;border-radius:20px;height:10px;overflow:hidden;">
            <div style="
                width:{pct}%;
                height:100%;
                background:linear-gradient(90deg,#6366F1,#8B5CF6);
                border-radius:20px;
                transition:width 0.6s ease;
            "></div>
        </div>
    </div>
    """
    return clean_html(raw)

def page_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p style="color:#6B7280;margin:4px 0 0;font-size:0.92rem;">{subtitle}</p>' if subtitle else ""
    raw = f"""
    <div style="margin-bottom:1.75rem; border-bottom: 1px solid #E5E7EB; padding-bottom: 0.75rem;">
        <h1 style="color:#1C1C1E;font-size:1.75rem;font-weight:800;margin:0;letter-spacing:-0.02em;">{title}</h1>
        {sub_html}
    </div>
    """
    st_html(raw)

def inject_styles():
    st.html(MAIN_CSS)

