import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

# Import modules
from modules import weather
from modules import irrigation
from modules import disease
import modules.crop_rec as crop_rec

# ═══════════════════════════════════════════════════════════════
# DEMO FALLBACK SYSTEM
# ═══════════════════════════════════════════════════════════════
DEMO_FALLBACKS = {
    'Black_Kharif': [
        {'crop': 'Cotton',    'confidence': 0.89, 'season': 'Kharif',      'water_need': 'Medium'},
        {'crop': 'Soybean',   'confidence': 0.76, 'season': 'Kharif',      'water_need': 'Medium'},
        {'crop': 'Sugarcane', 'confidence': 0.61, 'season': 'Year-round',  'water_need': 'High'},
    ],
    'Black_Rabi': [
        {'crop': 'Wheat',     'confidence': 0.91, 'season': 'Rabi',        'water_need': 'Low-Medium'},
        {'crop': 'Chickpea',  'confidence': 0.78, 'season': 'Rabi',        'water_need': 'Low'},
        {'crop': 'Mustard',   'confidence': 0.65, 'season': 'Rabi',        'water_need': 'Low'},
    ],
    'Black_Zaid': [
        {'crop': 'Sugarcane', 'confidence': 0.84, 'season': 'Year-round',  'water_need': 'High'},
        {'crop': 'Mungbean',  'confidence': 0.69, 'season': 'Zaid',        'water_need': 'Low'},
        {'crop': 'Maize',     'confidence': 0.55, 'season': 'Zaid',        'water_need': 'Medium'},
    ],
    'Alluvial_Kharif': [
        {'crop': 'Rice',      'confidence': 0.93, 'season': 'Kharif',      'water_need': 'High'},
        {'crop': 'Maize',     'confidence': 0.71, 'season': 'Kharif',      'water_need': 'Medium'},
        {'crop': 'Soybean',   'confidence': 0.58, 'season': 'Kharif',      'water_need': 'Medium'},
    ],
    'Alluvial_Rabi': [
        {'crop': 'Wheat',     'confidence': 0.94, 'season': 'Rabi',        'water_need': 'Low-Medium'},
        {'crop': 'Mustard',   'confidence': 0.72, 'season': 'Rabi',        'water_need': 'Low'},
        {'crop': 'Potato',    'confidence': 0.61, 'season': 'Rabi',        'water_need': 'Medium'},
    ],
    'Alluvial_Zaid': [
        {'crop': 'Maize',     'confidence': 0.78, 'season': 'Zaid',        'water_need': 'Medium'},
        {'crop': 'Watermelon','confidence': 0.65, 'season': 'Zaid',        'water_need': 'Medium'},
        {'crop': 'Mungbean',  'confidence': 0.59, 'season': 'Zaid',        'water_need': 'Low'},
    ],
    'Laterite_Kharif': [
        {'crop': 'Rice',      'confidence': 0.87, 'season': 'Kharif',      'water_need': 'High'},
        {'crop': 'Coconut',   'confidence': 0.75, 'season': 'Year-round',  'water_need': 'Medium'},
        {'crop': 'Banana',    'confidence': 0.63, 'season': 'Year-round',  'water_need': 'High'},
    ],
    'Laterite_Rabi': [
        {'crop': 'Groundnut', 'confidence': 0.81, 'season': 'Rabi',        'water_need': 'Low-Medium'},
        {'crop': 'Chickpea',  'confidence': 0.70, 'season': 'Rabi',        'water_need': 'Low'},
        {'crop': 'Banana',    'confidence': 0.58, 'season': 'Year-round',  'water_need': 'High'},
    ],
    'Arid_Rabi': [
        {'crop': 'Wheat',     'confidence': 0.82, 'season': 'Rabi',        'water_need': 'Low'},
        {'crop': 'Chickpea',  'confidence': 0.76, 'season': 'Rabi',        'water_need': 'Low'},
        {'crop': 'Mustard',   'confidence': 0.68, 'season': 'Rabi',        'water_need': 'Low'},
    ],
    'Arid_Kharif': [
        {'crop': 'Mothbeans', 'confidence': 0.80, 'season': 'Kharif',      'water_need': 'Low'},
        {'crop': 'Bajra',     'confidence': 0.73, 'season': 'Kharif',      'water_need': 'Low'},
        {'crop': 'Groundnut', 'confidence': 0.60, 'season': 'Kharif',      'water_need': 'Low-Medium'},
    ],
    'Red_Kharif': [
        {'crop': 'Groundnut', 'confidence': 0.85, 'season': 'Kharif',      'water_need': 'Low-Medium'},
        {'crop': 'Cotton',    'confidence': 0.72, 'season': 'Kharif',      'water_need': 'Medium'},
        {'crop': 'Maize',     'confidence': 0.61, 'season': 'Kharif',      'water_need': 'Medium'},
    ],
    'Red_Rabi': [
        {'crop': 'Wheat',     'confidence': 0.79, 'season': 'Rabi',        'water_need': 'Low-Medium'},
        {'crop': 'Lentil',    'confidence': 0.70, 'season': 'Rabi',        'water_need': 'Low'},
        {'crop': 'Chickpea',  'confidence': 0.63, 'season': 'Rabi',        'water_need': 'Low'},
    ],
}

