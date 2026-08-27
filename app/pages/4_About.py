"""
GrowMate - app/pages/4_About.py
"Know your soil. Grow your future."

About page: project info, methodology, limitations, disclaimer.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import inject_css, render_sidebar

st.set_page_config(
    page_title="GrowMate - About",
    page_icon="ℹ️",
    layout="wide"
)
inject_css()
render_sidebar("About")

st.markdown("# ℹ️ About GrowMate")
st.markdown("*Know your soil. Grow your future.*")
st.markdown("---")

# Project info
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="gm-card">
        <h3>📋 Project Overview</h3>
        <p>GrowMate is an AI-based soil analysis and smart cultivation planning
        system developed as a Final Year Project at <b>Landmark University</b>,
        Omu-Aran, Kwara State, Nigeria.</p>
        <p>The system provides smallholder farmers in West Africa with an
        affordable, accessible alternative to laboratory soil testing by using
        deep learning to classify soil from smartphone photographs.</p>
        <p>
            <b>Department:</b> Computer Science<br>
            <b>Institution:</b> Landmark University, Omu-Aran<br>
            <b>Academic Year:</b> 2024/2025<br>
            <b>Version:</b> 1.0
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="gm-card">
        <h3>🎯 Research Objectives</h3>
        <ol style="line-height:2;">
            <li>Acquire a suitable dataset for soil analysis</li>
            <li>Train a deep learning model for soil classification</li>
            <li>Develop a crop recommendation mechanism</li>
            <li>Develop a web-based application for user interaction</li>
            <li>Test and evaluate system performance</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# System architecture
st.markdown("## 🏗️ System Architecture")
st.markdown("""
<div class="gm-card">
    <p>GrowMate uses a <b>Three-Tier Architecture</b> (Section 3.6):</p>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;">
        <div style="flex:1;min-width:160px;background:#F0FFF4;
                    border-radius:10px;padding:14px;text-align:center;">
            <div style="font-size:1.5rem;">🖥️</div>
            <b>Presentation Layer</b><br>
            <span style="font-size:13px;color:#555;">
                Streamlit web app<br>Interactive UI pages
            </span>
        </div>
        <div style="flex:1;min-width:160px;background:#F0FFF4;
                    border-radius:10px;padding:14px;text-align:center;">
            <div style="font-size:1.5rem;">⚙️</div>
            <b>Application Layer</b><br>
            <span style="font-size:13px;color:#555;">
                MobileNetV2 CNN<br>Scoring engine<br>Weather API
            </span>
        </div>
        <div style="flex:1;min-width:160px;background:#F0FFF4;
                    border-radius:10px;padding:14px;text-align:center;">
            <div style="font-size:1.5rem;">🗄️</div>
            <b>Data Layer</b><br>
            <span style="font-size:13px;color:#555;">
                SQLite crop database<br>HDF5 model weights
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# How the AI works
st.markdown("## 🤖 How the AI works")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="gm-card">
        <h3>🧠 Deep Learning Model</h3>
        <p>GrowMate uses <b>MobileNetV2 with transfer learning</b>.
        Pre-trained on ImageNet, fine-tuned on soil images.</p>
        <p><b>Architecture:</b><br>
        MobileNetV2 → GlobalAveragePooling2D → Dense(256, ReLU) →
        BatchNorm → Dropout(0.4) → Dense(128, ReLU) → Dropout(0.3) →
        Softmax(3) — Equation 3.2</p>
        <p><b>Loss:</b> Categorical Cross-Entropy — Equation 3.3</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="gm-card">
        <h3>🌾 Crop Scoring Algorithm</h3>
        <p>Crop recommendations use a <b>weighted scoring function</b>
        (Equation 3.4):</p>
        <div style="background:#F0FFF4;padding:12px;border-radius:8px;
                    font-family:monospace;margin:8px 0;font-weight:bold;">
            S = 0.40 × Cs + 0.30 × Ct + 0.30 × Cr
        </div>
        <p>
            <b>Cs</b> = Soil compatibility (40%)<br>
            <b>Ct</b> = Temperature suitability (30%)<br>
            <b>Cr</b> = Rainfall suitability (30%)
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tech stack
st.markdown("## 🛠️ Technology Stack")
tech = ["Python 3.8+","TensorFlow / Keras","MobileNetV2","Streamlit",
        "SQLite","OpenWeatherMap API","scikit-learn","Pillow",
        "Matplotlib / Seaborn","fpdf2","NumPy / Pandas"]
badges = "".join(
    f'<span style="background:#EAF3DE;color:#27500A;padding:4px 12px;'
    f'border-radius:20px;font-size:12px;font-weight:bold;margin:3px;'
    f'display:inline-block;">{t}</span>'
    for t in tech
)
st.markdown(f'<div class="gm-card">{badges}</div>', unsafe_allow_html=True)

st.markdown("---")

# Limitations
st.markdown("## ⚠️ System Limitations")
limits = [
    ("📸 Image quality sensitivity",
     "Results depend on image quality. Wet, shaded, or blurry photos reduce accuracy."),
    ("🔬 NPK is estimated, not measured",
     "N, P, K levels are categorical estimates based on soil class — not lab measurements."),
    ("🌍 Soil heterogeneity",
     "West African soils are highly variable. The model may miss sub-regional variation."),
    ("🌧️ Weather data accuracy",
     "Annual rainfall estimates from current weather are approximate."),
    ("🌱 Crop database scope",
     "Only 6 major crops covered. Vegetables, fruits, and minor crops are not included."),
    ("📊 Dataset size",
     "Trained on a limited dataset. Performance may vary on unusual soil types."),
]
c1, c2 = st.columns(2)
for i, (title, desc) in enumerate(limits):
    col = c1 if i % 2 == 0 else c2
    with col:
        st.markdown(f"""
        <div class="gm-warning">
            <b>{title}</b><br>
            <span style="font-size:13px;color:#666;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Disclaimer
st.markdown("## 📜 Full Disclaimer")
st.markdown("""
<div style="background:#FCEBEB;border-radius:12px;padding:20px;
            border-left:5px solid #E24B4A;font-size:14px;line-height:1.8;">
    <b>GrowMate is a research prototype and decision-support tool only.</b>
    It is not intended to substitute professional agricultural advice,
    laboratory soil analysis, or the guidance of qualified agronomists.
    <br><br>
    The AI model provides probabilistic results based on visual characteristics.
    These carry inherent uncertainty and may not accurately reflect the true
    chemical or physical properties of any specific soil sample.
    <br><br>
    The developers and Landmark University accept no liability for
    agricultural decisions made solely on the basis of GrowMate's output.
    <br><br>
    <b>Confidence threshold:</b> Only Softmax probabilities above 70%
    are considered high-confidence outputs (Section 3.8).
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#888;font-size:13px;padding:16px 0;">
    GrowMate v1.0 &nbsp;|&nbsp; Landmark University, Omu-Aran &nbsp;|&nbsp;
    Final Year Project 2024/2025 &nbsp;|&nbsp;
    <i>"Know your soil. Grow your future."</i>
</div>
""", unsafe_allow_html=True)