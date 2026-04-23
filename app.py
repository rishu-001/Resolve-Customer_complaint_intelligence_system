import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from nlp_engine import ComplaintAnalyzer
from data_manager import DataManager

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Complaint Intelligence System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #0d0f14; color: #e8eaf0; }
.stApp { background-color: #0d0f14; }

.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00e5ff;
    letter-spacing: -1px;
    margin-bottom: 0;
}
.hero-sub {
    font-size: 1rem;
    color: #8892a4;
    margin-top: 4px;
    margin-bottom: 24px;
}

.card {
    background: #161b27;
    border: 1px solid #232b3e;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 8px;
}

.metric-val {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.urgency-critical { background: #ff1744; color: white; }
.urgency-high     { background: #ff6d00; color: white; }
.urgency-medium   { background: #ffd600; color: #111; }
.urgency-low      { background: #00c853; color: white; }

.result-box {
    background: #0d1520;
    border: 1px solid #1e2d45;
    border-left: 4px solid #00e5ff;
    border-radius: 8px;
    padding: 20px;
    margin-top: 16px;
}
.result-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a5568;
}
.result-value {
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 4px;
}

.stTextArea textarea {
    background: #161b27 !important;
    border: 1px solid #232b3e !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00e5ff, #0070f3) !important;
    color: #0d0f14 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 1px !important;
    padding: 10px 28px !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,229,255,0.3) !important;
}

.sidebar .sidebar-content { background: #0d0f14; }
[data-testid="stSidebar"] { background: #111520 !important; border-right: 1px solid #1e2535; }

.history-item {
    background: #161b27;
    border: 1px solid #232b3e;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    cursor: pointer;
}
.history-item:hover { border-color: #00e5ff44; }

div[data-testid="metric-container"] {
    background: #161b27;
    border: 1px solid #232b3e;
    border-radius: 12px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Init ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_engine():
    return ComplaintAnalyzer()

@st.cache_resource
def load_data_manager():
    return DataManager()

analyzer = load_engine()
dm = load_data_manager()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 CIS Dashboard")
    st.markdown("---")
    page = st.radio("Navigation", ["Analyze Complaint", "Dashboard & Insights", "Batch Upload", "History"])
    st.markdown("---")
    stats = dm.get_stats()
    st.markdown(f"**Total Analyzed:** {stats['total']}")
    st.markdown(f"**Critical Today:** {stats['critical_today']}")
    st.markdown(f"**Top Category:** {stats['top_category']}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — ANALYZE
# ─────────────────────────────────────────────────────────────────────────────
if page == "Analyze Complaint":
    st.markdown('<div class="hero-title">🧠 Complaint Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI-powered complaint categorization, urgency detection & action routing</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        complaint_text = st.text_area(
            "Paste customer complaint here",
            height=180,
            placeholder="e.g. I have been charged twice for my order #12345 and nobody is responding to my emails. This is absolutely unacceptable..."
        )

        customer_id = st.text_input("Customer ID (optional)", placeholder="CUST-001")
        channel = st.selectbox("Channel", ["Email", "Chat", "Phone", "Social Media", "App Review"])

        analyze_btn = st.button("⚡ ANALYZE COMPLAINT", use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Quick Examples")
        examples = {
            "💳 Payment Issue": "I was charged twice for my subscription this month and I want an immediate refund. My account number is 4521. This is the third time this has happened!",
            "📦 Delivery Problem": "My order was supposed to arrive 5 days ago and it still hasn't shown up. I have a wedding this weekend and I needed this package urgently.",
            "🔧 Technical Bug": "Your app keeps crashing every time I try to checkout. I've lost my cart 3 times already. Very frustrating experience.",
            "👎 Poor Service": "The customer support agent was rude and hung up on me without resolving my issue. I've been a loyal customer for 5 years.",
        }
        for label, text in examples.items():
            if st.button(label, use_container_width=True):
                st.session_state["example_text"] = text
                st.rerun()

        if "example_text" in st.session_state:
            complaint_text = st.session_state["example_text"]

    # ── Results ───────────────────────────────────────────────────────────────
    if analyze_btn and complaint_text.strip():
        with st.spinner("Analyzing..."):
            result = analyzer.analyze(complaint_text)
            dm.save_complaint(complaint_text, result, customer_id, channel)

        st.markdown("---")
        st.markdown("### 📊 Analysis Result")

        c1, c2, c3, c4 = st.columns(4)
        urgency_colors = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        c1.metric("Category", result["category"])
        c2.metric("Urgency", f"{urgency_colors.get(result['urgency'], '')} {result['urgency']}")
        c3.metric("Sentiment", result["sentiment"])
        c4.metric("Confidence", f"{result['confidence']}%")

        st.markdown('<div class="result-box">', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="result-label">Suggested Action</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-value">⚡ {result["action"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="result-label" style="margin-top:16px">Department</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-value">🏢 {result["department"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="result-label" style="margin-top:16px">Response SLA</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-value">⏱ {result["sla"]}</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="result-label">Key Issues Detected</div>', unsafe_allow_html=True)
            for issue in result["key_issues"]:
                st.markdown(f"• {issue}")

            st.markdown('<div class="result-label" style="margin-top:16px">Labels</div>', unsafe_allow_html=True)
            labels_html = " ".join([f'<span style="background:#1e2d45;padding:3px 10px;border-radius:20px;font-size:0.8rem;margin:2px">{l}</span>' for l in result["labels"]])
            st.markdown(labels_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Suggested reply
        with st.expander("✉️ Suggested Customer Reply"):
            st.text_area("", value=result["suggested_reply"], height=120)

    elif analyze_btn:
        st.warning("Please enter a complaint to analyze.")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Dashboard & Insights":
    st.markdown('<div class="hero-title">📊 Insights Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Real-time analytics across all analyzed complaints</div>', unsafe_allow_html=True)

    df = dm.get_dataframe()

    if df.empty:
        st.info("No complaints analyzed yet. Go to 'Analyze Complaint' to get started!")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Complaints", len(df))
        c2.metric("Critical", len(df[df["urgency"] == "Critical"]))
        c3.metric("Avg Confidence", f"{df['confidence'].mean():.0f}%")
        c4.metric("Categories Found", df["category"].nunique())

        col1, col2 = st.columns(2)

        with col1:
            cat_counts = df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig = px.bar(cat_counts, x="Count", y="Category", orientation="h",
                        color="Count", color_continuous_scale=["#1e2d45", "#00e5ff"],
                        title="Complaints by Category")
            fig.update_layout(paper_bgcolor="#161b27", plot_bgcolor="#161b27",
                             font_color="#e8eaf0", title_font_color="#00e5ff",
                             showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            urg_counts = df["urgency"].value_counts().reset_index()
            urg_counts.columns = ["Urgency", "Count"]
            colors = {"Critical": "#ff1744", "High": "#ff6d00", "Medium": "#ffd600", "Low": "#00c853"}
            fig2 = px.pie(urg_counts, values="Count", names="Urgency",
                         color="Urgency", color_discrete_map=colors,
                         title="Urgency Distribution", hole=0.4)
            fig2.update_layout(paper_bgcolor="#161b27", plot_bgcolor="#161b27",
                              font_color="#e8eaf0", title_font_color="#00e5ff")
            st.plotly_chart(fig2, use_container_width=True)

        # Sentiment over time
        if len(df) > 2:
            fig3 = px.scatter(df, x="timestamp", y="confidence", color="sentiment",
                             size="confidence", hover_data=["category", "urgency"],
                             title="Confidence & Sentiment Over Time",
                             color_discrete_map={"Negative": "#ff1744", "Neutral": "#ffd600", "Positive": "#00c853"})
            fig3.update_layout(paper_bgcolor="#161b27", plot_bgcolor="#161b27",
                              font_color="#e8eaf0", title_font_color="#00e5ff")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 🗂 Recent Complaints")
        display_df = df[["timestamp", "category", "urgency", "sentiment", "confidence", "action"]].tail(10).iloc[::-1]
        st.dataframe(display_df, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — BATCH
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Batch Upload":
    st.markdown('<div class="hero-title">📁 Batch Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload a CSV of complaints for bulk processing</div>', unsafe_allow_html=True)

    st.markdown("**CSV Format:** Must have a column named `complaint` (optional: `customer_id`, `channel`)")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        df_input = pd.read_csv(uploaded)
        st.write(f"✅ Loaded **{len(df_input)}** rows")
        st.dataframe(df_input.head())

        if "complaint" not in df_input.columns:
            st.error("CSV must have a 'complaint' column!")
        else:
            if st.button("⚡ RUN BATCH ANALYSIS", use_container_width=True):
                results = []
                bar = st.progress(0)
                status = st.empty()
                for i, row in df_input.iterrows():
                    status.text(f"Analyzing complaint {i+1}/{len(df_input)}...")
                    r = analyzer.analyze(str(row["complaint"]))
                    r["complaint"] = row["complaint"]
                    r["customer_id"] = row.get("customer_id", "")
                    results.append(r)
                    bar.progress((i + 1) / len(df_input))

                results_df = pd.DataFrame(results)
                st.success(f"✅ Analyzed {len(results_df)} complaints!")
                st.dataframe(results_df[["complaint", "category", "urgency", "sentiment", "action", "confidence"]])

                csv = results_df.to_csv(index=False)
                st.download_button("⬇️ Download Results CSV", csv, "complaint_analysis_results.csv", "text/csv")

    else:
        # Sample CSV
        sample = pd.DataFrame({
            "complaint": [
                "I was double charged and want my money back immediately!",
                "The delivery is 3 days late. Please update me.",
                "Your app crashes on checkout every single time."
            ],
            "customer_id": ["C001", "C002", "C003"],
            "channel": ["Email", "Chat", "App Review"]
        })
        st.markdown("#### 📄 Sample CSV Format")
        st.dataframe(sample)
        csv = sample.to_csv(index=False)
        st.download_button("⬇️ Download Sample CSV", csv, "sample_complaints.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — HISTORY
# ─────────────────────────────────────────────────────────────────────────────
elif page == "History":
    st.markdown('<div class="hero-title">🕑 Complaint History</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Browse and filter all past analyses</div>', unsafe_allow_html=True)

    df = dm.get_dataframe()

    if df.empty:
        st.info("No history yet.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            cat_filter = st.multiselect("Category", options=df["category"].unique(), default=list(df["category"].unique()))
        with col2:
            urg_filter = st.multiselect("Urgency", options=df["urgency"].unique(), default=list(df["urgency"].unique()))
        with col3:
            sent_filter = st.multiselect("Sentiment", options=df["sentiment"].unique(), default=list(df["sentiment"].unique()))

        filtered = df[df["category"].isin(cat_filter) & df["urgency"].isin(urg_filter) & df["sentiment"].isin(sent_filter)]
        st.markdown(f"Showing **{len(filtered)}** records")

        for _, row in filtered.iloc[::-1].iterrows():
            urgency_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(row["urgency"], "⚪")
            with st.expander(f"{urgency_emoji} [{row['category']}] {row['complaint_text'][:80]}..."):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Urgency:** {row['urgency']}")
                c2.markdown(f"**Sentiment:** {row['sentiment']}")
                c3.markdown(f"**Confidence:** {row['confidence']}%")
                st.markdown(f"**Action:** {row['action']}")
                st.markdown(f"**Timestamp:** {row['timestamp']}")
                st.markdown(f"**Full text:** {row['complaint_text']}")
