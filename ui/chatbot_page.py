import streamlit as st
import pandas as pd
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.rag_pipeline import RAGPipeline
from services.performance_engine import compute_performance

QUICK_PROMPTS = [
    "Which region has the most vendors?",
    "Which employees need improvement?"
]


def build_df_context(data: dict) -> str:
    employees = compute_performance(data["employees"])
    vendors   = data["vendors"]
    logistics = data["logistics"]
    contracts = data["contracts"]

    top_emp      = employees.loc[employees["performance_score"].idxmax()]
    top_vendor   = vendors.loc[vendors["contract_value"].idxmax()]
    top_logistics = logistics.loc[logistics["shipments_handled"].idxmax()]
    active_contracts = contracts[contracts["status"] == "Active"]

    context = f"""
EMPLOYEE SUMMARY ({len(employees)} total):
- Top Performer: {top_emp['name']} ({top_emp['role']}, {top_emp['department']}) - Score: {top_emp['performance_score']:.1f}
- Elite tier: {len(employees[employees['performance_tier']=='Elite'])} employees
- High tier: {len(employees[employees['performance_tier']=='High'])} employees
- Departments: {', '.join(employees['department'].unique())}
- Warehouses: {', '.join(employees['warehouse'].unique())}
- Avg on-time delivery: {(employees['on_time_delivery_rate'].mean()*100):.1f}%

VENDOR SUMMARY ({len(vendors)} total):
- Highest value vendor: {top_vendor['vendor_name']} (₹{top_vendor['contract_value']:,}, {top_vendor['category']})
- Total contract value: ₹{vendors['contract_value'].sum():,}
- Categories: {', '.join(vendors['category'].unique())}
- Regions: {', '.join(vendors['region'].unique())}

LOGISTICS SUMMARY ({len(logistics)} total):
- Busiest partner: {top_logistics['partner_name']} ({top_logistics['shipments_handled']} shipments)
- Best avg delivery time: {logistics['avg_delivery_time'].min()} min

CONTRACTS ({len(contracts)} total):
- Active: {len(active_contracts)} contracts worth ₹{active_contracts['value'].sum():,}
- Expired: {len(contracts[contracts['status']=='Expired'])} contracts

FULL EMPLOYEE LIST:
{employees[['name','department','role','warehouse','performance_score','performance_tier']].to_string(index=False)}

FULL VENDOR LIST:
{vendors[['vendor_name','category','contract_value','region']].to_string(index=False)}

FULL LOGISTICS LIST:
{logistics[['partner_name','region','shipments_handled','avg_delivery_time']].to_string(index=False)}
"""
    return context.strip()


def show_chatbot(data: dict, rag_pipeline: RAGPipeline):
    # ── Page header
    st.markdown("""
    <div class="page-header">
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="background:linear-gradient(135deg,#FF7A00,#FF9A3C); border-radius:14px;
                        width:52px; height:52px; display:flex; align-items:center;
                        justify-content:center; font-size:1.6rem; flex-shrink:0;"></div>
            <div>
                <div style="font-size:1.6rem; font-weight:800; color:#1F2937; line-height:1.1;">
                    BlinkBot — AI Supply Chain Assistant
                </div>
                <div style="font-size:0.88rem; color:#9CA3AF; margin-top:4px; font-weight:500;">
                    Ask anything about employees, vendors, logistics, and contracts &nbsp;·&nbsp;
                    <span style="color:#16A34A; font-weight:600;"> RAG Active</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Init session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm **BlinkBot**, your Blinkit Supply Chain AI. Ask me anything about your employees, vendors, logistics partners, or contracts. I'm powered by Groq LLM + RAG for accurate, context-aware answers.",
                "time": datetime.datetime.now().strftime("%H:%M"),
            }
        ]
    if "df_context" not in st.session_state:
        st.session_state.df_context = build_df_context(data)

    # ── Quick prompts
    st.markdown("<div class='section-title'> Quick Questions</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, prompt in enumerate(QUICK_PROMPTS):
        with cols[i % 4]:
            if st.button(prompt, key=f"qp_{i}", use_container_width=True):
                ts = datetime.datetime.now().strftime("%H:%M")
                st.session_state.messages.append({"role": "user", "content": prompt, "time": ts})
                with st.spinner("BlinkBot is thinking..."):
                    resp = rag_pipeline.query_with_dataframe_context(
                        prompt, st.session_state.df_context
                    )
                st.session_state.messages.append({"role": "assistant", "content": resp, "time": ts})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Chat window
    st.markdown("<div class='section-title'> Conversation</div>", unsafe_allow_html=True)

    # Render all messages
    for msg in st.session_state.messages:
        ts = msg.get("time", "")
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-user">
                    <div class="chat-user-label">You</div>
                    {msg['content']}
                    <div class="chat-ts">{ts}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Render markdown content safely
            content_escaped = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            # Restore markdown-style bold
            import re
            content_escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_escaped)
            content_escaped = content_escaped.replace("\n", "<br>")
            st.markdown(
                f"""
                <div class="chat-bot">
                    <div class="chat-bot-label"> BlinkBot</div>
                    {content_escaped}
                    <div class="chat-ts">{ts}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Input area
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            user_input = st.text_input(
                "Message",
                placeholder="type here...",
                label_visibility="collapsed",
            )
        with c2:
            submitted = st.form_submit_button(
                "Send ",
                use_container_width=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted and user_input.strip():
        ts = datetime.datetime.now().strftime("%H:%M")
        st.session_state.messages.append({"role": "user", "content": user_input, "time": ts})
        with st.spinner(" BlinkBot is analyzing..."):
            resp = rag_pipeline.query_with_dataframe_context(
                user_input, st.session_state.df_context
            )
        st.session_state.messages.append({"role": "assistant", "content": resp, "time": ts})
        st.rerun()

    # ── Footer controls
    col_a, col_b, _ = st.columns([1, 1, 4])
    with col_a:
        if st.button(" Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Chat cleared. How can I help you?",
                    "time": datetime.datetime.now().strftime("%H:%M"),
                }
            ]
            rag_pipeline.reset_history()
            st.rerun()
    with col_b:
        msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(
            f"<div style='padding:8px 12px; background:#F9FAFB; border:1px solid #E8EAF0; "
            f"border-radius:10px; font-size:0.82rem; color:#6B7280; font-weight:600; text-align:center;'>"
            f" {msg_count} message{'s' if msg_count != 1 else ''}</div>",
            unsafe_allow_html=True,
        )
