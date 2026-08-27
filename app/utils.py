"""
GrowMate - app/utils.py
"Know your soil. Grow your future."

Shared constants, CSS, and helper functions used by ALL app pages.
Every page imports from here - nothing is duplicated.
"""

import os
import streamlit as st

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
SOIL_CLASSES  = ["Sandy", "Clay", "Loamy"]
IMAGE_SIZE    = (224, 224)
MODEL_PATH    = "models/growmate_model.h5"
LABELS_PATH   = "models/class_labels.json"
DB_PATH       = "data/growmate_crops.db"

CROP_ICONS = {
    "Cassava":   "🌿",
    "Yam":       "🍠",
    "Maize":     "🌽",
    "Cowpea":    "🫘",
    "Groundnut": "🥜",
    "Sorghum":   "🌾",
}

NPK_COLORS = {
    "Low":    ("#E24B4A", "#FCEBEB", "🔴"),
    "Medium": ("#E9C46A", "#FAEEDA", "🟡"),
    "High":   ("#52B788", "#EAF3DE", "🟢"),
}

NPK_BAR_WIDTH = {"Low": "30%", "Medium": "62%", "High": "92%"}

SOIL_DESCRIPTIONS = {
    "Sandy": {
        "color":  "#E9C46A",
        "icon":   "🏜️",
        "desc":   "Sandy soil has large particles with good drainage but low "
                  "water and nutrient retention. Warms quickly and is easy to work.",
        "traits": ["Good drainage", "Low water retention",
                   "Easy to cultivate", "Low organic matter"],
    },
    "Clay": {
        "color":  "#D4A373",
        "icon":   "🧱",
        "desc":   "Clay soil has fine particles that retain water and nutrients "
                  "well but can become waterlogged and compacted.",
        "traits": ["High nutrient retention", "Poor drainage",
                   "Heavy when wet", "Cracks when dry"],
    },
    "Loamy": {
        "color":  "#52B788",
        "icon":   "🌿",
        "desc":   "Loamy soil is the ideal agricultural soil - a balanced mix "
                  "of sand, silt, and clay. Excellent for most crops.",
        "traits": ["Balanced drainage", "High fertility",
                   "Easy to work", "Best for most crops"],
    },
}

NPK_ESTIMATES = {
    "Sandy": {"N": "Low",    "P": "Low",    "K": "Medium"},
    "Clay":  {"N": "Medium", "P": "Medium", "K": "Medium"},
    "Loamy": {"N": "High",   "P": "Medium", "K": "High"},
}

# ── SHARED CSS ────────────────────────────────────────────────────────────────
GROWMATE_CSS = """
<style>
[data-testid="stSidebar"] {
    background-color: #1B4332;
}
[data-testid="stSidebar"] * {
    color: #D8F3DC !important;
}
.main .block-container {
    background-color: #FEFAE0;
    padding: 2rem 3rem;
}
h1, h2, h3 {
    color: #1B4332 !important;
    font-family: Georgia, serif;
}
.stButton > button {
    background-color: #2D6A4F;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-size: 15px;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #52B788;
    color: white;
}
[data-testid="stMetric"] {
    background-color: #D8F3DC;
    border-radius: 10px;
    padding: 10px 16px;
    border-left: 4px solid #2D6A4F;
}
[data-testid="stFileUploader"] {
    border: 2px dashed #52B788;
    border-radius: 12px;
    padding: 10px;
    background-color: #F0FFF4;
}
.stAlert { border-radius: 10px; }
.gm-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    border-left: 5px solid #2D6A4F;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.gm-warning {
    background: #FFF9E6;
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 16px;
    border-left: 5px solid #E9C46A;
}
.gm-hero {
    background: linear-gradient(135deg, #2D6A4F 0%, #52B788 100%);
    border-radius: 16px;
    padding: 36px 48px;
    color: white;
    margin-bottom: 28px;
}
.gm-hero h1 { color: white !important; font-size: 2.6rem; }
.gm-hero p  { color: #D8F3DC; font-size: 1.05rem; }
</style>
"""

