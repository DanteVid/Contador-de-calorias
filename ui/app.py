# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import time
import requests

FASTAPI_URL = "http://localhost:8000"

st.set_page_config(
    page_title="NutriAI – Conteo Inteligente de Calorías",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark = st.session_state["dark_mode"]

# ── Paletas ──────────────────────────────────
if dark:
    BG         = "#0f1117"
    CARD_BG    = "#1a1d2e"
    CARD_BDR   = "#2d3155"
    TEXT_MAIN  = "#e8eaf6"
    TEXT_SUB   = "#9ca3af"
    FOOD_BG    = "#1e2235"
    FOOD_HOV   = "#252a45"
    UP_BG      = "#1a1d2e"
    UP_BDR     = "#4f46e5"
    HIST_BG    = "#1a1d2e"
    HIST_BDR   = "#2d3155"
    PROG_BG    = "#2d3155"
    FOOT_BDR   = "#2d3155"
    HR_COLOR   = "#2d3155"
else:
    BG         = "#f0f2f8"
    CARD_BG    = "#ffffff"
    CARD_BDR   = "#e2e8f0"
    TEXT_MAIN  = "#1e1b4b"
    TEXT_SUB   = "#64748b"
    FOOD_BG    = "#f8fafc"
    FOOD_HOV   = "#eef2ff"
    UP_BG      = "#f5f3ff"
    UP_BDR     = "#a5b4fc"
    HIST_BG    = "#ffffff"
    HIST_BDR   = "#e2e8f0"
    PROG_BG    = "#e2e8f0"
    FOOT_BDR   = "#e2e8f0"
    HR_COLOR   = "#e2e8f0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* ── App background ── */
.stApp {{ background: {BG} !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {{
    background: {'#13162b' if dark else '#1e1b4b'} !important;
    padding: 24px 16px;
}}

/* Todos los textos del sidebar en blanco */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {{
    color: #ffffff !important;
}}

/* Input numérico en sidebar */
[data-testid="stSidebar"] input[type="number"] {{
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}

/* Selectbox en sidebar — el trigger */
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {{
    color: #ffffff !important;
    font-weight: 600 !important;
}}

/* Dropdown popup — SIEMPRE fondo blanco con texto oscuro */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[data-baseweb="menu"],
[role="listbox"],
[data-baseweb="select"] ul {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15) !important;
}}
[data-baseweb="menu"] li,
[data-baseweb="option"],
[role="option"] {{
    color: #1e1b4b !important;
    font-weight: 500 !important;
    background: #ffffff !important;
}}
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover,
[role="option"]:hover {{
    background: #eef2ff !important;
    color: #4f46e5 !important;
}}

[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.15) !important; }}
[data-testid="stSidebar"] .stInfo {{
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
}}

/* ── Botón modo oscuro/claro ── */
.mode-btn > button {{
    background: rgba(255,255,255,0.15) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 999px !important;
    padding: 8px 20px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    width: auto !important;
    box-shadow: none !important;
    transition: background .2s !important;
}}
.mode-btn > button:hover {{
    background: rgba(255,255,255,0.25) !important;
    transform: none !important;
    box-shadow: none !important;
}}

