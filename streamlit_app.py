import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import random
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq

# Load real data from the specified file path
def load_real_data(file_path):
    try:
        df = pd.read_csv(file_path, sep="\t", header=None, names=["reading", "bearing_block", "driven_pulley"])
        return df[["reading", "bearing_block", "driven_pulley"]]
    except FileNotFoundError:
        st.error(f"Error: File {file_path} not found.")
        return pd.DataFrame(columns=["reading", "bearing_block", "driven_pulley"])

# Synthetic Data Generation based on Real Data Statistics
def generate_synthetic_data(real_data, num_records=100, sampling_rate=100):
    time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
    mean_real = real_data.mean()
    std_real = real_data.std()
    synthetic_signal = np.sin(2 * np.pi * 50 * time_intervals) * std_real + mean_real + np.random.normal(0, std_real, num_records)
    
    return pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(seconds=i) for i in range(num_records)],
        'Driving belt alignment': synthetic_signal
    })

# Load real dataset
data_file = "data/Data 150-F-0/51.txt"  # Updated file path
real_data = load_real_data(data_file)
synthetic_data = generate_synthetic_data(real_data["driven_pulley"]) if not real_data.empty else pd.DataFrame()

st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")

if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

def compute_fft(signal, sampling_rate=100):
    num_samples = len(signal)
    freq_values = fftfreq(num_samples, d=1/sampling_rate)[:num_samples//2]
    fft_values = abs(fft(signal))[:num_samples//2]
    return freq_values, fft_values

def show_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
    
    with col1:
        st.markdown(
            f'<div style="background-color:#E74C3C; padding:15px; border-radius:5px; color:white; font-weight:bold;">❌ Driving belt alignment</div>',
            unsafe_allow_html=True
        )
    with col2:
        st.image("assets/icons/data_icon.svg", width=30)
        if st.button("View Data", key="data_belt"):
            st.session_state.selected_device = "Driving belt alignment"
            st.rerun()
    with col3:
        st.image("assets/icons/maintenance_icon.svg", width=30)
        if st.button("Maintenance", key="maint_belt"):
            st.markdown(f"[Maintenance Instructions](#)")  # Placeholder link

def show_data():
    st.title("Live Data - Driving Belt Alignment")
    
    if synthetic_data.empty:
        st.error("No data available for visualization.")
        return
    
    # Time-domain plot
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=synthetic_data['timestamp'], y=synthetic_data['Driving belt alignment'], mode='lines+markers', name='Synthetic Data'))
    st.plotly_chart(fig_time)
    
    # Frequency-domain analysis using FFT
    sampling_rate = 100  # Hz
    freq_values, fft_values = compute_fft(synthetic_data['Driving belt alignment'], sampling_rate)
    freq_values_real, fft_values_real = compute_fft(real_data['driven_pulley'], sampling_rate)
    
    fig_freq = go.Figure()
    fig_freq.add_trace(go.Scatter(x=freq_values_real, y=fft_values_real, mode='lines', name='Real Data (Good)'))
    fig_freq.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='Synthetic Data (Faulty)', line=dict(color='red')))
    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
    st.plotly_chart(fig_freq)
    
    # Data Table
    st.dataframe(synthetic_data[['timestamp', 'Driving belt alignment']])
    
    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

if st.session_state.selected_device:
    show_data()
else:
    show_dashboard()
