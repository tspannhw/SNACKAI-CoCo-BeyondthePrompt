"""
NEXUS-7 // Beyond the Prompt: Enterprise AI Demo
Tim Spann | NYC AI Meetup | March 2026
"""

import streamlit as st
import snowflake.connector
import os
import pandas as pd
import plotly.graph_objects as go
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

st.set_page_config(
    page_title="NEXUS-7 // Enterprise AI",
    page_icon="🔺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BLADE_RUNNER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
.stApp { background: linear-gradient(180deg, #0a0a0f 0%, #1a0a1a 50%, #0a1a1a 100%); }
h1, h2, h3 { font-family: 'Orbitron', monospace !important; text-transform: uppercase; letter-spacing: 3px; }
h1 { color: #00fff9 !important; text-shadow: 0 0 10px #00fff9; }
h2 { color: #ff00ff !important; text-shadow: 0 0 10px #ff00ff; }
h3 { color: #ff6600 !important; }
.stMetric { background: rgba(0,255,249,0.1); border: 1px solid #00fff9; padding: 15px; }
.stMetric label { font-family: 'Orbitron', monospace !important; color: #ff00ff !important; }
.stMetric [data-testid="stMetricValue"] { font-family: 'Share Tech Mono', monospace !important; color: #00fff9 !important; }
.stButton > button { font-family: 'Orbitron', monospace !important; background: #1a0a2e !important; border: 2px solid #00fff9 !important; color: #00fff9 !important; }
code { font-family: 'Share Tech Mono', monospace !important; background: rgba(0,255,249,0.1) !important; color: #00fff9 !important; }
</style>
"""
st.markdown(BLADE_RUNNER_CSS, unsafe_allow_html=True)


def get_private_key_bytes():
    """Load and return private key as DER bytes."""
    key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def get_connection():
    """Create new Snowflake connection."""
    return snowflake.connector.connect(
        account="SFSENORTHAMERICA-TSPANN-AWS1",
        user="kafkaguy",
        private_key=get_private_key_bytes(),
        role="ACCOUNTADMIN",
        warehouse="INGEST",
        database="DEMO",
        schema="DEMO"
    )


def run_query(sql):
    """Execute SQL and return DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


st.markdown('<div style="text-align:center;padding:20px;"><p style="font-family:monospace;color:#ff00ff;letter-spacing:5px;">TYRELL CORPORATION // NEXUS DIVISION // 2026</p></div>', unsafe_allow_html=True)
st.title("NEXUS-7 BEYOND THE PROMPT")
st.markdown("**ENTERPRISE AI** // OPERATOR: TIM SPANN")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["NEXUS CORE", "AI CORTEX", "SEMANTIC GRID", "MULTI-VERSE", "ORACLE"])

with tab1:
    st.header("NEXUS CORE SYSTEMS")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### BASELINE\n| CHATBOT | NEXUS-7 |\n|---------|----------|\n| Generic | YOUR data |\n| No gov | Full RBAC |\n| Isolated | Integrated |")
    with col2:
        st.markdown("### FOUR CORES\n1. **CORTEX AI FUNCTIONS**\n2. **SEMANTIC VIEWS**\n3. **CORTEX AGENTS**\n4. **MCP PROTOCOL**")
    
    st.divider()
    st.subheader("LIVE TELEMETRY")
    try:
        df = run_query("SELECT COUNT(DISTINCT PLANEID) aircraft, COUNT(DISTINCT FLIGHT) flights, ROUND(AVG(TRY_CAST(ALTBARO AS NUMBER))) avg_alt, ROUND(AVG(TRY_CAST(GS AS NUMBER))) avg_spd FROM DEMO.DEMO.ADSB WHERE SEEN_POS IS NOT NULL")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AIRCRAFT", int(df['AIRCRAFT'].iloc[0]))
        c2.metric("FLIGHTS", int(df['FLIGHTS'].iloc[0]))
        c3.metric("AVG ALT", f"{int(df['AVG_ALT'].iloc[0]):,} ft")
        c4.metric("AVG SPD", f"{int(df['AVG_SPD'].iloc[0]):,} kts")
        st.success("TELEMETRY ONLINE")
    except Exception as e:
        st.error(f"ERROR: {e}")

with tab2:
    st.header("CORTEX AI FUNCTIONS")
    demo = st.selectbox("SELECT FUNCTION", ["SENTIMENT", "CLASSIFY", "SUMMARIZE"])
    
    if demo == "SENTIMENT":
        txt = st.text_area("INPUT:", "Flight experiencing turbulence, passengers secure.")
        if st.button("ANALYZE"):
            with st.spinner("Processing..."):
                r = run_query(f"SELECT AI_SENTIMENT('{txt.replace(chr(39), chr(39)+chr(39))}') as s")
                st.json(r['S'].iloc[0])
    elif demo == "CLASSIFY":
        if st.button("CLASSIFY SQUAWKS"):
            with st.spinner("Classifying..."):
                r = run_query("SELECT sq, ds, AI_CLASSIFY('Squawk '||sq||': '||ds, ['normal','radio_failure','hijack','emergency']):label::STRING cl FROM (SELECT '7700' sq,'Emergency' ds UNION ALL SELECT '7600','Radio failure' UNION ALL SELECT '1200','VFR standard')")
                st.dataframe(r)
    elif demo == "SUMMARIZE":
        txt = st.text_area("INPUT:", "Boeing 737 had hydraulic warnings. Captain declared emergency. Landed safely.")
        if st.button("SUMMARIZE"):
            with st.spinner("Summarizing..."):
                r = run_query(f"SELECT AI_COMPLETE('claude-3-5-sonnet','Summarize: {txt.replace(chr(39), chr(39)+chr(39))}') as s")
                st.info(r['S'].iloc[0])

with tab3:
    st.header("SEMANTIC GRID")
    if st.button("QUERY SEMANTIC VIEW"):
        with st.spinner("Querying..."):
            try:
                r = run_query("SELECT sv.total_aircraft, sv.total_flights, sv.avg_altitude, sv.avg_ground_speed FROM SEMANTIC_VIEW(DEMO.DEMO.adsb_flight_tracking METRICS total_aircraft, total_flights, avg_altitude, avg_ground_speed) AS sv")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("AIRCRAFT", int(r['TOTAL_AIRCRAFT'].iloc[0]))
                c2.metric("FLIGHTS", int(r['TOTAL_FLIGHTS'].iloc[0]))
                c3.metric("AVG ALT", f"{int(r['AVG_ALTITUDE'].iloc[0]):,}")
                c4.metric("AVG SPD", f"{int(r['AVG_GROUND_SPEED'].iloc[0]):,}")
                st.success("SEMANTIC TRANSLATION COMPLETE")
            except Exception as e:
                st.error(f"Error: {e}")
    if st.button("RAW DATA"):
        r = run_query("SELECT FLIGHT, ALTBARO, GS, SQUAWK FROM DEMO.DEMO.ADSB WHERE FLIGHT IS NOT NULL LIMIT 8")
        st.dataframe(r)

with tab4:
    st.header("MULTI-VERSE")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("FLIGHTS")
        try:
            st.dataframe(run_query("SELECT FLIGHT, ALTBARO, GS FROM DEMO.DEMO.ADSB WHERE FLIGHT IS NOT NULL LIMIT 8"), height=250)
        except Exception as e:
            st.error(str(e))
    with c2:
        st.subheader("CRYPTO")
        try:
            st.dataframe(run_query("SELECT TIMESTAMP, ROUND(CLOSE,2) BTC FROM DEMO.DEMO.FINANCIAL ORDER BY TIMESTAMP DESC LIMIT 8"), height=250)
        except Exception as e:
            st.error(str(e))
    st.subheader("BTC CHART")
    try:
        df = run_query("SELECT TIMESTAMP, CLOSE FROM DEMO.DEMO.FINANCIAL ORDER BY TIMESTAMP DESC LIMIT 30")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['TIMESTAMP'], y=df['CLOSE'], name='BTC', line=dict(color='#00fff9')))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), height=300)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("Chart unavailable")

with tab5:
    st.header("ORACLE")
    if st.button("GENERATE INSIGHT"):
        with st.spinner("Oracle processing..."):
            try:
                r = run_query("SELECT AI_COMPLETE('claude-3-5-sonnet','You are NEXUS-7. Based on: '||total_aircraft::STRING||' aircraft, '||ROUND(avg_alt)::STRING||' ft avg. Give 2-sentence insight.') insight FROM (SELECT COUNT(DISTINCT PLANEID) total_aircraft, AVG(TRY_CAST(ALTBARO AS NUMBER)) avg_alt FROM DEMO.DEMO.ADSB WHERE SEEN_POS IS NOT NULL)")
                st.success(r['INSIGHT'].iloc[0])
            except Exception as e:
                st.error(str(e))
    st.markdown("| CAPABILITY | ADVANTAGE |\n|------------|----------|\n| AI FUNCTIONS | Zero data movement |\n| SEMANTIC VIEWS | Business precision |\n| CORTEX AGENTS | Autonomous reasoning |\n| GOVERNANCE | Full audit trail |")

st.divider()
st.markdown('<div style="text-align:center;"><p style="color:#ff00ff;">NEXUS-7 // TIM SPANN // @PaaSDev</p><p style="color:#444;">"MORE HUMAN THAN HUMAN"</p></div>', unsafe_allow_html=True)