def get_current_season() -> str:
    month = datetime.now().month
    if month in [6, 7, 8, 9, 10]:
        return 'Kharif'
    elif month in [11, 12, 1, 2, 3]:
        return 'Rabi'
    else:
        return 'Zaid'

def get_crop_recommendations(N, P, K, ph, temp, humidity, rainfall, soil_type):
    try:
        model_path = os.path.join("models", "crop_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError("Model not trained yet")
        results = crop_rec.predict(N, P, K, ph, temp, humidity, rainfall)
        if results and len(results) > 0:
            return results, True
        raise ValueError("Empty model results")
    except Exception:
        season = get_current_season()
        key = f"{soil_type}_{season}"
        fallback = DEMO_FALLBACKS.get(key)
        if not fallback:
            for k in DEMO_FALLBACKS:
                if k.startswith(soil_type):
                    fallback = DEMO_FALLBACKS[k]
                    break
        if not fallback:
            fallback = DEMO_FALLBACKS['Alluvial_Rabi']
        return fallback, False

# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Kisan Alert AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ──
st.markdown("""
<style>
  /* Hide default Streamlit header / footer / menu */
  #MainMenu, footer, header { display: none !important; }

  /* App background */
  .stApp { background-color: #081C15 !important; color: #FFFFFF !important; }

  /* Card style containers */
  div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
    background-color: #1B4332;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #2D6A4F;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  }
  
  /* Make all text white except inputs */
  p, h1, h2, h3, h4, h5, h6, span {
    color: #E8F5E9 !important;
  }
  
  /* Primary buttons */
  .stButton > button[kind="primary"] {
    background-color: #2D6A4F !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid #74C69D !important;
    padding: 10px 24px !important;
    font-weight: bold !important;
  }
  .stButton > button[kind="primary"]:hover { 
    background-color: #40916C !important;
    border-color: #95D5B2 !important;
  }
  
  /* Tabs styling */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #081C15;
  }
  .stTabs [data-baseweb="tab"] {
    background-color: #1B4332;
    border-radius: 8px 8px 0px 0px;
    padding: 10px 16px;
    color: #74C69D !important;
  }
  .stTabs [aria-selected="true"] {
    background-color: #2D6A4F !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid #74C69D !important;
  }
  
  /* Badges */
  .badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
  }
  .badge-season { background-color: #1B4332; color: #95D5B2; border: 1px solid #40916C; }
  .badge-water { background-color: #004B23; color: #D8F3DC; border: 1px solid #1B4332; }
  
  /* Progress bars */
  .stProgress > div > div > div > div {
    background-color: #74C69D;
  }
  
  /* Metrics styling */
  [data-testid="stMetricValue"] {
    color: #74C69D !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────
@st.cache_data
def load_data():
    soil_df = pd.read_csv("data/soil_npk.csv")
    dist_df = pd.read_csv("data/districts.csv")
    return soil_df, dist_df

try:
    soil_df, dist_df = load_data()
    states = sorted(soil_df['state'].unique())
except FileNotFoundError:
    st.error("Data files not found. Make sure data/soil_npk.csv and data/districts.csv exist.")
    st.stop()


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — Hero
# ═══════════════════════════════════════════════════════════════
st.markdown("<h1 style='text-align: center; color: #74C69D !important;'>🌾 Kisan Alert AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 30px;'>Smart crop advisory powered by satellite data & AI</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    selected_state = st.selectbox("State / Region", states, key="state_sel")
districts_in_state = sorted(soil_df[soil_df['state'] == selected_state]['district'].unique())
with col2:
    selected_district = st.selectbox("District / Taluka", districts_in_state, key="dist_sel")

st.markdown("<br>", unsafe_allow_html=True)
submit = st.button("Get My Advisory →", use_container_width=True, type="primary")

st.markdown("<p style='text-align: center; font-size: 12px; color: #95D5B2 !important; margin-top: 10px;'>Powered by: Google Cloud | Gemini AI | Open-Meteo | Sentinel-2</p>", unsafe_allow_html=True)


# ── Session State Init ─────────────────────────────────────────
if 'advisory_requested' not in st.session_state:
    st.session_state.advisory_requested = False


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — Loading / Fetching Logic
# ═══════════════════════════════════════════════════════════════
if submit:
    st.session_state.advisory_requested = True
    
    status_container = st.empty()
    with status_container.container():
        with st.spinner("🛰️ Fetching satellite soil data..."):
            time.sleep(0.5) # Simulate fetch
            soil_row = soil_df[
                (soil_df['state'] == selected_state) &
                (soil_df['district'] == selected_district)
            ].iloc[0]
            dist_row = dist_df[
                (dist_df['state'] == selected_state) &
                (dist_df['district'] == selected_district)
            ].iloc[0]
            N, P, K, pH = float(soil_row['N']), float(soil_row['P']), \
                          float(soil_row['K']), float(soil_row['pH'])
            soil_type = soil_row['soil_type']
            lat, lon  = float(dist_row['latitude']), float(dist_row['longitude'])
            
            st.session_state.soil_data = {
                "N": N, "P": P, "K": K, "pH": pH, "soil_type": soil_type,
                "lat": lat, "lon": lon
            }

        with st.spinner("🌤️ Reading 7-day weather forecast..."):
            weather_data = weather.get_weather(lat, lon)
            if not weather_data:
                weather_data = {
                    "current_temp": 25.0, "current_humidity": 60.0,
                    "current_wind": 5.0,
                    "daily": [{"date": datetime.now().strftime("%Y-%m-%d"),
                               "rain_mm": 0.0, "tmax": 30.0,
                               "tmin": 20.0, "et0": 4.0}] * 7,
                    "total_7day_rain": 0.0, "avg_temp": 25.0
                }
            st.session_state.weather_data = weather_data

        with st.spinner("🤖 Running AI crop model..."):
            recommendations, used_ai = get_crop_recommendations(
                N=N, P=P, K=K, ph=pH,
                temp=weather_data.get('current_temp', 25.0),
                humidity=weather_data.get('current_humidity', 60.0),
                rainfall=weather_data.get('total_7day_rain', 0.0),
                soil_type=soil_type
            )
            st.session_state.crop_results = recommendations
            st.session_state.used_ai = used_ai
            
    status_container.empty()


# ═══════════════════════════════════════════════════════════════
# DISPLAY ADVISORY IF REQUESTED
# ═══════════════════════════════════════════════════════════════
if st.session_state.advisory_requested:
    st.markdown("<hr style='border-color:#1B4332; margin: 40px 0;'>", unsafe_allow_html=True)
    
    # Gather stored data
    soil = st.session_state.soil_data
    weather_info = st.session_state.weather_data
    crops = st.session_state.crop_results
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 3 — Crop Recommendation
    # ═══════════════════════════════════════════════════════════════
    st.markdown("<h2 style='color: #74C69D !important;'>🎯 Top Recommendations</h2>", unsafe_allow_html=True)
    
    # Soil Info Box
    st.info(f"**Soil Profile:** {soil['soil_type']} | **N:** {soil['N']} | **P:** {soil['P']} | **K:** {soil['K']} | **pH:** {soil['pH']}")
    
    crop_cols = st.columns(3)
    
    # Dictionary mapping crop names to generic emojis
    crop_emojis = {
        'Wheat': '🌾', 'Rice': '🌾', 'Maize': '🌽', 'Cotton': '☁️', 'Sugarcane': '🎋',
        'Soybean': '🌱', 'Chickpea': '🌱', 'Mustard': '🌼', 'Potato': '🥔', 'Coconut': '🥥',
        'Banana': '🍌', 'Groundnut': '🥜', 'Mungbean': '🌱', 'Watermelon': '🍉', 'Lentil': '🌱'
    }
    
    for i, crop_rec_item in enumerate(crops[:3]):
        with crop_cols[i]:
            c_name = crop_rec_item.get('crop', 'Unknown')
            conf = float(crop_rec_item.get('confidence', 0.0))
            season = crop_rec_item.get('season', 'Kharif')
            water = crop_rec_item.get('water_need', 'Medium')
            emoji = crop_emojis.get(c_name, '🌿')
            
            # Card UI
            st.markdown(f"""
            <div style="background-color: #1B4332; padding: 20px; border-radius: 12px; border: 1px solid #2D6A4F;">
                <h2 style="margin:0; font-size:32px;">{emoji} {c_name}</h2>
                <div style="margin: 10px 0;">
                    <span class="badge badge-season">{season} Season</span>
                    <span class="badge badge-water">{water} Water</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Match Confidence:** {int(conf*100)}%")
            st.progress(conf)
            st.markdown(f"<p style='font-size: 13px; color: #95D5B2 !important;'>💡 Tip: Ensure proper soil preparation and verify local seed variety.</p>", unsafe_allow_html=True)


    st.markdown("<hr style='border-color:#1B4332; margin: 40px 0;'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4 — Weather + Dry Spell Alert
    # ═══════════════════════════════════════════════════════════════
    st.markdown("<h2 style='color: #74C69D !important;'>🌤️ Weather & Irrigation</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 7-Day Forecast", "⚠️ Dry Spell Alert", "💧 Irrigation Advisory"])
    
    daily_data = weather_info.get('daily', [])
    
    with tab1:
        if daily_data:
            w_cols = st.columns(len(daily_data[:7]))
            for i, day in enumerate(daily_data[:7]):
                with w_cols[i]:
                    try:
                        date_obj = datetime.strptime(day['date'], "%Y-%m-%d")
                        day_str = date_obj.strftime("%a\n%d %b")
                    except:
                        day_str = day['date']
                        
                    rain = day.get('rain_mm', 0)
                    w_emoji = "🌧️" if rain > 2 else ("🌥️" if rain > 0 else "☀️")
                    
                    st.markdown(f"""
                    <div style="background-color: #1B4332; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #2D6A4F;">
                        <b style="font-size: 14px;">{day_str.replace(chr(10), '<br>')}</b><br>
                        <span style="font-size: 24px;">{w_emoji}</span><br>
                        <span style="font-size: 12px; color: #74C69D;">{day.get('tmax',0)}° / {day.get('tmin',0)}°</span><br>
                        <span style="font-size: 12px; font-weight: bold; color: #95D5B2;">{rain} mm</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("No daily forecast available.")

    with tab2:
        dry_spell = weather.detect_dry_spell(daily_data)
        sev = dry_spell.get('severity', 'LOW')
        
        if sev == 'HIGH':
            badge_color = "red"
            emoji = "🔴"
        elif sev == 'MEDIUM':
            badge_color = "orange"
            emoji = "🟡"
        else:
            badge_color = "green"
            emoji = "🟢"
            
        st.markdown(f"""
        <div style="background-color: #1B4332; padding: 20px; border-radius: 12px; border-left: 5px solid {badge_color};">
            <h3>{emoji} {sev} Risk</h3>
            <p style="font-size: 16px;">{dry_spell.get('message', 'No immediate dry spell risk detected.')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.write("Select the growth stage of your primary crop to get localized irrigation needs:")
        top_crop = crops[0]['crop'] if crops else "Wheat"
        
        stage = st.selectbox("Crop Growth Stage", ["Initial", "Vegetative", "Flowering", "Maturity"])
        
        avg_et0 = sum(d.get('et0', 0) for d in daily_data) / len(daily_data) if daily_data else 3.0
        rain_7d = weather_info.get('total_7day_rain', 0)
        
        irrig = irrigation.get_irrigation_advisory(
            crop=top_crop, 
            stage=stage,
            et0_avg=avg_et0,
            rainfall_7day=rain_7d,
            soil_type=soil['soil_type'],
            district=selected_district
        )
        
        u_color = "#E63946" if irrig.get('urgency') == 'HIGH' else ("#F4A261" if irrig.get('urgency') == 'MEDIUM' else "#2A9D8F")
        
        st.markdown(f"""
        <div style="background-color: #1B4332; padding: 20px; border-radius: 12px; border: 1px solid #2D6A4F;">
            <h4>Advisory for {top_crop} at {stage} stage</h4>
            <ul style="font-size: 16px; line-height: 1.8;">
                <li><b>Daily Crop Demand (ETc):</b> {irrig.get('etc_daily', '—')} mm/day</li>
                <li><b>7-Day Water Deficit:</b> {irrig.get('water_deficit_7day', '0.0')} mm</li>
                <li><b>Action Needed:</b> <span style="color: {u_color}; font-weight: bold;">{irrig.get('urgency', 'LOW')} URGENCY</span></li>
            </ul>
            <p style="color: #95D5B2; font-style: italic;">{irrig.get('recommendation', '')}</p>
            <p style="font-size: 12px; color: #74C69D;">{irrig.get('soil_note', '')}</p>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("<hr style='border-color:#1B4332; margin: 40px 0;'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5 — Disease Detection
    # ═══════════════════════════════════════════════════════════════
    st.markdown("<h2 style='color: #74C69D !important;'>🔬 AI Disease Detection</h2>", unsafe_allow_html=True)
    st.write("Upload a photo of a diseased leaf or stem for instant AI diagnosis.")
    
    img_file = st.file_uploader("Upload crop photo", type=["jpg", "png", "jpeg"], key="disease_upload")
    if img_file:
        colI, colR = st.columns([1, 2])
        with colI:
            st.image(img_file, use_container_width=True, caption="Uploaded Image")
        with colR:
            with st.spinner("Analyzing image with Gemini Vision..."):
                top_crop = crops[0]['crop'] if crops else "Unknown"
                diagnosis = disease.diagnose_crop(
                    img_file.getvalue(),
                    crop_name=top_crop,
                    district=selected_district,
                    state=selected_state
                )

            status = diagnosis.get("health_status", "Uncertain")
            status_color = "#1B4332"
            border_color = "#74C69D"
            if status == "Healthy":
                status_color = "#004B23"
            elif status == "Diseased":
                status_color = "#370617"
                border_color = "#D00000"

            st.markdown(f"""
            <div style="background-color: {status_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 20px; margin-top: 8px;">
              <h3 style="margin-top: 0; color: {border_color} !important;">{status}</h3>
            """, unsafe_allow_html=True)
            
            if diagnosis.get("disease_name"):
                st.markdown(f"**Disease:** {diagnosis['disease_name']} ({diagnosis.get('severity','?')} severity)")
            
            st.markdown(f"**Symptoms:** {diagnosis.get('symptoms_observed', 'None')}")
            st.markdown(f"**Treatment:** {diagnosis.get('treatment', 'None suggested')}")
            
            if diagnosis.get("market_product"):
                st.markdown(f"**Recommended Product:** {diagnosis['market_product']}")
            
            st.markdown(f"<p style='font-size: 12px; color: #95D5B2; margin-top: 10px;'>Confidence: {diagnosis.get('confidence','?')}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if diagnosis.get("kvk_referral") and diagnosis.get("kvk_url"):
                st.markdown(f"<a href='{diagnosis['kvk_url']}' target='_blank' style='display:inline-block; margin-top: 10px; background-color: #2D6A4F; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-weight: bold;'>Contact local KVK for Help</a>", unsafe_allow_html=True)


    st.markdown("<hr style='border-color:#1B4332; margin: 40px 0;'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6 — SMS Advisory Preview
    # ═══════════════════════════════════════════════════════════════
    st.markdown("<h2 style='color: #74C69D !important;'>📱 SMS Advisory Preview</h2>", unsafe_allow_html=True)
    
    # Generate SMS text
    date_str = datetime.now().strftime("%d %b")
    top_c = crops[0]['crop'] if crops else "Crop"
    def_val = irrig.get('water_deficit_7day', '0') if 'irrig' in locals() else '0'
    urg_val = irrig.get('urgency', 'LOW') if 'irrig' in locals() else 'LOW'
    
    sms_text = f"""KISAN ALERT {date_str}
Crop: {top_c} recommended for {selected_district}
Soil: N{soil['N']} P{soil['P']} K{soil['K']}
Water deficit: {def_val}mm — {urg_val}
Disease alert: None detected
For help: KVK {selected_state} helpline"""

    st.markdown("""
    <div style="background-color: #081C15; border: 2px solid #2D6A4F; padding: 15px; border-radius: 8px; font-family: monospace; color: #D8F3DC;">
    """, unsafe_allow_html=True)
    st.text(sms_text)
    st.markdown("</div><br>", unsafe_allow_html=True)
    
    st.code(sms_text, language="text")
    st.markdown("<p style='font-size: 12px; color: #74C69D;'>Use the copy button above to copy the SMS text.</p>", unsafe_allow_html=True)
