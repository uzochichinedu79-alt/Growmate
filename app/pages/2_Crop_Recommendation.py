

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import requests
import streamlit as st
from utils import (inject_css, render_sidebar, render_disclaimer,
                   DB_PATH, CROP_ICONS, NPK_COLORS)

st.set_page_config(
    page_title="GrowMate - Crop Recommendation",
    page_icon="🌾",
    layout="wide"
)
inject_css()
render_sidebar("Crop Recommendation")

# ── WEATHER API KEY — replace with your own ───────────────────────────────────
WEATHER_KEY = "3dfa1c66372aaafb3dc8e203457981f0"

# ── WEATHER FETCH ─────────────────────────────────────────────────────────────
def get_weather(city, key):
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": key, "units": "metric"},
            timeout=8
        )
        if r.status_code != 200:
            return None
        d    = r.json()
        desc = d["weather"][0]["main"].lower()
        rain_day = 10 if "rain" in desc else 0
        return {
            "city":        d["name"],
            "country":     d["sys"]["country"],
            "temp":        d["main"]["temp"],
            "humidity":    d["main"]["humidity"],
            "description": d["weather"][0]["description"].capitalize(),
            "rain_annual": rain_day * 365 * 0.3,
        }
    except Exception:
        return None

# ── SCORING FUNCTION (Equation 3.4) ──────────────────────────────────────────
def score_crop(crop, temp, rain_annual):
    """S = 0.40*Cs + 0.30*Ct + 0.30*Cr"""
    Cs = 1.0  # soil matched by SQL query

    min_t, max_t = crop["min_temp"], crop["max_temp"]
    Ct = 1.0 if min_t <= temp <= max_t else \
         max(0, 1 - (min_t - temp) / 10) if temp < min_t else \
         max(0, 1 - (temp - max_t) / 10)

    min_r, max_r = crop["min_rainfall"], crop["max_rainfall"]
    Cr = 1.0 if min_r <= rain_annual <= max_r else \
         max(0, 1 - (min_r - rain_annual) / 500) if rain_annual < min_r else \
         max(0, 1 - (rain_annual - max_r) / 500)

    S = round(0.40*Cs + 0.30*Ct + 0.30*Cr, 4)
    return S, Cs, Ct, Cr

