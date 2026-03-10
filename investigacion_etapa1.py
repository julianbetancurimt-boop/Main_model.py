import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO SOPHISTICATED ---
st.set_page_config(page_title="R&D Materials Optimizer", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 36px; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; }
    .stTabs [aria-selected="true"] { background-color: #1d4ed8 !important; color: white !important; }
    .report-card { background-color: #1e293b; padding: 25px; border-radius: 15px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- MODELOS MATEMÁTICOS ---
def modelo_logistico(T, L, k, T0):
    return L / (1 + np.exp(-k * (T - T0)))

# --- TÍTULO Y HEADER ---
st.title("Materials Innovation | Polymeric shrink model")
st.markdown("*Coordinación de Innovación y Desarrollo - Proyecto reducción de calibre - Termoencogible*")
st.markdown("---")

# --- BARRA LATERAL (CONTROL DE VARIABLES) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3067/3067451.png", width=80)
    st.header("⚙️ Configuración Técnica")
    
    with st.expander("Resinas (Valores en COP)", expanded=True):
        costo_pcr = st.number_input("Costo PCR ($/kg)", value=6400, step=100)
        costo_vir = st.number_input("Costo Virgen + mLLDPE ($/kg)", value=7800, step=100)
        sig_pcr = st.slider("Fluencia PCR (MPa)", 8.0, 15.0, 12.0)
        sig_vir = st.slider("Fluencia Virgen (MPa)", 18.0, 35.0, 24.0)

    with st.expander("Proceso y Carga", expanded=True):
        gap = st.number_input("Gap del Dado (mm)", value=1.2)
        bur = st.slider("BUR (Soplado)", 1.5, 4.0, 3.0)
        cal_actual = st.number_input("Calibre Actual (µm)", value=60)
        vol_produccion = st.number_input("Volumen Mensual (kg)", value=25000)

# --- LÓGICA DE INGENIERÍA ---
# 1. Downgauging
f_pcr = sig_pcr * (cal_actual / 1000)
cal_target = (f_pcr / sig_vir) * 1000
ahorro_masa = ((cal_actual - cal_target) / cal_actual) * 100

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🌎 Sostenibilidad", "🏗️ Mecánica y Estabilidad", "🔥 Cinética Térmica", "💰 ROI Financiero"])

# --- TAB 1: SOSTENIBILIDAD ---
with tab1:
    st.markdown('<div class="report-card"><h3>Impacto en Economía Circular</h3></div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Espesor Objetivo", f"{cal_target:.1f} µm", f"-{ahorro_masa:.1f}%")
    m2.metric("Plástico Evitado", f"{(vol_produccion * ahorro_masa/100):,.0f} kg/mes")
    # 2.1 kg CO2e por kg plástico PE
    co2 = (vol_produccion * ahorro_masa/100) * 2.1
    m3.metric("Reducción Huella CO2", f"{co2:,.0f} kg", "Impacto Mensual")

# --- TAB 2: MECÁNICA Y ESTABILIDAD (REDISEÑADO) ---
with tab2:
    st.markdown('<div class="report-card"><h3>Análisis de Esfuerzos y Procesabilidad</h3></div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("📦 Ley de Laplace (Contención)")
        # Parámetros fijos de la paca sugeridos antes
        l_paca, a_paca, peso = 400, 200, 18
        p_eq = 2 * (l_paca + a_paca)
        d_eq = p_eq / np.pi
        
        # Esfuerzo inducido (N/mm) considerando factor dinámico
        esfuerzo_real = (peso * 9.81 * 0.22) / (2 * a_paca)
        resistencia_material = sig_vir * (cal_target / 1000)
        fs = resistencia_material / esfuerzo_real
        
        st.write(f"**Diámetro Equivalente:** {d_eq:.1f} mm")
        if fs > 1.2:
            st.success(f"Factor de Seguridad: {fs:.2f} (CUMPLE)")
        else:
            st.error(f"Factor de Seguridad: {fs:.2f} (FALLO MECÁNICO)")

    with col_r:
        st.subheader("🫧 Estabilidad de Burbuja (DDR)")
        ddr = gap / ((cal_target/1000) * bur)
        st.write(f"**Draw-Down Ratio (DDR):** {ddr:.1f}")
        
        if ddr < 45:
            st.info("Estado: Estable (Proceso Robusto)")
        elif ddr < 55:
            st.warning("Estado: Crítico (Riesgo de Oscilación)")
        else:
            st.error("Estado: Inestable (Reducir Gap o BUR)")

# --- TAB 3: CINÉTICA ---
with tab3:
    st.markdown('<div class="report-card"><h3>Cinética de Contracción Térmica</h3></div>', unsafe_allow_html=True)
    c_dat, c_plt = st.columns([1,2])
    with c_dat:
        df_lab = pd.DataFrame({"T": [90, 100, 110, 120, 130, 140, 150], "S": [2, 8, 25, 47, 57, 61, 63]})
        new_data = st.data_editor(df_lab)
    with c_plt:
        try:
            popt, _ = curve_fit(modelo_logistico, new_data["T"], new_data["S"], p0=[65, 0.1, 115])
            tr = np.linspace(85, 160, 100)
            plt.style.use('dark_background')
            fig, ax = plt.subplots(); ax.plot(tr, modelo_logistico(tr, *popt), color='#38bdf8'); ax.scatter(new_data["T"], new_data["S"], color='red')
            ax.set_title("Curva de Contracción TD"); st.pyplot(fig)
        except: st.write("Ajustando modelo...")

# --- TAB 4: FINANCIERO (PESOS COLOMBIANOS) ---
with tab4:
    st.markdown('<div class="report-card"><h3>Evaluación Económica (COP)</h3></div>', unsafe_allow_html=True)
    
    costo_mes_pcr = vol_produccion * costo_pcr
    kg_vir = vol_produccion * (1 - ahorro_masa/100)
    costo_mes_vir = kg_vir * costo_vir
    ahorro_mes = costo_mes_pcr - costo_mes_vir
    
    f1, f2, f3 = st.columns(3)
    f1.metric("Costo PCR Actual", f"$ {costo_mes_pcr:,.0f}")
    f2.metric("Costo Virgen Optimizado", f"$ {costo_mes_vir:,.0f}", f"- $ {ahorro_mes:,.0f}")
    f3.metric("AHORRO ANUAL PROYECTADO", f"$ {(ahorro_mes * 12):,.0f}")
    
    st.write("---")
    if ahorro_mes > 0:
        st.success(f"La transición a material virgen es financieramente viable. El ahorro por reducción de calibre compensa el sobrecosto de la resina en un **{((ahorro_mes/costo_mes_pcr)*100):.1f}%** mensual.")