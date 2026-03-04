import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.performance_engine import compute_performance

try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False

# Node palette — light-friendly but vivid
NODE_COLORS = {
    "Employee":   "#FF7A00",
    "Vendor":     "#4D96FF",
    "Department": "#8B5CF6",
    "Warehouse":  "#16A34A",
    "Logistics":  "#F59E0B",
    "Contract":   "#EC4899",
    "Region":     "#06B6D4",
}


def build_local_graph(data: dict):
    employees = compute_performance(data["employees"])
    vendors   = data["vendors"]
    logistics = data["logistics"]
    contracts = data["contracts"]

    net = Network(
        height="620px", width="100%",
        bgcolor="#F9FAFB",   # light background
        font_color="#1F2937",
        notebook=False,
    )
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {"springLength": 130, "gravitationalConstant": -80},
            "minVelocity": 0.6,
            "solver": "forceAtlas2Based"
        },
        "interaction": {"hover": true, "tooltipDelay": 150},
        "edges": {"smooth": {"type": "continuous"}, "color": {"inherit": false}}
    }
    """)

    added = set()

    def add_node(nid, label, group, title, size=20):
        if nid not in added:
            net.add_node(
                nid, label=label,
                color=NODE_COLORS.get(group, "#9CA3AF"),
                title=title, size=size,
                font={"color": "#1F2937", "size": 12, "strokeWidth": 2, "strokeColor": "#FFFFFF"},
                borderWidth=2,
                borderWidthSelected=3,
            )
            added.add(nid)

    for _, row in employees.iterrows():
        score = row["performance_score"]
        add_node(
            row["employee_id"], row["name"].split()[0], "Employee",
            f"👤 {row['name']}\n{row['role']}\nScore: {score:.1f} | {row['performance_tier']}",
            size=15 + score / 12,
        )
        dept_id = f"DEPT_{row['department']}"
        add_node(dept_id, row["department"], "Department", f"🏢 {row['department']}", size=28)
        net.add_edge(row["employee_id"], dept_id, color="#8B5CF666", title="BELONGS_TO", width=1.5)

        wh_id = f"WH_{row['warehouse']}"
        add_node(wh_id, row["warehouse"], "Warehouse", f"🏪 {row['warehouse']}", size=24)
        net.add_edge(row["employee_id"], wh_id, color="#16A34A55", title="WORKS_AT", width=1.5)

    for _, row in vendors.iterrows():
        add_node(
            row["vendor_id"], row["vendor_name"][:13], "Vendor",
            f"🏭 {row['vendor_name']}\nCategory: {row['category']}\nValue: ₹{row['contract_value']:,}",
            size=22,
        )
        reg_id = f"REG_{row['region']}"
        add_node(reg_id, row["region"], "Region", f"📍 {row['region']} Region", size=26)
        net.add_edge(row["vendor_id"], reg_id, color="#4D96FF55", title="OPERATES_IN", width=1.5)

    for _, row in logistics.iterrows():
        add_node(
            row["logistics_id"], row["partner_name"][:13], "Logistics",
            f"🚚 {row['partner_name']}\nShipments: {row['shipments_handled']}\nAvg: {row['avg_delivery_time']} min",
            size=20,
        )
        reg_id = f"REG_{row['region']}"
        add_node(reg_id, row["region"], "Region", f"📍 {row['region']} Region", size=26)
        net.add_edge(row["logistics_id"], reg_id, color="#F59E0B55", title="COVERS", width=1.5)

    for _, row in contracts.iterrows():
        vendor_match = vendors[vendors["vendor_name"] == row["vendor_name"]]
        if not vendor_match.empty:
            vid = vendor_match.iloc[0]["vendor_id"]
            cid = row["contract_id"]
            c   = "#16A34A" if row["status"] == "Active" else "#EF4444"
            add_node(
                cid, cid, "Contract",
                f"📄 {cid}\n{row['vendor_name']}\n₹{row['value']:,} | {row['status']}",
                size=14,
            )
            net.add_edge(cid, vid, color=c + "88", title=f"CONTRACT_{row['status']}", width=1.5)

    return net


def show_graph(data: dict, neo4j_service=None):
    # ── Page header
    st.markdown("""
    <div class="page-header">
        <div style="font-size:1.65rem; font-weight:800; color:#1F2937;">🕸️ Supply Chain Knowledge Graph</div>
        <div style="font-size:0.88rem; color:#9CA3AF; margin-top:4px; font-weight:500;">
            Interactive entity relationship visualization — hover nodes for details, drag to explore
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Legend
    st.markdown("<div class='page-card' style='padding:16px 22px;'>", unsafe_allow_html=True)
    legend_html = " &nbsp;&nbsp; ".join(
        f"<span class='legend-item'><span class='legend-dot' style='background:{c};'></span>{t}</span>"
        for t, c in NODE_COLORS.items()
    )
    st.markdown(
        f"<div style='display:flex; flex-wrap:wrap; gap:8px; align-items:center;'>"
        f"<span style='font-size:0.8rem; font-weight:700; color:#6B7280; margin-right:4px;'>Node Types:</span>"
        f"{legend_html}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not PYVIS_AVAILABLE:
        st.warning("⚠️ pyvis not installed. Run: `pip install pyvis`")
        return

    st.markdown("<div class='page-card' style='padding:12px;'>", unsafe_allow_html=True)

    if neo4j_service and neo4j_service.is_connected():
        st.markdown(
            "<div style='font-size:0.82rem; color:#16A34A; font-weight:600; padding:6px 8px;'>"
            "✅ Connected to Neo4j Aura — Live graph data</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='font-size:0.82rem; color:#F59E0B; font-weight:600; padding:6px 8px;'>"
            "ℹ️ Neo4j offline — Showing local graph</div>",
            unsafe_allow_html=True,
        )

    with st.spinner("Building knowledge graph..."):
        net = build_local_graph(data)
        
        tmp = os.path.join(tempfile.gettempdir(), "blinkit_graph_light.html")
        net.save_graph(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            html = f.read()
        # Patch the iframe background to match light mode
        html = html.replace(
            "body {",
            "body { background:#F9FAFB !important; color:#1F2937 !important; font-family:'Inter',sans-serif;",
        )

    components.html(html, height=640, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='page-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Graph Statistics</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Employee Nodes", len(data["employees"]), delta="Active")
    c2.metric("Vendor Nodes", len(data["vendors"]), delta="Mapped")
    c3.metric("Logistics Nodes", len(data["logistics"]), delta="Live")
    c4.metric("Contract Edges", len(data["contracts"]), delta="Tracked")
    st.markdown("</div>", unsafe_allow_html=True)
