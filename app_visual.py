# app_visual.py - Versión con mejoras visuales
import datetime as dt
from datetime import datetime, date, timedelta
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum
import plotly.express as px

# Configuración Streamlit
st.set_page_config(
    page_title="✂️ Mi Barbería - Sistema Profesional", 
    layout="wide",
    page_icon="✂️",
    initial_sidebar_state="expanded"
)

# CSS personalizado para interfaz moderna
st.markdown("""
<style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --success-color: #C73E1D;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Estilo general */
    .main {
        font-family: 'Inter', sans-serif;
        padding-top: 1rem;
    }
    
    /* Header principal */
    .header-container {
        background: var(--background-gradient);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.3rem;
        font-weight: 300;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar personalizado */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Métricas modernas */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Botones modernos */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, var(--secondary-color), var(--primary-color));
    }
    
    /* Tabs modernos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px 10px 0 0;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }
    
    /* Alertas personalizadas */
    .success-alert {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 1px solid #28a745;
        border-radius: 10px;
        padding: 1rem;
        color: #155724;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(40, 167, 69, 0.1);
    }
    
    .info-alert {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border: 1px solid #17a2b8;
        border-radius: 10px;
        padding: 1rem;
        color: #0c5460;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(23, 162, 184, 0.1);
    }
    
    /* Navegación sidebar */
    .nav-header {
        background: var(--background-gradient);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Header principal mejorado
st.markdown("""
<div class="header-container">
    <h1 class="header-title">✂️ Mi Barbería Premium</h1>
    <p class="header-subtitle">🏆 Sistema de Gestión Profesional 🏆</p>
</div>
""", unsafe_allow_html=True)

# Sidebar con navegación moderna
st.sidebar.markdown("""
<div class="nav-header">
    🏪 NAVEGACIÓN
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "📍 Selecciona una sección:",
    [
        "📊 Dashboard Principal", 
        "🧾 Registrar Venta", 
        "💰 Finanzas Completas", 
        "📈 Reportes Avanzados",
        "👤 Gestión Clientes", 
        "🧰 Catálogo Items", 
        "📜 Historial Completo"
    ],
    index=0
)

# Mostrar mensaje de bienvenida con las mejoras
if "Dashboard" in page:
    st.markdown("""
    ## 🎉 ¡Bienvenido a tu sistema mejorado!
    
    ### ✨ **Nuevas características visuales:**
    - 🎨 **Diseño moderno** con gradientes y sombras
    - 🏷️ **Header elegante** con efectos visuales
    - 🎯 **Navegación mejorada** con iconos
    - 💫 **Botones interactivos** con animaciones
    - 📊 **Métricas con hover effects**
    
    ### 🚀 **Nueva sección agregada:**
    - 📈 **Reportes Avanzados** - ¡Pruébala!
    
    ### 🎯 **Para ver todas las mejoras:**
    1. Navega por las diferentes secciones
    2. Prueba la nueva sección "📈 Reportes Avanzados"
    3. Observa los efectos hover en botones y métricas
    """)
    
    # Métricas de ejemplo con el nuevo diseño
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: var(--primary-color); margin: 0;">💰 Ingresos</h3>
            <h2 style="margin: 0.5rem 0;">$ 125.000</h2>
            <p style="color: #666; margin: 0;">↗️ +15% vs mes anterior</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: var(--secondary-color); margin: 0;">✂️ Servicios</h3>
            <h2 style="margin: 0.5rem 0;">45</h2>
            <p style="color: #666; margin: 0;">🔥 Día muy activo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: var(--accent-color); margin: 0;">👥 Clientes</h3>
            <h2 style="margin: 0.5rem 0;">28</h2>
            <p style="color: #666; margin: 0;">💎 8 nuevos esta semana</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: var(--success-color); margin: 0;">📈 Balance</h3>
            <h2 style="margin: 0.5rem 0;">$ 98.500</h2>
            <p style="color: #666; margin: 0;">💪 Excelente mes</p>
        </div>
        """, unsafe_allow_html=True)

elif "Reportes" in page:
    st.title("📈 Reportes Avanzados - ¡NUEVA SECCIÓN!")
    
    st.markdown("""
    <div class="success-alert">
        🎉 <strong>¡Esta es la nueva sección que agregué!</strong><br>
        Aquí tendrás reportes súper avanzados para analizar tu barbería.
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs de ejemplo
    tab1, tab2, tab3 = st.tabs(["🏆 Top Servicios", "💰 Análisis Financiero", "👥 Clientes VIP"])
    
    with tab1:
        st.subheader("🏆 Servicios más populares")
        st.info("Aquí verás gráficos de tus servicios más vendidos y rentables")
        
    with tab2:
        st.subheader("💰 Análisis financiero detallado")
        st.info("ROI, proyecciones, márgenes de ganancia y más")
        
    with tab3:
        st.subheader("👥 Tus mejores clientes")
        st.info("Análisis de fidelidad y clientes que más gastan")

else:
    st.title(f"{page}")
    st.markdown("""
    <div class="info-alert">
        ℹ️ <strong>Sección en desarrollo</strong><br>
        Esta sección mantendrá toda la funcionalidad original pero con el nuevo diseño visual.
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    ✂️ <strong>Mi Barbería Premium</strong> - Sistema de Gestión Profesional<br>
    <small>Versión mejorada con diseño moderno</small>
</div>
""", unsafe_allow_html=True)