# ── DATABASE QUERY ────────────────────────────────────────────────────────────
def get_candidates(soil_class):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM crop_agronomy WHERE soil_type = ?
        ORDER BY crop_name
    """, (soil_class,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ── RENDER CROP CARD ──────────────────────────────────────────────────────────
def render_crop_card(crop, score, rank, Cs, Ct, Cr, confidence):
    icon     = CROP_ICONS.get(crop["crop_name"], "🌱")
    is_best  = rank == 1
    border   = "2px solid #2D6A4F" if is_best else "1px solid #E0E0E0"
    badge    = ('<span style="background:#2D6A4F;color:white;padding:3px 10px;'
                'border-radius:12px;font-size:12px;font-weight:bold;">'
                '⭐ Top Recommendation</span>') if is_best else ""

    score_pct = int(score * 100)
    bar_color = "#2D6A4F" if score_pct >= 80 else \
                "#E9C46A" if score_pct >= 60 else "#E24B4A"

    def npk_badge(level, key):
        color, bg, _ = NPK_COLORS[level]
        label = {"N":"Nitrogen","P":"Phosphorus","K":"Potassium"}[key]
        return (f'<span style="background:{bg};color:{color};padding:2px 8px;'
                f'border-radius:10px;font-size:12px;font-weight:bold;margin:2px;">'
                f'{label}: {level}</span>')

    npk_html = (npk_badge(crop["npk_nitrogen"],   "N") +
                npk_badge(crop["npk_phosphorus"],  "P") +
                npk_badge(crop["npk_potassium"],   "K"))

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:20px;
                margin-bottom:16px;border:{border};
                box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;
                    align-items:flex-start;margin-bottom:10px;">
            <div>
                <span style="font-size:1.8rem;">{icon}</span>
                <span style="font-size:1.3rem;font-weight:bold;
                             color:#1B4332;margin-left:8px;">
                    #{rank} {crop['crop_name']}
                </span>
                <span style="color:#888;font-size:13px;margin-left:6px;">
                    ({crop['local_name']})
                </span>
                <div style="margin-top:6px;">{badge}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.5rem;font-weight:bold;color:{bar_color};">
                    {score_pct}%
                </div>
                <div style="font-size:11px;color:#888;">suitability score</div>
            </div>
        </div>
        <div style="background:#E9ECEF;border-radius:8px;height:14px;
                    width:100%;overflow:hidden;margin-bottom:12px;">
            <div style="background:{bar_color};height:100%;
                         width:{score_pct}%;border-radius:8px;"></div>
        </div>
        <div style="font-size:13px;color:#444;line-height:1.6;margin-bottom:10px;">
            {crop['description']}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
            <span style="background:#F0FFF4;color:#2D6A4F;padding:3px 10px;
                         border-radius:10px;font-size:12px;">
                🗓️ {crop['grow_days']} days to harvest
            </span>
            <span style="background:#F0FFF4;color:#2D6A4F;padding:3px 10px;
                         border-radius:10px;font-size:12px;">
                🌡️ {crop['min_temp']}–{crop['max_temp']}°C
            </span>
            <span style="background:#F0FFF4;color:#2D6A4F;padding:3px 10px;
                         border-radius:10px;font-size:12px;">
                🌧️ {crop['min_rainfall']}–{crop['max_rainfall']}mm/yr
            </span>
        </div>
        <div>Required NPK: {npk_html}</div>
        <div style="margin-top:10px;font-size:12px;color:#aaa;">
            Score breakdown: Soil {int(Cs*100)}% · Temperature {int(Ct*100)}%
            · Rainfall {int(Cr*100)}% | AI confidence: {confidence:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown("# 🌾 Crop Recommendation")
st.markdown(
    "Based on your soil analysis and live weather data, "
    "GrowMate recommends the best crops for your farm."
)

# Check soil analysis done
if "soil_class" not in st.session_state:
    st.warning("⚠️ No soil analysis found. Please run Soil Analysis first.")
    if st.button("🔬 Go to Soil Analysis"):
        st.switch_page("pages/1_Soil_Analysis.py")
    st.stop()

soil_class = st.session_state["soil_class"]
confidence = st.session_state["confidence"]
npk        = st.session_state["npk"]

st.markdown("---")

# Soil summary
st.markdown("### Your soil analysis summary")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Soil Type",    soil_class)
m2.metric("Confidence",   f"{confidence:.1f}%")
m3.metric("Nitrogen",     npk["N"])
m4.metric("P / K",        f"{npk['P']} / {npk['K']}")

st.markdown("---")

# Weather input
st.markdown("### 🌤️ Live weather data")
st.markdown("Enter your nearest city to fetch live weather conditions.")

c1, c2 = st.columns([3, 1])
with c1:
    city = st.text_input("City", value="Ilorin",
                          placeholder="e.g. Ilorin, Lagos, Abuja",
                          label_visibility="collapsed")
with c2:
    fetch = st.button("🌍 Fetch Weather")

weather = None
if fetch or city:
    if WEATHER_KEY == "YOUR_API_KEY_HERE":
        st.info(
            "ℹ️ No API key set. Using default weather values. "
            "Add your OpenWeatherMap key in 2_Crop_Recommendation.py line 22."
        )
        weather = {
            "city": city, "country": "NG",
            "temp": 28.0, "humidity": 72,
            "description": "Partly cloudy (default values - no API key)",
            "rain_annual": 1100.0,
        }
    else:
        with st.spinner(f"Fetching weather for {city}..."):
            weather = get_weather(city, WEATHER_KEY)
        if weather is None:
            st.error("Could not fetch weather. Check city name or API key. Using defaults.")
            weather = {
                "city": city,"country":"NG","temp":28.0,
                "humidity":72,"description":"Default values",
                "rain_annual":1100.0,
            }

if weather:
    # Weather card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#2D6A4F 0%,#52B788 100%);
                border-radius:14px;padding:20px;color:white;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="font-size:1.2rem;font-weight:bold;">
                    📍 {weather['city']}, {weather['country']}
                </div>
                <div style="font-size:13px;opacity:0.85;margin-top:4px;">
                    {weather['description']}
                </div>
            </div>
            <div style="display:flex;gap:24px;flex-wrap:wrap;">
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:bold;">
                        {weather['temp']:.1f}°C
                    </div>
                    <div style="font-size:12px;opacity:0.8;">Temperature</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:bold;">
                        {weather['humidity']}%
                    </div>
                    <div style="font-size:12px;opacity:0.8;">Humidity</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:bold;">
                        {weather['rain_annual']:.0f}mm
                    </div>
                    <div style="font-size:12px;opacity:0.8;">Est. annual rain</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Score and rank crops
    candidates = get_candidates(soil_class)
    if not candidates:
        st.error(f"No crops found for {soil_class} soil. "
                 "Check the crop database was created by prepare_data.py.")
        st.stop()

    scored = sorted(
        [(score_crop(c, weather["temp"], weather["rain_annual"]), c)
         for c in candidates],
        key=lambda x: x[0][0], reverse=True
    )

    st.markdown("### 🏆 Recommended crops for your farm")
    st.markdown(
        f"Based on **{soil_class} soil**, {weather['temp']:.1f}°C, "
        f"and ~{weather['rain_annual']:.0f}mm/yr rainfall in **{weather['city']}**:"
    )

    # Save best crop for calendar
    st.session_state["best_crop"]  = scored[0][1]
    st.session_state["weather"]    = weather
    st.session_state["all_scored"] = [(s[0], c["crop_name"]) for s, c in scored]

    for rank, ((S, Cs, Ct, Cr), crop) in enumerate(scored, 1):
        render_crop_card(crop, S, rank, Cs, Ct, Cr, confidence)

    st.markdown("---")
    render_disclaimer(
        "Crop recommendations are generated automatically using soil "
        "classification and weather data. Always consult a local "
        "agricultural extension officer before major planting decisions."
    )
    st.markdown("---")
    st.markdown("### Ready to plan your season?")
    if st.button("📅 View Cultivation Calendar →"):
        st.switch_page("pages/3_Cultivation_Calendar.py")

else:
    st.info("Enter your city above and click **Fetch Weather** to get recommendations.")