/* ── Hero ── */
.hero {{
    background: linear-gradient(135deg, #3730a3 0%, #4f46e5 35%, #7c3aed 70%, #a855f7 100%);
    border-radius: 24px; padding: 48px 40px;
    margin-bottom: 28px; overflow: hidden; position: relative;
}}
.hero::after {{
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}}
.hero-inner {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 32px; position: relative; z-index: 1;
}}
.hero-text {{ flex: 1; min-width: 0; }}
.hero-title {{
    font-size: 52px; font-weight: 800;
    background: linear-gradient(90deg, #ffffff, #fde68a);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.05; margin: 0 0 14px;
}}
.hero-sub {{
    font-size: 16px; color: rgba(255,255,255,0.82);
    line-height: 1.65; margin: 0; max-width: 420px;
}}
.hero-stat {{
    display: flex; flex-direction: column; align-items: center;
    background: rgba(255,255,255,0.12); border-radius: 12px;
    padding: 12px 20px; border: 1px solid rgba(255,255,255,0.2);
    min-width: 72px;
}}
.hero-stat-num {{ font-size: 22px; font-weight: 800; color: #fbbf24; line-height: 1; }}
.hero-stat-lbl {{ font-size: 11px; color: rgba(255,255,255,0.7); margin-top: 4px; font-weight: 500; }}
.hero-visual {{
    flex-shrink: 0; position: relative;
    width: 200px; height: 200px;
    display: flex; align-items: center; justify-content: center;
}}
.hero-plate {{
    font-size: 100px; line-height: 1;
    filter: drop-shadow(0 8px 24px rgba(0,0,0,0.3));
    animation: float 3s ease-in-out infinite;
}}
@keyframes float {{
    0%,100% {{ transform: translateY(0); }}
    50%      {{ transform: translateY(-10px); }}
}}
.hero-pill {{
    position: absolute; background: rgba(255,255,255,0.95);
    color: #1e1b4b; border-radius: 999px; padding: 6px 14px;
    font-size: 12px; font-weight: 700;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    white-space: nowrap;
}}
.pill1 {{ top: 10px;  right: -20px; }}
.pill2 {{ bottom: 40px; right: -30px; }}
.pill3 {{ bottom: 10px; left: -10px; }}
.hero-badges {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.badge {{ padding: 5px 14px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
.badge-ia   {{ background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.3); }}
.badge-acad {{ background: #fbbf24; color: #1e1b4b; }}

/* ── Cards ── */
.card {{
    background: {CARD_BG};
    border-radius: 16px; padding: 24px;
    border: 1px solid {CARD_BDR};
    box-shadow: 0 1px 12px rgba(79,70,229,0.06);
    margin-bottom: 20px;
}}
.card-title {{ font-size: 17px; font-weight: 700; color: {TEXT_MAIN}; margin: 0 0 4px; }}
.card-sub   {{ font-size: 13px; color: {TEXT_SUB}; margin: 0 0 18px; }}

/* ── Upload placeholder ── */
.upload-ph {{
    border: 2px dashed {UP_BDR}; border-radius: 14px;
    padding: 48px 20px; text-align: center; background: {UP_BG};
}}
.upload-ph p {{ margin: 6px 0; }}

/* ── Metrics ── */
.metrics-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px; }}
.metric-card {{ border-radius: 14px; padding: 20px 16px; text-align: center; }}
.metric-card.purple {{ background: linear-gradient(135deg,#4f46e5,#7c3aed); color:#fff; }}
.metric-card.amber  {{ background: linear-gradient(135deg,#f59e0b,#ef4444); color:#fff; }}
.m-label {{ font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; opacity:.8; }}
.m-value {{ font-size: 40px; font-weight: 800; line-height: 1.1; margin: 4px 0 2px; }}
.m-unit  {{ font-size: 12px; opacity:.75; }}

/* ── Progress ── */
.prog-wrap {{ background: {PROG_BG}; border-radius: 999px; height: 8px; overflow: hidden; margin: 0 0 18px; }}
.prog-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg,#fbbf24,#f59e0b); }}

/* ── Food rows ── */
.food-row {{
    display: flex; justify-content: space-between; align-items: center;
    background: {FOOD_BG}; border-radius: 10px; padding: 12px 14px;
    margin-bottom: 8px; border-left: 3px solid #6366f1;
    transition: background .15s, transform .15s;
}}
.food-row:hover {{ background: {FOOD_HOV}; transform: translateX(3px); }}
.food-name  {{ font-weight: 600; font-size: 14px; color: {TEXT_MAIN}; }}
.food-macro {{ font-size: 11px; color: {TEXT_SUB}; margin-top: 2px; }}
.food-kcal  {{ font-size: 16px; font-weight: 700; color: #6366f1; white-space: nowrap; }}
.food-conf  {{
    display: inline-block; font-size: 10px; font-weight: 700;
    background: #ede9fe; color: #5b21b6; border-radius: 999px;
    padding: 1px 7px; margin-left: 5px;
}}

/* ── Rec boxes ── */
.rec-box {{
    border-radius: 12px; padding: 14px 16px; font-size: 13px; font-weight: 500;
    margin-top: 4px; line-height: 1.5;
}}
.rec-box.ok   {{ background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }}
.rec-box.warn {{ background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }}
.rec-box.info {{ background: #ede9fe; color: #4c1d95; border: 1px solid #c4b5fd; }}

/* ── History cards ── */
.hist-card {{
    background: {HIST_BG}; border-radius: 14px; padding: 16px 12px;
    border: 1px solid {HIST_BDR}; text-align: center;
    box-shadow: 0 1px 6px rgba(79,70,229,0.05);
    transition: transform .2s, box-shadow .2s;
}}
.hist-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 18px rgba(79,70,229,0.1); }}
.hist-meal {{ font-size: 11px; font-weight: 700; color: {TEXT_SUB}; text-transform: uppercase; letter-spacing: 1px; }}
.hist-time {{ font-size: 11px; color: {TEXT_SUB}; margin: 2px 0 8px; }}
.hist-kcal {{ font-size: 26px; font-weight: 800; color: #6366f1; }}
.hist-unit {{ font-size: 11px; color: {TEXT_SUB}; }}
.hist-date {{
    display: inline-block; margin-top: 8px; font-size: 10px; font-weight: 700;
    background: #ede9fe; color: #5b21b6; border-radius: 999px; padding: 2px 9px;
}}

/* ── Main buttons ── */
.stButton > button {{
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; padding: 11px 22px !important;
    font-weight: 600 !important; font-size: 14px !important;
    width: 100% !important; transition: all .2s !important;
    box-shadow: 0 3px 12px rgba(79,70,229,0.25) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.35) !important;
}}

/* ── Streamlit misc ── */
.stAlert {{ border-radius: 10px !important; }}

/* File uploader — más grande y visible */
[data-testid="stFileUploader"] {{
    border-radius: 14px !important;
}}
[data-testid="stFileUploader"] > div {{
    border: 2px dashed {UP_BDR} !important;
    border-radius: 14px !important;
    background: {UP_BG} !important;
    padding: 32px 20px !important;
    transition: border-color .2s, background .2s !important;
}}
[data-testid="stFileUploader"] > div:hover {{
    border-color: #6366f1 !important;
    background: {'#1e2235' if dark else '#eef2ff'} !important;
}}

/* ── Section headers ── */
.section-title {{
    font-size: 20px; font-weight: 700; color: {TEXT_MAIN};
    margin: 28px 0 16px; display: flex; align-items: center; gap: 8px;
}}

/* ── Footer ── */
.footer {{
    text-align: center; padding: 28px 20px; margin-top: 32px;
    border-top: 1px solid {FOOT_BDR}; color: {TEXT_SUB}; font-size: 12px;
}}
.footer strong {{ color: #6366f1; }}

/* ── Focus ring ── */
a:focus-visible, button:focus-visible, input:focus-visible {{
    outline: 3px solid #fbbf24 !important; outline-offset: 2px !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥗 NutriAI")
    st.caption("Sistema Inteligente de Calorías")
    st.markdown("---")

    # Botón modo con ícono
    icon = "☀️ Modo claro" if dark else "🌙 Modo oscuro"
    st.markdown('<div class="mode-btn">', unsafe_allow_html=True)
    if st.button(icon, key="toggle_mode"):
        st.session_state["dark_mode"] = not dark
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 👥 Equipo")
    st.info(
        "Juan Camilo Liberato Sierra\n\n"
        "Daniel Alejandro Ruiz Vidal\n\n"
        "Sara Ximena Zambrano Ortiz"
    )

    st.markdown("---")
    st.markdown("#### 🎯 Tu perfil")

    goal = st.selectbox(
        "Objetivo principal",
        ["🏋️ Pérdida de peso", "💪 Ganancia muscular", "⚖️ Recomposición corporal", "❤️ Salud general"],
        help="El sistema adapta sus recomendaciones a tu objetivo"
    )
    daily_target = st.number_input(
        "Meta calórica diaria (kcal)",
        min_value=1200, max_value=4000, value=2200, step=50,
        help="Basado en tu metabolismo basal y nivel de actividad"
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Tecnologías")
    st.markdown("""
- 🎯 YOLOv8 — Detección  
- 🧠 CNN — Clasificación  
- ☁️ Cloud backend  
- 📱 React / Kotlin
""")
    st.markdown("---")
    st.caption("Universidad de Ibagué · 2026")

# ─────────────────────────────────────────────
# HERO — layout de dos columnas dentro del banner
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-inner">
    <!-- Izquierda: texto -->
    <div class="hero-text">
      <div class="hero-badges" style="justify-content:flex-start;margin-bottom:16px">
        <span class="badge badge-acad">🎓 Investigación Académica</span>
        <span class="badge badge-ia">� YOLOv8 + CNN</span>
      </div>
      <h1 class="hero-title">NutriAI</h1>
      <p class="hero-sub">
        Estima las calorías de tus comidas con <strong style="color:#fbbf24">inteligencia artificial</strong>.<br>
        Sube una foto y obtén el desglose nutricional completo al instante.
      </p>
      <div style="display:flex;gap:20px;margin-top:24px;flex-wrap:wrap">
        <div class="hero-stat"><span class="hero-stat-num">98%</span><span class="hero-stat-lbl">Precisión</span></div>
        <div class="hero-stat"><span class="hero-stat-num">&lt;3s</span><span class="hero-stat-lbl">Análisis</span></div>
        <div class="hero-stat"><span class="hero-stat-num">500+</span><span class="hero-stat-lbl">Alimentos</span></div>
      </div>
    </div>
    <!-- Derecha: visual -->
    <div class="hero-visual">
      <div class="hero-plate">🥗</div>
      <div class="hero-pill pill1">🔥 653 kcal</div>
      <div class="hero-pill pill2">💪 46g proteína</div>
      <div class="hero-pill pill3">✅ En meta</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN — dos columnas
# ─────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

# ── Columna izquierda: subir imagen ──────────
with col_left:

    resultado = None

    st.markdown(f'<div class="card"><p class="card-title">📸 Captura tu comida</p><p class="card-sub">Sube una imagen y el sistema identificará los alimentos automáticamente</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Arrastra una imagen aquí o haz clic para seleccionar · JPG, PNG",
        type=["jpg", "jpeg", "png"],
        help="El sistema detecta múltiples alimentos en una sola foto"
    )

    if uploaded_file:
        st.image(uploaded_file, use_container_width = True)
        if st.button("Calcular"):
            response = requests.post(
            f"{FASTAPI_URL}/analyze",
            files={"file": uploaded_file.getvalue()}
            )
            resultado = response.json()["resultado"]
            st.session_state["done"] = True
        
        
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 8px;color:{TEXT_SUB};font-size:13px">
            💡 El sistema detecta múltiples alimentos en una sola foto
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("➕ Información adicional (opcional)"):
        st.text_input("Peso aproximado del plato", placeholder="Ej: 350 g")
        st.text_area("Ingredientes o método de cocción", placeholder="Ej: pollo a la plancha sin aceite…", height=72)

# ── Columna derecha: resultados ──────────────
with col_right:
    st.markdown(f'<div class="card"><p class="card-title">📊 Análisis Nutricional</p><p class="card-sub">Resultados generados por el modelo de IA</p>', unsafe_allow_html=True)

    if st.session_state.get("done", False):
        st.write(resultado)
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:72px 20px;">
            <div style="font-size:52px;margin-bottom:14px">🤖</div>
            <p style="font-size:17px;font-weight:700;color:{TEXT_MAIN};margin:0">Sistema listo</p>
            <p style="color:{TEXT_SUB};margin-top:6px;font-size:13px">Sube una imagen para comenzar el análisis</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HISTORIAL
# ─────────────────────────────────────────────
st.markdown(f'<p class="section-title">📅 Historial reciente</p>', unsafe_allow_html=True)

history = [
    {"meal": "Desayuno", "time": "08:30", "calories": 420, "date": "Hoy"},
    {"meal": "Almuerzo", "time": "13:15", "calories": 653, "date": "Hoy"},
    {"meal": "Cena",     "time": "20:00", "calories": 450, "date": "Ayer"},
    {"meal": "Almuerzo", "time": "12:45", "calories": 620, "date": "Ayer"},
]

cols = st.columns(4, gap="medium")
for col, item in zip(cols, history):
    with col:
        st.markdown(f"""
        <div class="hist-card">
            <div class="hist-meal">{item['meal']}</div>
            <div class="hist-time">{item['time']}</div>
            <div class="hist-kcal">{item['calories']}</div>
            <div class="hist-unit">kcal</div>
            <div class="hist-date">{item['date']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <p><strong>NutriAI</strong> — Sistema Inteligente de Estimación Calórica</p>
    <p style="margin-top:4px">"Development of an Intelligent Agent for Estimating and Counting Calories"</p>
    <p style="margin-top:6px;color:#818cf8">Universidad de Ibagué · 2026</p>
</div>
""", unsafe_allow_html=True)
