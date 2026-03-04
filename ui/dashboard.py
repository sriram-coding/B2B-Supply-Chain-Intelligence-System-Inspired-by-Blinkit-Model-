import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.performance_engine import compute_performance, get_top_performer

# Light-mode Plotly theme shared across all charts
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FAFBFC",
    font=dict(color="#374151", family="Inter"),
    xaxis=dict(gridcolor="#F3F4F6", zerolinecolor="#F3F4F6"),
    yaxis=dict(gridcolor="#F3F4F6", zerolinecolor="#F3F4F6"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151")),
    margin=dict(l=10, r=10, t=36, b=10),
)

TIER_COLORS = {
    "Elite": "#FF7A00",
    "High": "#4D96FF",
    "Moderate": "#F59E0B",
    "Needs Improvement": "#EF4444",
}


def render_kpi_card(label, value, icon, accent):
    st.markdown(
        f"""
        <div class="kpi-card" style="border-top: 3px solid {accent};">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value" style="color:{accent};">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_dashboard(data: dict):
    # ── Page Header
    st.markdown("""
    <div class="page-header">
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="background:linear-gradient(135deg,#FF7A00,#FF9A3C); border-radius:14px;
                        width:52px; height:52px; display:flex; align-items:center;
                        justify-content:center; font-size:1.6rem; flex-shrink:0;"></div>
            <div>
                <div style="font-size:1.6rem; font-weight:800; color:#1F2937; line-height:1.1;">
                    Blinkit Supply Chain Intelligence
                </div>
                <div style="font-size:0.88rem; color:#9CA3AF; margin-top:4px; font-weight:500;">
                    Real-time operations overview · Today's snapshot
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    employees = data["employees"]
    vendors   = data["vendors"]
    contracts = data["contracts"]
    logistics = data["logistics"]

    scored_emp     = compute_performance(employees)
    top            = get_top_performer(employees)
    active_contracts = contracts[contracts["status"] == "Active"].shape[0]
    warehouses     = employees["warehouse"].nunique()

    # ── KPI Row
    kpis = [
        ("Total Employees",   len(employees),     "", "#FF7A00"),
        ("Total Vendors",     len(vendors),        "", "#4D96FF"),
        ("Active Contracts",  active_contracts,    "", "#16A34A"),
        ("Warehouses",        warehouses,          "", "#8B5CF6"),
        ("Logistics Partners",len(logistics),      "", "#F59E0B"),
        ("Top Performer",     top["name"].split()[0], "", "#EC4899"),
    ]
    cols = st.columns(6)
    for col, (label, value, icon, accent) in zip(cols, kpis):
        with col:
            render_kpi_card(label, value, icon, accent)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Pie + Bar
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'> Performance Tier Distribution</div>", unsafe_allow_html=True)
        tier_counts = scored_emp["performance_tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Count"]
        fig = px.pie(
            tier_counts, values="Count", names="Tier",
            color="Tier", color_discrete_map=TIER_COLORS, hole=0.52,
        )
        fig.update_traces(textposition="outside", textfont_color="#374151")
        fig.update_layout(**{**PLOT_LAYOUT, "height": 300, "showlegend": True})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Vendors by Region</div>", unsafe_allow_html=True)
        region_counts = vendors["region"].value_counts().reset_index()
        region_counts.columns = ["Region", "Count"]
        fig2 = px.bar(
            region_counts, x="Region", y="Count",
            color="Region",
            color_discrete_sequence=["#FF7A00","#4D96FF","#16A34A","#8B5CF6","#F59E0B"],
        )
        fig2.update_layout(**{**PLOT_LAYOUT, "height": 300, "showlegend": False})
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Logistics bar + Contract pie
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Top Logistics Partners by Shipments</div>", unsafe_allow_html=True)
        top_log = data["logistics"].nlargest(6, "shipments_handled")
        fig3 = px.bar(
            top_log, x="partner_name", y="shipments_handled",
            color="avg_delivery_time", color_continuous_scale="RdYlGn_r",
            labels={"partner_name": "", "shipments_handled": "Shipments", "avg_delivery_time": "Avg Time (min)"},
        )
        fig3.update_layout(**{**PLOT_LAYOUT, "height": 300})
        fig3.update_traces(marker_line_width=0)
        fig3.update_xaxes(tickangle=-28, tickfont=dict(size=11))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Contract Value by Status</div>", unsafe_allow_html=True)
        contracts["value"] = pd.to_numeric(contracts["value"], errors="coerce")
        contract_summary = contracts.groupby("status")["value"].sum().reset_index()
        fig4 = px.pie(
            contract_summary, values="value", names="status",
            color_discrete_sequence=["#16A34A", "#EF4444"],
            hole=0.5,
        )
        fig4.update_traces(textposition="outside", textfont_color="#374151")
        fig4.update_layout(**{**PLOT_LAYOUT, "height": 300})
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 3: Scatter bubble
    st.markdown("<div class='page-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Department Headcount vs Avg Performance Score</div>", unsafe_allow_html=True)
    dept_stats = scored_emp.groupby("department").agg(
        Headcount=("employee_id", "count"),
        Avg_Score=("performance_score", "mean"),
    ).reset_index()
    fig5 = px.scatter(
        dept_stats, x="Headcount", y="Avg_Score", text="department",
        size="Headcount", color="Avg_Score",
        color_continuous_scale=["#FFE4CC","#FF7A00","#CC5200"],
        size_max=65,
        labels={"Avg_Score": "Avg Performance Score", "Headcount": "Headcount"},
    )
    fig5.update_traces(textposition="top center", textfont=dict(color="#374151", size=11))
    fig5.update_layout(**{**PLOT_LAYOUT, "height": 380})
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
