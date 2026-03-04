import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from services.ingestion import load_all
from services.performance_engine import compute_performance
from services.pinecone_service import PineconeService
from services.neo4j_service import Neo4jService
from services.rag_pipeline import RAGPipeline
from ui.dashboard import show_dashboard
from ui.employee_page import show_employees
from ui.graph_page import show_graph
from ui.chatbot_page import show_chatbot

st.set_page_config(
    page_title="Blinkit Enterprise AI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Background ── */
.stApp { background-color: #F5F6FA !important; }
section.main > div { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E8EAF0 !important;
    box-shadow: 2px 0 16px rgba(0,0,0,0.05) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.2rem 1rem; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    border-radius: 10px !important;
    border: 1.5px solid #E5E7EB !important;
    background-color: #FFFFFF !important;
    color: #374151 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
.stButton > button:hover {
    background-color: #FFF4EC !important;
    border-color: #FF7A00 !important;
    color: #FF7A00 !important;
    box-shadow: 0 3px 12px rgba(255,122,0,0.18) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #E8EAF0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #6B7280 !important;
    padding: 8px 20px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF7A00, #FF9A3C) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(255,122,0,0.3) !important;
}

/* ── Inputs ── */
.stSelectbox > div > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #E5E7EB !important;
    border-radius: 10px !important;
    color: #374151 !important;
}
.stTextInput > div > div > input {
    background-color: #FFFFFF !important;
    border: 1.5px solid #E5E7EB !important;
    border-radius: 10px !important;
    color: #374151 !important;
    padding: 0.5rem 0.75rem !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within {
    border-color: #FF7A00 !important;
    box-shadow: 0 0 0 3px rgba(255,122,0,0.12) !important;
    outline: none !important;
}

/* ── Metrics ── */
div[data-testid="stMetricValue"] { color: #FF7A00 !important; font-weight: 800 !important; font-size: 1.6rem !important; }
div[data-testid="stMetricLabel"] { color: #6B7280 !important; font-size: 0.8rem !important; font-weight: 600 !important; }
div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    box-shadow: 0 6px 20px rgba(255,122,0,0.1);
    border-color: #FFD4A8;
    transform: translateY(-2px);
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 12px !important;
    border: 1px solid #E8EAF0 !important;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #FFFFFF !important;
    border: 1px solid #E8EAF0 !important;
    border-radius: 12px !important;
    color: #374151 !important;
    font-weight: 600 !important;
}

/* ── Dividers & scrollbar ── */
hr { border: none !important; height: 1px !important; background: #E8EAF0 !important; margin: 1.5rem 0 !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F5F6FA; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #FF7A00; }

/* ── Multiselect tags ── */
span[data-baseweb="tag"] { background-color: #FFF4EC !important; color: #FF7A00 !important; border-radius: 6px !important; }

/* ── Reusable layout classes ── */
.page-header {
    background: linear-gradient(135deg, #FFFFFF 0%, #FFF8F2 100%);
    border: 1px solid #FFE4CC;
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    box-shadow: 0 4px 20px rgba(255,122,0,0.08);
}
.page-card {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E8EAF0;
    padding: 26px 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    margin-bottom: 20px;
}
.section-title {
    font-size: 1.0rem;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 14px;
}
.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E8EAF0;
    padding: 22px 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.22s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(255,122,0,0.14);
    border-color: #FFD4A8;
}
.kpi-icon { font-size: 1.7rem; margin-bottom: 8px; }
.kpi-value { font-size: 1.8rem; font-weight: 800; color: #FF7A00; line-height: 1; }
.kpi-label { font-size: 0.76rem; color: #9CA3AF; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 5px; }

/* ── Sidebar brand block ── */
.sidebar-logo {
    background: linear-gradient(135deg, #FFF4EC, #FFE8D0);
    border: 1.5px solid #FFD4A8;
    border-radius: 16px;
    padding: 18px 14px;
    text-align: center;
    margin-bottom: 22px;
}
.sidebar-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #9CA3AF;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin: 16px 0 8px 2px;
}
.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 10px;
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    margin-bottom: 6px;
    font-size: 0.84rem;
    color: #374151;
    font-weight: 500;
}

/* ── Leaderboard rows ── */
.leader-row {
    background: #FFFFFF;
    border: 1px solid #F3F4F6;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    transition: all 0.18s ease;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.leader-row:hover {
    box-shadow: 0 4px 16px rgba(255,122,0,0.1);
    border-color: #FFD4A8;
    transform: translateX(4px);
}

/* ── Chat bubbles ── */
.chat-user {
    background: linear-gradient(135deg, #FF7A00, #FF9A3C);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 18px;
    margin: 10px 0 10px 100px;
    box-shadow: 0 3px 14px rgba(255,122,0,0.28);
    font-size: 0.92rem;
    line-height: 1.55;
}
.chat-user-label {
    font-weight: 700;
    font-size: 0.72rem;
    opacity: 0.8;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.chat-bot {
    background: #FFFFFF;
    color: #1F2937;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 10px 100px 10px 0;
    border: 1px solid #E8EAF0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
    font-size: 0.92rem;
    line-height: 1.55;
}
.chat-bot-label {
    font-weight: 700;
    font-size: 0.72rem;
    color: #FF7A00;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.chat-ts { font-size: 0.7rem; opacity: 0.45; margin-top: 4px; }

/* ── Graph legend ── */
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #374151;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}
</style>
"""
st.markdown(LIGHT_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def init_services():
    pinecone_svc = PineconeService()
    neo4j_svc = Neo4jService()
    rag = RAGPipeline(pinecone_svc)
    return pinecone_svc, neo4j_svc, rag


@st.cache_data(show_spinner=False)
def load_data():
    return load_all()


pinecone_svc, neo4j_svc, rag = init_services()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2.4rem;line-height:1;"></div>
        <div style="font-weight:800;font-size:1.05rem;color:#FF7A00;margin-top:6px;">Blinkit Enterprise</div>
        <div style="font-size:0.7rem;color:#9CA3AF;margin-top:3px;font-weight:600;letter-spacing:0.06em;">
            SUPPLY CHAIN INTELLIGENCE
        </div>
    </div>
    <div class="sidebar-section-label">Navigation</div>
    """, unsafe_allow_html=True)

    pages = {
        "  Overview": "overview",
        "  Employees": "employees",
        "  Vendors & Logistics": "vendors",
        "  Knowledge Graph": "graph",
        "  AI Assistant": "chatbot",
    }
    selected_page = st.radio("nav", list(pages.keys()), label_visibility="collapsed")

    st.markdown('<div class="sidebar-section-label" style="margin-top:18px;">Service Status</div>', unsafe_allow_html=True)

    neo4j_ok = neo4j_svc.is_connected()
    pinecone_ok = pinecone_svc.is_connected()
    groq_ok = bool(__import__("config").GROQ_API_KEY)

    for name, ok, icon in [("Neo4j Aura", neo4j_ok, ""), ("Pinecone", pinecone_ok, ""), ("Groq LLM", groq_ok, "")]:
        dot = "🟢" if ok else "🔴"
        clr = "#16A34A" if ok else "#DC2626"
        lbl = "Online" if ok else "Offline"
        st.markdown(
            f"<div class='status-row'>{icon} <span style='flex:1'>{name}</span>"
            f"<span style='font-size:0.75rem;color:{clr};font-weight:700;'>{dot} {lbl}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='text-align:center;color:#D1D5DB;font-size:0.7rem;font-weight:500;margin-top:28px;'>"
        "v1.0.0 &nbsp;·&nbsp;Powered By Sriram</div>",
        unsafe_allow_html=True,
    )


with st.spinner("Loading supply chain data..."):
    data = load_data()

page_key = pages[selected_page]

if page_key == "overview":
    show_dashboard(data)

elif page_key == "employees":
    show_employees(data)

elif page_key == "vendors":
    st.markdown("""
    <div class="page-header">
        <div style="font-size:1.65rem;font-weight:800;color:#1F2937;"> Vendors &amp; Logistics</div>
        <div style="font-size:0.88rem;color:#9CA3AF;margin-top:4px;font-weight:500;">
            Supplier contracts, regional coverage, and delivery partner performance
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  Vendors", "  Logistics"])

    with tab1:
        vendors = data["vendors"]
        contracts = data["contracts"]
        active_c = len(contracts[contracts["status"] == "Active"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Vendors", len(vendors))
        col2.metric("Total Contract Value", f"₹{vendors['contract_value'].sum():,.0f}")
        col3.metric("Active Contracts", active_c)

        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'> Contract Value by Vendor</div>", unsafe_allow_html=True)
        fig = px.bar(
            vendors.sort_values("contract_value", ascending=True),
            x="contract_value", y="vendor_name", orientation="h",
            color="category",
            color_discrete_sequence=["#FF7A00","#FF9A3C","#FFB870","#4D96FF","#16A34A","#8B5CF6","#F59E0B"],
            labels={"contract_value": "Contract Value (₹)", "vendor_name": "Vendor"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFBFC",
            font=dict(color="#374151", family="Inter"), height=480,
            xaxis=dict(gridcolor="#F3F4F6"), yaxis=dict(tickfont=dict(color="#374151")),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📋 Contract Registry</div>", unsafe_allow_html=True)
        contracts_merged = contracts.merge(vendors[["vendor_name","category","region"]], on="vendor_name", how="left")
        st.dataframe(contracts_merged, use_container_width=True, height=300)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        logistics = data["logistics"]
        col1, col2, col3 = st.columns(3)
        col1.metric("Logistics Partners", len(logistics))
        col2.metric("Total Shipments", f"{logistics['shipments_handled'].sum():,}")
        col3.metric("Best Delivery Time", f"{logistics['avg_delivery_time'].min()} min")

        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'> Delivery Performance Matrix</div>", unsafe_allow_html=True)
        fig2 = px.scatter(
            logistics, x="avg_delivery_time", y="shipments_handled",
            size="shipments_handled", color="region", hover_name="partner_name",
            size_max=55,
            labels={"avg_delivery_time": "Avg Delivery Time (min)", "shipments_handled": "Total Shipments"},
            color_discrete_sequence=["#FF7A00","#FF9A3C","#4D96FF","#16A34A","#8B5CF6"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFBFC",
            font=dict(color="#374151", family="Inter"), height=360,
            xaxis=dict(gridcolor="#F3F4F6"), yaxis=dict(gridcolor="#F3F4F6"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'> Partner Directory</div>", unsafe_allow_html=True)
        st.dataframe(logistics, use_container_width=True, height=270)
        st.markdown("</div>", unsafe_allow_html=True)

elif page_key == "graph":
    show_graph(data, neo4j_svc)

elif page_key == "chatbot":
    show_chatbot(data, rag)
