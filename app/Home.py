"""
GrowMate - app/Home.py
"Know your soil. Grow your future."

Main landing page. Launch with:
  streamlit run app/Home.py
  OR
  python run.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils import inject_css, render_sidebar

st.set_page_config(
    page_title="GrowMate - Know Your Soil",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()
render_sidebar("Home")

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gm-hero">
    <h1>🌱 GrowMate</h1>
    <p><strong>Know your soil. Grow your future.</strong></p>
    <p>
        An AI-powered soil analysis and smart cultivation planning system
        for smallholder farmers in West Africa. Upload a photo of your soil
        and get instant analysis, crop recommendations, and a personalised
        planting calendar — all in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# ── QUICK STATS ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Soil Classes",    "3",       "Sandy · Clay · Loamy")
c2.metric("Crops Covered",   "6",       "West African staples")
c3.metric("NPK Estimation",  "3 Levels","Low · Medium · High")
c4.metric("Weather Data",    "Live",    "OpenWeatherMap API")

st.markdown("---")

# ── HOW IT WORKS ──────────────────────────────────────────────────────────────
st.markdown("## How GrowMate works")

col1, col2, col3, col4 = st.columns(4)

steps = [
    ("📸","Step 1","Upload a soil photo",
     "Take a clear photo of dry soil and upload it. Any smartphone works."),
    ("🤖","Step 2","AI analyses your soil",
     "MobileNetV2 classifies your soil and estimates NPK nutrient levels."),
    ("🌤️","Step 3","Live weather check",
     "Real-time temperature and rainfall combined with your soil results."),
    ("🌾","Step 4","Get your crop plan",
     "Ranked crop list and a 12-week cultivation calendar you can export."),
]

for col, (icon, step, title, desc) in zip([col1,col2,col3,col4], steps):
    with col:
        st.markdown(f"""
        <div class="gm-card">
            <div style="font-size:2rem;text-align:center;">{icon}</div>
            <div style="text-align:center;font-size:12px;
                        color:#888;margin:4px 0;">{step}</div>
            <div style="text-align:center;font-weight:bold;
                        color:#1B4332;margin-bottom:8px;">{title}</div>
            <div style="font-size:13px;color:#555;text-align:center;">
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── SUPPORTED CROPS ───────────────────────────────────────────────────────────
st.markdown("## Supported crops")

crops = [
    ("🌿","Cassava (Ege)",   "Sandy, Loamy",       "240-270 days","Drought-tolerant staple"),
    ("🍠","Yam (Isu)",       "Loamy, Clay",         "240-270 days","High-value tuber crop"),
    ("🌽","Maize (Agbado)",  "Sandy, Clay, Loamy",  "90-110 days", "Fast-growing food crop"),
    ("🫘","Cowpea (Ewa)",    "Sandy, Loamy",        "70-75 days",  "Nitrogen-fixing legume"),
    ("🥜","Groundnut (Epa)", "Sandy, Loamy",        "110-120 days","Important cash crop"),
    ("🌾","Sorghum (Oka)",   "Clay, Sandy",         "120-130 days","Drought-hardy grain"),
]

c1, c2 = st.columns(2)
for i, (icon, name, soils, days, desc) in enumerate(crops):
    col = c1 if i % 2 == 0 else c2
    with col:
        st.markdown(f"""
        <div style="background:#F0FFF4;border-radius:10px;
                    padding:12px 16px;margin-bottom:10px;
                    border:1px solid #B7E4C7;">
            <b>{icon} {name}</b><br>
            <span style="color:#2D6A4F;font-size:13px;">
                {soils} &nbsp;|&nbsp; {days} &nbsp;|&nbsp; {desc}
            </span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown("## Ready to analyse your soil?")
if st.button("🔬 Start Soil Analysis →"):
    st.switch_page("pages/1_Soil_Analysis.py")

st.markdown("---")
st.caption(
    "⚠️ GrowMate is a decision-support tool providing initial screening "
    "estimates only. For precise fertiliser recommendations, laboratory "
    "soil analysis is advised."
)