import streamlit as st
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.performance_engine import compute_performance

TIER_COLORS = {
    "Elite": "#FF7A00",
    "High": "#4D96FF",
    "Moderate": "#F59E0B",
    "Needs Improvement": "#EF4444",
}
TIER_BG = {
    "Elite": "#FFF4EC",
    "High": "#EFF6FF",
    "Moderate": "#FFFBEB",
    "Needs Improvement": "#FEF2F2",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FAFBFC",
    font=dict(color="#374151", family="Inter"),
    xaxis=dict(gridcolor="#F3F4F6", zerolinecolor="#F3F4F6"),
    yaxis=dict(gridcolor="#F3F4F6", zerolinecolor="#F3F4F6"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151")),
    margin=dict(l=10, r=10, t=36, b=10),
)


def show_employees(data: dict):
    employees = data["employees"]
    scored = compute_performance(employees)

    # ── Page header
    st.markdown("""
    <div class="page-header">
        <div style="font-size:1.65rem; font-weight:800; color:#1F2937;"> Employee Performance Hub</div>
        <div style="font-size:0.88rem; color:#9CA3AF; margin-top:4px; font-weight:500;">
            Leaderboard, tier analysis, and delivery metrics across all departments
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary KPIs
    s = scored
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Employees", len(s))
    col2.metric("Elite Performers", len(s[s["performance_tier"] == "Elite"]))
    col3.metric("Avg Score", f"{s['performance_score'].mean():.1f}")
    col4.metric("Avg OTD Rate", f"{(s['on_time_delivery_rate'].mean()*100):.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters
    st.markdown("<div class='page-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)
    with fc1:
        departments = ["All"] + sorted(scored["department"].unique().tolist())
        selected_dept = st.selectbox("Department", departments)
    with fc2:
        tiers = ["All"] + sorted(scored["performance_tier"].unique().tolist())
        selected_tier = st.selectbox("Performance Tier", tiers)
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = scored.copy()
    if selected_dept != "All":
        filtered = filtered[filtered["department"] == selected_dept]
    if selected_tier != "All":
        filtered = filtered[filtered["performance_tier"] == selected_tier]
    filtered = filtered.sort_values("performance_score", ascending=False).reset_index(drop=True)

    # ── Leaderboard
    st.markdown("<div class='page-card'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='section-title'>Performance Leaderboard "
        f"<span style='font-weight:400; font-size:0.82rem; color:#9CA3AF;'>({len(filtered)} employees)</span></div>",
        unsafe_allow_html=True,
    )

    for i, row in filtered.iterrows():
        rank = i + 1
        color = TIER_COLORS.get(row["performance_tier"], "#888")
        bg    = TIER_BG.get(row["performance_tier"], "#F9FAFB")
        medal = "" if rank == 1 else "🥈" if rank == 2 else "" if rank == 3 else f"#{rank}"
        bar_w = int(row["performance_score"])

        st.markdown(
            f"""
            <div class="leader-row" style="border-left: 4px solid {color};">
                <span style="font-size:1.25rem; width:44px; flex-shrink:0;">{medal}</span>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:700; font-size:0.95rem; color:#1F2937;
                                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        {row['name']}
                    </div>
                    <div style="font-size:0.78rem; color:#6B7280; margin-top:1px;">
                        {row['role']} &nbsp;·&nbsp; {row['department']} &nbsp;·&nbsp;  {row['warehouse']}
                    </div>
                    <div style="background:#F3F4F6; border-radius:4px; height:4px; margin-top:6px; width:100%;">
                        <div style="background:{color}; border-radius:4px; height:4px; width:{bar_w}%;"></div>
                    </div>
                </div>
                <div style="text-align:right; margin-left:16px; flex-shrink:0;">
                    <div style="background:{bg}; color:{color}; border:1px solid {color}33;
                                padding:4px 12px; border-radius:20px;
                                font-size:0.82rem; font-weight:700; white-space:nowrap;">
                        {row['badge']}
                    </div>
                    <div style="font-size:0.78rem; color:#9CA3AF; margin-top:3px;">
                        {row['performance_score']:.1f} / 100
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts row
    ca, cb = st.columns(2)

    with ca:
        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Score Distribution</div>", unsafe_allow_html=True)
        fig = px.histogram(
            filtered, x="performance_score", nbins=10,
            color="performance_tier", color_discrete_map=TIER_COLORS,
        )
        fig.update_layout(**{**PLOT_LAYOUT, "height": 280, "showlegend": True})
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with cb:
        st.markdown("<div class='page-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Projects vs Clients Managed</div>", unsafe_allow_html=True)
        fig2 = px.scatter(
            filtered, x="projects_handled", y="clients_managed",
            color="performance_tier", size="performance_score",
            hover_name="name", color_discrete_map=TIER_COLORS, size_max=28,
            labels={"projects_handled": "Projects", "clients_managed": "Clients"},
        )
        fig2.update_layout(**{**PLOT_LAYOUT, "height": 280})
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── OTD bar
    st.markdown("<div class='page-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'> On-Time Delivery Rate by Department</div>", unsafe_allow_html=True)
    dept_delivery = filtered.groupby("department")["on_time_delivery_rate"].mean().reset_index()
    dept_delivery.columns = ["Department", "Avg OTD Rate"]
    dept_delivery["Pct"] = (dept_delivery["Avg OTD Rate"] * 100).round(2)
    fig3 = px.bar(
        dept_delivery, x="Department", y="Pct",
        color="Pct", color_continuous_scale=["#FFE4CC","#FF7A00","#CC5200"],
        text="Pct",
        labels={"Pct": "Avg OTD Rate (%)"},
    )
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0)
    fig3.update_layout(**{**PLOT_LAYOUT, "height": 320}, yaxis_range=[0, 108])
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Raw data expander
    with st.expander("Full Employee Data Table"):
        st.dataframe(
            filtered[["employee_id","name","department","role","warehouse",
                       "projects_handled","clients_managed","tasks_completed",
                       "on_time_delivery_rate","performance_score","badge"]],
            use_container_width=True,
            height=300,
        )
