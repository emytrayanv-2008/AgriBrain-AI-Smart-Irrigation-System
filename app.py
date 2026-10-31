"""
Smart AI-Based Irrigation System - Streamlit Interactive Web Application
Real-Time Telemetry Monitoring, AI Automated Pump Actuation & Agronomic Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import json
from PIL import Image

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from inference import SmartIrrigationEngine
from hardware_bridge import HardwareBridge

# Page configuration
st.set_page_config(
    page_title="AgriBrain - AI Smart Irrigation System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #0b111e;
        color: #e6edf3;
    }
    
    /* Metrics glass card */
    .metric-card {
        background: rgba(22, 32, 54, 0.7);
        border: 1px solid rgba(56, 139, 253, 0.25);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 139, 253, 0.55);
    }
    .metric-title {
        color: #8b949e;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 2.1rem;
        font-weight: 700;
        color: #f0f6fc;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #58a6ff;
        margin-top: 4px;
    }

    /* Pump Status Badges */
    .pump-active {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        padding: 8px 16px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 0 20px rgba(2, 132, 199, 0.6);
        animation: pulse-blue 2s infinite;
    }
    .pump-inactive {
        background: rgba(33, 38, 45, 0.9);
        color: #8b949e;
        padding: 8px 16px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.05rem;
        border: 1px solid #30363d;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    @keyframes pulse-blue {
        0% { box-shadow: 0 0 0 0 rgba(2, 132, 199, 0.7); }
        70% { box-shadow: 0 0 0 14px rgba(2, 132, 199, 0); }
        100% { box-shadow: 0 0 0 0 rgba(2, 132, 199, 0); }
    }
    
    /* Header hero */
    .hero-banner {
        background: linear-gradient(90deg, #132338 0%, #0d1b2a 100%);
        border: 1px solid rgba(56, 139, 253, 0.3);
        border-radius: 14px;
        padding: 24px 30px;
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #3fb950);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-desc {
        color: #8b949e;
        font-size: 0.98rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'bridge' not in st.session_state:
    st.session_state.bridge = HardwareBridge(simulated=True)
if 'engine' not in st.session_state:
    st.session_state.engine = SmartIrrigationEngine()

bridge = st.session_state.bridge
engine = st.session_state.engine

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/plant-under-rain.png", width=64)
    st.title("AgriBrain Control")
    st.markdown("Capstone: **AI-Based Smart Irrigation**")
    st.markdown("---")
    
    st.subheader("Field & Crop Settings")
    crop_selected = st.selectbox(
        "Cultivated Crop", 
        ['Tomato', 'Wheat', 'Maize', 'Rice', 'Cotton'], 
        index=0
    )
    soil_selected = st.selectbox(
        "Soil Texture Class", 
        ['Loamy', 'Sandy', 'Clay'], 
        index=0
    )
    model_choice = st.selectbox(
        "AI Classifier Model",
        ['Random Forest', 'Decision Tree', 'Logistic Regression'],
        index=0
    )
    
    bridge.latest_telemetry['crop_type'] = crop_selected
    bridge.latest_telemetry['soil_type'] = soil_selected
    
    st.markdown("---")
    st.subheader("Pump Control Mode")
    operation_mode = st.radio("Operating Mode", ["Auto (AI-Governed)", "Manual Override"], index=0)
    
    if operation_mode == "Manual Override":
        manual_pump = st.toggle("Force Water Pump ON", value=False)
        bridge.set_manual_override(True, manual_pump)
    else:
        bridge.set_manual_override(False)
        
    st.markdown("---")
    st.caption("v1.0.0 • Deep Learning & IoT Sensor Fusion • 2026")

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 class="hero-title">AI-Based Smart Irrigation System</h1>
            <p class="hero-desc">Real-time Soil Moisture & Environmental Sensor Telemetry with Automated Machine Learning Irrigation Control</p>
        </div>
        <div style="text-align: right; margin-top: 8px;">
            <span style="background: rgba(46, 160, 67, 0.15); border: 1px solid #2ea043; color: #3fb950; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                ● AI MONITOR ONLINE
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌾 Live Telemetry & Control",
    "🧪 AI Prediction Sandbox",
    "📊 Exploratory Data Analysis (EDA)",
    "🏆 Model Benchmarking & Metrics",
    "🔌 Hardware & Serial Integration"
])

# ==========================================
# TAB 1: LIVE TELEMETRY & CONTROL
# ==========================================
with tab1:
    c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 4])
    with c_btn1:
        if st.button("🔄 Step Environment Simulation", use_container_width=True):
            bridge.step_simulation()
    with c_btn2:
        if st.button("🌧️ Toggle Rain Sensor", use_container_width=True):
            bridge.latest_telemetry['rain_sensor'] = 1 if bridge.latest_telemetry['rain_sensor'] == 0 else 0
            bridge.step_simulation()
            
    # Read current state
    t = bridge.latest_telemetry
    
    # 4 Key Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Soil Moisture Sensor</div>
            <div class="metric-val" style="color: {t['badge_color']};">{t['soil_moisture']:.1f}%</div>
            <div class="metric-sub">{t['soil_health']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Ambient Temperature</div>
            <div class="metric-val">{t['temperature']:.1f}°C</div>
            <div class="metric-sub">Soil Temp: {t['soil_temperature']:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Relative Humidity</div>
            <div class="metric-val">{t['humidity']:.1f}%</div>
            <div class="metric-sub">Sunlight: {t['sunlight_lux']:,.0f} Lux</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        rain_status = "🌧️ RAIN DETECTED" if t['rain_sensor'] == 1 else "☀️ NO RAIN (DRY)"
        rain_col = "#58a6ff" if t['rain_sensor'] == 1 else "#8b949e"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Rain Sensor Status</div>
            <div class="metric-val" style="font-size: 1.45rem; color: {rain_col};">{rain_status}</div>
            <div class="metric-sub">Active Sensor Pin: D2</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # Actuator & AI Decision Status Banner
    act_col1, act_col2 = st.columns([1, 1])
    
    with act_col1:
        st.markdown("### 🚰 Water Pump Actuation Status")
        if 'ON' in t['pump_status']:
            st.markdown(f"""
            <div class="pump-active">
                <span>🌊 PUMP ACTIVE (VALVE OPEN)</span>
            </div>
            <p style="margin-top: 10px; color: #79c0ff; font-size: 0.9rem;">
                Estimated Runtime Remaining: <b>{t['pump_runtime_remaining']:.1f} seconds</b> | Dosage: <b>{t['water_requirement_ml']:.1f} ml</b>
            </p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="pump-inactive">
                <span>🛑 PUMP IDLE (STANDBY)</span>
            </div>
            <p style="margin-top: 10px; color: #8b949e; font-size: 0.9rem;">
                Relay Module: Contact Open | 0.0 mA Draw
            </p>
            """, unsafe_allow_html=True)
            
    with act_col2:
        st.markdown("### 🧠 AI Decision & Agronomic Reasoning")
        alert_type = st.error if t['irrigation_required'] == 1 else st.success
        if t['rain_sensor'] == 1:
            st.info(f"**AI Determination:** {t['log_message']} (Model Confidence: {t['confidence']}%)")
        elif t['irrigation_required'] == 1:
            st.error(f"**AI Determination:** {t['log_message']} (Model Confidence: {t['confidence']}%)")
        else:
            st.success(f"**AI Determination:** {t['log_message']} (Model Confidence: {t['confidence']}%)")
            
    st.markdown("---")
    
    # Live Trends Chart
    st.subheader("📈 Live Field Telemetry Trends")
    if len(bridge.history) > 1:
        hist_df = pd.DataFrame(bridge.history)
        chart_df = hist_df[['timestamp', 'soil_moisture', 'temperature', 'humidity']].set_index('timestamp')
        st.line_chart(chart_df, color=["#2f9e44", "#e03131", "#1971c2"], height=280)
    else:
        st.info("Click 'Step Environment Simulation' above to generate continuous trend data.")

# ==========================================
# TAB 2: AI PREDICTION SANDBOX
# ==========================================
with tab2:
    st.subheader("🧪 Interactive What-If Scenario Simulator")
    st.markdown("Test hypothetical environmental conditions to evaluate how the AI model responds.")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        sb_moisture = st.slider("Soil Moisture Level (%)", 0.0, 100.0, 24.5, 0.5)
        sb_temp = st.slider("Ambient Temperature (°C)", 10.0, 50.0, 36.0, 0.5)
        sb_humidity = st.slider("Relative Humidity (%)", 10.0, 100.0, 30.0, 1.0)
    with s_col2:
        sb_crop = st.selectbox("Crop Variety", ['Tomato', 'Wheat', 'Maize', 'Rice', 'Cotton'], index=0, key="sb_crop")
        sb_soil = st.selectbox("Soil Type", ['Sandy', 'Loamy', 'Clay'], index=0, key="sb_soil")
        sb_rain = st.radio("Rainfall Detected?", [0, 1], format_func=lambda x: "Yes (Raining)" if x == 1 else "No Rain (Dry)", horizontal=True)
        sb_model = st.selectbox("Inference Algorithm", ['Random Forest', 'Decision Tree', 'Logistic Regression'], index=0, key="sb_model")
        
    if st.button("⚡ Run AI Prediction", type="primary", use_container_width=True):
        res = engine.predict(
            soil_moisture=sb_moisture,
            temperature=sb_temp,
            humidity=sb_humidity,
            rain_sensor=sb_rain,
            crop_type=sb_crop,
            soil_type=sb_soil,
            model_name=sb_model
        )
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Irrigation Required?", "YES (1)" if res['irrigation_required'] == 1 else "NO (0)")
        with p2:
            st.metric("Model Confidence", f"{res['confidence']}%")
        with p3:
            st.metric("Target Water Dosage", f"{res['water_requirement_ml']} ml", f"{res['recommended_pump_duration_sec']}s run")
            
        st.markdown(f"""
        <div style="background: rgba(22, 32, 54, 0.85); border-left: 4px solid {res['badge_color']}; padding: 14px 18px; border-radius: 6px; margin-top: 10px;">
            <b style="color: {res['badge_color']}; font-size: 1.05rem;">{res['status_text']}</b>
            <p style="color: #c9d1d9; margin: 4px 0 0 0;">{res['reasoning']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3: EXPLORATORY DATA ANALYSIS (EDA)
# ==========================================
with tab3:
    st.subheader("📊 Sensor Dataset & Exploratory Data Analysis")
    st.markdown("Detailed visual exploration of the agronomic sensor dataset, correlations, and distribution characteristics.")
    
    eda_plots_dir = os.path.join(os.path.dirname(__file__), 'eda_plots')
    
    eda_tab_a, eda_tab_b, eda_tab_c = st.tabs(["🔥 Correlation & Distributions", "🌱 Crop & Soil Statistics", "🕒 Diurnal 24h Cycles"])
    
    with eda_tab_a:
        e1, e2 = st.columns(2)
        with e1:
            st.markdown("#### Environmental Correlation Matrix")
            corr_path = os.path.join(eda_plots_dir, 'correlation_matrix.png')
            if os.path.exists(corr_path):
                st.image(corr_path, use_container_width=True)
        with e2:
            st.markdown("#### Soil Moisture Distribution by Target")
            dist_path = os.path.join(eda_plots_dir, 'soil_moisture_distribution.png')
            if os.path.exists(dist_path):
                st.image(dist_path, use_container_width=True)
                
    with eda_tab_b:
        e3, e4 = st.columns(2)
        with e3:
            st.markdown("#### Crop & Soil Irrigation Probability")
            crop_path = os.path.join(eda_plots_dir, 'crop_irrigation_rates.png')
            if os.path.exists(crop_path):
                st.image(crop_path, use_container_width=True)
        with e4:
            st.markdown("#### Temperature vs Humidity Distribution")
            th_path = os.path.join(eda_plots_dir, 'temp_vs_humidity.png')
            if os.path.exists(th_path):
                st.image(th_path, use_container_width=True)
                
    with eda_tab_c:
        st.markdown("#### 24-Hour Diurnal Sensor Cycle")
        diurnal_path = os.path.join(eda_plots_dir, 'diurnal_sensor_trends.png')
        if os.path.exists(diurnal_path):
            st.image(diurnal_path, use_container_width=True)
            
    st.markdown("---")
    st.markdown("#### Sample Dataset Records")
    data_path = os.path.join(os.path.dirname(__file__), 'dataset', 'smart_irrigation_data.csv')
    if os.path.exists(data_path):
        sample_df = pd.read_csv(data_path).head(10)
        st.dataframe(sample_df, use_container_width=True)

# ==========================================
# TAB 4: MODEL BENCHMARKING & METRICS
# ==========================================
with tab4:
    st.subheader("🏆 Model Evaluation, Comparative Benchmarking & Explainability")
    
    metrics_path = os.path.join(os.path.dirname(__file__), 'models', 'model_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics_data = json.load(f)
            
        st.markdown("#### 1. Classification Models Comparison")
        clf_metrics = pd.DataFrame(metrics_data['classification']).T
        clf_metrics_display = clf_metrics[['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']].copy()
        clf_metrics_display.columns = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
        clf_metrics_display = clf_metrics_display.map(lambda x: f"{x*100:.2f}%")
        st.table(clf_metrics_display)
        
        st.markdown("#### 2. Water Requirement Regression Models (ml)")
        reg_metrics = pd.DataFrame(metrics_data['regression']).T
        reg_metrics.columns = ['MAE (ml)', 'RMSE (ml)', 'R² Score']
        st.table(reg_metrics)
        
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown("#### Confusion Matrices")
        cm_path = os.path.join(eda_plots_dir, 'confusion_matrices.png')
        if os.path.exists(cm_path):
            st.image(cm_path, use_container_width=True)
    with m_col2:
        st.markdown("#### ROC Curves")
        roc_path = os.path.join(eda_plots_dir, 'roc_curves.png')
        if os.path.exists(roc_path):
            st.image(roc_path, use_container_width=True)
            
    m_col3, m_col4 = st.columns(2)
    with m_col3:
        st.markdown("#### Random Forest Feature Importance")
        feat_path = os.path.join(eda_plots_dir, 'feature_importances.png')
        if os.path.exists(feat_path):
            st.image(feat_path, use_container_width=True)
    with m_col4:
        st.markdown("#### Actual vs Predicted Water Dosage (Regression)")
        reg_plot_path = os.path.join(eda_plots_dir, 'regression_predictions.png')
        if os.path.exists(reg_plot_path):
            st.image(reg_plot_path, use_container_width=True)

# ==========================================
# TAB 5: HARDWARE & SERIAL INTEGRATION
# ==========================================
with tab5:
    st.subheader("🔌 Microcontroller & Sensor Integration (Arduino / ESP32)")
    st.markdown("""
    Connect your physical hardware prototype via USB Serial to read real soil moisture, DHT11/DHT22 temperature & humidity, and actuate the 5V relay module in real-time.
    """)
    
    h_col1, h_col2 = st.columns([1, 1])
    
    with h_col1:
        st.markdown("#### Serial Port Connection")
        available_ports = bridge.get_available_ports()
        if not available_ports:
            available_ports = ["COM1", "COM3", "COM4", "/dev/ttyUSB0"]
            st.warning("No physical serial ports currently enumerated. Simulation mode is currently running.")
            
        port_choice = st.selectbox("Select Microcontroller COM Port", available_ports)
        baud_choice = st.selectbox("Baud Rate", [9600, 115200, 57600], index=0)
        
        if st.button("🔗 Connect to Microcontroller", use_container_width=True):
            success, msg = bridge.connect_serial(port_choice, baud_choice)
            if success:
                st.success(msg)
            else:
                st.warning(msg)
                
    with h_col2:
        st.markdown("#### Pinout & Wiring Quick Reference")
        st.markdown("""
        | Sensor / Module | Microcontroller Pin (Uno / ESP32) | Voltage | Description |
        |---|---|---|---|
        | **Capacitive Soil Moisture** | Analog `A0` (Uno) / `GPIO 34` (ESP32) | 3.3V / 5V | Analog voltage calibrated to 0-100% |
        | **DHT11 / DHT22 Sensor** | Digital `D4` (Uno) / `GPIO 4` (ESP32) | 3.3V / 5V | Temperature & Relative Humidity |
        | **Rain Drop Sensor** | Digital `D2` (Uno) / `GPIO 15` (ESP32) | 5V | Active LOW Rain Trigger |
        | **5V Relay Module (Pump)** | Digital `D8` (Uno) / `GPIO 23` (ESP32) | 5V | Active HIGH/LOW Pump Coil Drive |
        """)
        
    st.markdown("---")
    st.markdown("#### Microcontroller JSON Telemetry Protocol")
    st.code("""
// The Arduino / ESP32 sends telemetry lines over Serial at 9600 baud:
{"moisture": 26.4, "temp": 32.1, "humidity": 41.5, "rain": 0}

// The Python system responds back with relay commands:
PUMP_ON\\n     // Trigger relay to start water pump
PUMP_OFF\\n    // De-energize relay to stop pump
    """, language="c")
