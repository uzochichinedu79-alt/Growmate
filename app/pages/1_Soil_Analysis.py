
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
import json
from PIL import Image
from utils import (inject_css, render_sidebar, render_npk_bars,
                   render_confidence_gauge, render_disclaimer,
                   is_model_available, load_demo_result,
                   SOIL_DESCRIPTIONS, NPK_ESTIMATES,
                   MODEL_PATH, LABELS_PATH, IMAGE_SIZE)

st.set_page_config(
    page_title="GrowMate - Soil Analysis",
    page_icon="🔬",
    layout="wide"
)
inject_css()
render_sidebar("Soil Analysis")

# ── LOAD MODEL IF AVAILABLE 
DEMO_MODE = not is_model_available()

if not DEMO_MODE:
    import tensorflow as tf

    @st.cache_resource
    def load_model():
        return tf.keras.models.load_model(MODEL_PATH)

    @st.cache_data
    def load_labels():
        if os.path.exists(LABELS_PATH):
            with open(LABELS_PATH) as f:
                return json.load(f)
        return {"0":"Sandy","1":"Clay","2":"Loamy"}

    model  = load_model()
    labels = load_labels()

def preprocess(pil_image):
    img = pil_image.convert("RGB").resize(IMAGE_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 🔬 Soil Analysis")
st.markdown("Upload a photograph of your soil sample to receive an instant AI analysis.")

if DEMO_MODE:
    st.warning(
        "**Demo Mode** — Trained model not found. "
        "Results shown are simulated for demonstration. "
        "Run `python train_model.py` to enable real AI analysis."
    )

st.markdown("---")

# ── UPLOAD ────────────────────────────────────────────────────────────────────
col_up, col_prev = st.columns(2)

with col_up:
    st.markdown("### 📤 Upload your soil image")
    st.markdown("Use **dry soil** photographed in **natural daylight** for best results.")
    uploaded = st.file_uploader(
        "Choose a soil image",
        type=["jpg","jpeg","png","bmp","webp"],
        label_visibility="collapsed"
    )
    st.markdown("""
    <div style="font-size:13px;color:#888;margin-top:6px;">
        Tips: dry soil only · natural light · fill the frame · avoid shadows
    </div>
    """, unsafe_allow_html=True)

with col_prev:
    if uploaded:
        st.image(Image.open(uploaded),
                 caption="Your uploaded soil image",
                 use_column_width=True)
    else:
        st.markdown("""
        <div style="background:#F0FFF4;border-radius:12px;padding:60px 20px;
                    text-align:center;border:2px dashed #52B788;color:#2D6A4F;">
            <div style="font-size:3rem;">📷</div>
            <div style="font-size:15px;margin-top:10px;">
                Your soil image will appear here
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── DEMO BUTTON ───────────────────────────────────────────────────────────────
show_demo_btn = DEMO_MODE and not uploaded
if show_demo_btn:
    st.markdown("")
    if st.button("🎭 Show demo results (presentation mode)"):
        st.session_state["show_demo"] = True

# ── RUN ANALYSIS ──────────────────────────────────────────────────────────────
run_analysis = uploaded is not None or st.session_state.get("show_demo", False)

if run_analysis:
    st.markdown("---")

    with st.spinner("🤖 GrowMate AI is analysing your soil..."):
        if DEMO_MODE or uploaded is None:
            demo       = load_demo_result()
            pred_class = demo["soil_class"]
            confidence = demo["confidence"]
            npk        = demo["npk"]
            all_probs  = demo["probs"]
            is_demo    = True
        else:
            img        = Image.open(uploaded)
            inp        = preprocess(img)
            probs_arr  = model.predict(inp, verbose=0)[0]
            pred_idx   = int(np.argmax(probs_arr))
            pred_class = labels[str(pred_idx)]
            confidence = float(probs_arr[pred_idx]) * 100
            npk        = NPK_ESTIMATES[pred_class]
            all_probs  = {labels[str(i)]: float(probs_arr[i])
                          for i in range(len(probs_arr))}
            is_demo    = False

    label = " (Demo)" if is_demo else ""
    st.success(f"✅ Analysis complete!{label}")
    st.markdown("## 📊 Your Results")

    soil_info = SOIL_DESCRIPTIONS[pred_class]
    r1, r2, r3 = st.columns([1.2, 1, 1.4])

    # Soil type card
    with r1:
        traits_html = "".join(
            f'<div style="background:#F0FFF4;border-radius:6px;'
            f'padding:5px 10px;margin:4px 0;font-size:13px;'
            f'color:#2D6A4F;">✓ {t}</div>'
            for t in soil_info["traits"]
        )
        st.markdown(f"""
        <div class="gm-card" style="border-left-color:{soil_info['color']};">
            <div style="font-size:3rem;text-align:center;">{soil_info['icon']}</div>
            <div style="text-align:center;font-size:1.6rem;font-weight:bold;
                        color:#1B4332;margin:8px 0;">
                {pred_class} Soil
            </div>
            <div style="text-align:center;font-size:14px;color:#555;
                        margin-bottom:14px;">
                {soil_info['desc']}
            </div>
            {traits_html}
        </div>
        """, unsafe_allow_html=True)

    # Confidence gauge
    with r2:
        st.markdown("### Confidence")
        render_confidence_gauge(confidence)
        st.markdown(
            '<div style="text-align:center;font-size:13px;color:#555;'
            'margin-bottom:8px;">All class probabilities:</div>',
            unsafe_allow_html=True
        )
        for cls, prob in all_probs.items():
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:4px 0;font-size:13px;">'
                f'<span>{cls}</span>'
                f'<span style="font-weight:bold;">{prob*100:.1f}%</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    # NPK bars
    with r3:
        st.markdown("### NPK Nutrient Levels")
        st.markdown(
            '<div style="font-size:13px;color:#555;margin-bottom:14px;">'
            'Estimated from soil visual properties and texture class.</div>',
            unsafe_allow_html=True
        )
        render_npk_bars(npk)
        st.markdown(
            '<div style="font-size:12px;color:#888;margin-top:6px;">'
            'Categorical estimates only. Laboratory testing required '
            'for precise values.</div>',
            unsafe_allow_html=True
        )

    # Save to session state for other pages
    st.session_state["soil_class"]  = pred_class
    st.session_state["confidence"]  = confidence
    st.session_state["npk"]         = npk
    st.session_state["probs"]       = all_probs

    st.markdown("---")
    render_disclaimer()
    st.markdown("---")
    st.markdown("### What next?")
    st.markdown(
        "Your soil results are saved. Head to **Crop Recommendation** "
        "to get personalised crop advice."
    )
    if st.button("🌾 Get Crop Recommendations →"):
        st.switch_page("pages/2_Crop_Recommendation.py")

else:
    st.info("👆 Upload a soil image above to begin your analysis.")