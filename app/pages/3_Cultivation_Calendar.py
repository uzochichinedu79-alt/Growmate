
import streamlit as st
from datetime import date, timedelta
from fpdf import FPDF
import re

st.set_page_config(page_title="GrowMate Farming Coach", page_icon="🌱", layout="wide")

st.title("🌱 Daily Farming Coach")
st.markdown("Step-by-step farming instructions for complete beginners.")

# ─────────────────────────────────────────────
# REMOVE EMOJIS FOR PDF SAFETY
# ─────────────────────────────────────────────

def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', str(text))

# ─────────────────────────────────────────────
# DAILY FARMING PLANS (BEGINNER FRIENDLY)
# ─────────────────────────────────────────────

DAILY_PLANS = {
    "Maize": [
        ("Clear land completely using hoe or cutlass.", "Removes weeds so maize can grow freely."),
        ("Break soil into fine pieces and level it.", "Helps roots grow deep and strong."),
        ("Mark straight planting rows using rope or stick.", "Makes planting organized and easy to manage."),
        ("Dig small holes (3–5 cm deep) and plant 2–3 seeds.", "Ensures at least one strong plant grows."),
        ("Lightly cover seeds with soil.", "Protects seeds and helps germination."),
        ("Water soil if no rain falls.", "Seeds need moisture to sprout."),
        ("Check for green shoots emerging.", "Shows germination is successful."),
        ("Remove weeds around young plants.", "Prevents competition for nutrients."),
        ("Add kitchen compost around plants.", "Gives natural nutrients for growth."),
        ("Inspect leaves for pests or damage.", "Early detection prevents crop loss."),
    ],

    "Cassava": [
        ("Select healthy cassava stems and cut into pieces.", "Healthy stems produce strong plants."),
        ("Clear land and remove all weeds.", "Reduces competition for nutrients."),
        ("Make ridges or mounds in soil.", "Helps tubers develop underground."),
        ("Plant stems slanted into soil.", "Improves root formation."),
        ("Cover lightly with soil.", "Prevents rotting."),
        ("Check soil moisture weekly.", "Supports early growth."),
        ("Remove weeds around plants.", "Improves yield."),
    ],

    "Yam": [
        ("Prepare large mounds using hoe.", "Gives space for tubers to grow."),
        ("Plant seed yam in center of mound.", "Ensures proper sprouting."),
        ("Install stakes for vine support.", "Helps yam climb properly."),
        ("Tie vines gently to stakes.", "Prevents damage."),
        ("Weed farm regularly.", "Keeps nutrients available for yam."),
    ],

    "Groundnut": [
        ("Loosen soil until soft and fine.", "Helps pods form underground."),
        ("Plant seeds 3–5 cm deep.", "Ensures proper germination."),
        ("Cover lightly with soil.", "Protects seeds."),
        ("Keep soil slightly moist.", "Supports sprouting."),
        ("Avoid disturbing soil after flowering.", "Pods develop underground."),
    ],

    "Cowpea": [
        ("Clear land completely.", "Removes competition."),
        ("Plant seeds shallow (2–3 cm deep).", "Ensures fast germination."),
        ("Water lightly if no rain.", "Supports early growth."),
        ("Watch for pests on leaves.", "Cowpea attracts insects."),
        ("Remove weeds early.", "Improves yield."),
    ],
}

# ─────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────

crop = st.selectbox("Choose Crop", list(DAILY_PLANS.keys()))
start_date = st.date_input("Planting Start Date", value=date.today())

plan = DAILY_PLANS[crop]

st.markdown("---")
st.subheader(f"📅 Daily Farming Guide for {crop}")

# ─────────────────────────────────────────────
# DISPLAY (STREAMLIT UI)
# ─────────────────────────────────────────────

for i, (task, reason) in enumerate(plan):
    day_date = start_date + timedelta(days=i)

    with st.container(border=True):
        st.markdown(f"## Day {i+1} — {day_date.strftime('%d %b %Y')}")
        st.write("🛠 What to do:")
        st.write(task)

        st.write("💡 Why:")
        st.write(reason)

# ─────────────────────────────────────────────
# PDF EXPORT (SAFE VERSION)
# ─────────────────────────────────────────────

def make_pdf(crop, plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    title = remove_emojis(f"GrowMate Daily Guide - {crop}")
    pdf.cell(200, 10, title, ln=True)

    for i, (task, reason) in enumerate(plan):
        pdf.ln(3)

        text = remove_emojis(
            f"Day {i+1}\n"
            f"What to do: {task}\n"
            f"Why: {reason}\n"
        )

        pdf.multi_cell(0, 7, text)

    return bytes(pdf.output(dest="S"))

# ─────────────────────────────────────────────
# DOWNLOAD
# ─────────────────────────────────────────────

st.markdown("---")
st.subheader("📤 Export Guide")

pdf_bytes = make_pdf(crop, plan)

st.download_button(
    "⬇️ Download PDF Guide",
    pdf_bytes,
    file_name=f"{crop}_daily_guide.pdf",
    mime="application/pdf"
)

st.success("Daily farming guide ready 🚜")