# ── FUNCTIONS ─────────────────────────────────────────────────────────────────

def inject_css():
    """Apply GrowMate theme. Call at top of every page."""
    st.markdown(GROWMATE_CSS, unsafe_allow_html=True)


def render_sidebar(active=""):
    """Standard GrowMate sidebar. Pass the current page name to bold it."""
    pages = [
        ("🏠", "Home"),
        ("🔬", "Soil Analysis"),
        ("🌾", "Crop Recommendation"),
        ("📅", "Cultivation Calendar"),
        ("ℹ️",  "About"),
    ]
    with st.sidebar:
        st.markdown("## 🌱 GrowMate")
        st.markdown("*Know your soil. Grow your future.*")
        st.markdown("---")
        st.markdown("### Navigation")
        for icon, name in pages:
            if name == active:
                st.markdown(f"**{icon} {name}** ← you are here")
            else:
                st.markdown(f"{icon} {name}")
        st.markdown("---")
        st.caption("GrowMate v1.0 | Landmark University")
        st.caption("Final Year Project 2024/2025")


def render_npk_bars(npk_dict):
    """Colour-coded NPK progress bars. Red=Low, Amber=Medium, Green=High."""
    labels = {"N":"Nitrogen (N)","P":"Phosphorus (P)","K":"Potassium (K)"}
    for key, level in npk_dict.items():
        bar_color, bg_color, icon = NPK_COLORS[level]
        width = NPK_BAR_WIDTH[level]
        st.markdown(f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-weight:600;color:#1B4332;">
                    {icon} {labels[key]}
                </span>
                <span style="background:{bg_color};color:{bar_color};
                             font-weight:bold;padding:2px 10px;
                             border-radius:12px;font-size:13px;">
                    {level}
                </span>
            </div>
            <div style="background:#E9ECEF;border-radius:8px;
                        height:18px;width:100%;overflow:hidden;">
                <div style="background:{bar_color};height:100%;
                             width:{width};border-radius:8px;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_confidence_gauge(confidence_pct):
    """Circular confidence indicator. Green>=80%, Amber>=60%, Red<60%."""
    if confidence_pct >= 80:
        color, label = "#2D6A4F", "High confidence"
    elif confidence_pct >= 60:
        color, label = "#E9C46A", "Moderate confidence"
    else:
        color, label = "#E24B4A", "Low confidence - treat with caution"

    st.markdown(f"""
    <div style="text-align:center;padding:16px;">
        <div style="display:inline-flex;align-items:center;
                    justify-content:center;width:130px;height:130px;
                    border-radius:50%;border:10px solid {color};
                    background:white;flex-direction:column;">
            <div style="font-size:1.9rem;font-weight:bold;color:{color};">
                {confidence_pct:.0f}%
            </div>
        </div>
        <div style="margin-top:8px;font-size:13px;
                    font-weight:bold;color:{color};">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer(text=None):
    """Standard GrowMate disclaimer box."""
    if text is None:
        text = (
            "GrowMate provides <b>initial screening estimates</b> based on "
            "visual soil characteristics. Results are probabilistic and should "
            "not replace laboratory soil analysis or professional agronomic "
            "advice. Always consult a qualified agronomist before major "
            "farming decisions."
        )
    st.markdown(f"""
    <div class="gm-warning">
        <b>⚠️ Disclaimer</b><br>{text}
    </div>
    """, unsafe_allow_html=True)


def is_model_available():
    """Returns True if the trained model file exists."""
    return os.path.exists(MODEL_PATH)


def load_demo_result():
    """
    Realistic fake result used when model is not yet trained.
    Allows full UI demonstration without a trained model.
    """
    return {
        "soil_class": "Loamy",
        "confidence": 87.4,
        "npk":        {"N":"High","P":"Medium","K":"High"},
        "probs":      {"Sandy":0.06,"Clay":0.07,"Loamy":0.87},
        "is_demo":    True,
    }