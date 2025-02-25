import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import random
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq

# Data generation
def generate_live_data(num_records=10000, sampling_rate=1):
    time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
    timestamps = [datetime.now() - timedelta(seconds=i) for i in range(num_records)]
    
    data = {
        'timestamp': timestamps,
        'Driven Drive End Bearing': np.sin(2 * np.pi * 10 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Motor Drive End Bearing': np.sin(2 * np.pi * 20 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Driven non Drive End Bearing': np.sin(2 * np.pi * 30 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Motor non Drive End Bearing': np.sin(2 * np.pi * 40 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Driving belt alignment': np.sin(2 * np.pi * 50 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Motor Current': np.sin(2 * np.pi * 15 * time_intervals) + np.random.normal(0, 0.5, num_records),
    }
    return pd.DataFrame(data)

data = generate_live_data()

st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")

if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

# Time Filter Options
time_options = {
    "Last 1 Minute": 60,
    "Last 5 Minutes": 300,
    "Last 30 Minutes": 1800,
    "Last 1 Hour": 3600,
    "Last 12 Hours": 43200,
    "Last 24 Hours": 86400
}

selected_time_range = st.sidebar.selectbox("Select Time Range", list(time_options.keys()))
cutoff_time = datetime.now() - timedelta(seconds=time_options[selected_time_range])
data = data[data['timestamp'] >= cutoff_time]

def get_status(device):
    return ("#E74C3C", "❌") if device == "Driving belt alignment" else ("#2ECC71", "✔️")

def show_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    for device in data.columns[1:]:
        color, icon = get_status(device)
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            st.markdown(
                f'<div style="background-color:{color}; padding:15px; margin-bottom:10px; border-radius:5px; color:white; font-weight:bold;">{icon} {device}</div>',
                unsafe_allow_html=True
            )
        with col2:
            if st.button("View Data", key=f"data_{device}"):
                st.session_state.selected_device = device
                st.rerun()
        with col3:
            if st.button("Maintenance", key=f"maint_{device}"):
                if device == "Driving belt alignment":
                    st.markdown('<a href="frn://s/6u615mm" target="_blank">Maintenance Instructions</a>', unsafe_allow_html=True)
                else:
                    st.markdown("[Maintenance Instructions](#)")

def show_data(device_name):
    st.title(f"Live Data - {device_name}")
    
    # Time-domain plot
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=data['timestamp'], y=data[device_name], mode='lines+markers', name=device_name))
    st.plotly_chart(fig_time)
    
    # Frequency-domain analysis using FFT
    sampling_rate = 1  # Hz
    num_samples = len(data)
    signal = data[device_name].values
    freq_values = fftfreq(num_samples, d=1/sampling_rate)[:num_samples//2]
    fft_values = abs(fft(signal))[:num_samples//2]
    
    fig_freq = go.Figure()
    fig_freq.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='FFT Magnitude'))
    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
    st.plotly_chart(fig_freq)
    
    # Additional Motor Current vs Frequency Plot
    if device_name == "Motor Current":
        fig_motor = go.Figure()
        fig_motor.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='Motor Current FFT'))
        fig_motor.update_layout(title="Motor Current vs Frequency", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
        st.plotly_chart(fig_motor)
    
    # Data Table
    st.dataframe(data[['timestamp', device_name]])
    
    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

if st.session_state.selected_device:
    show_data(st.session_state.selected_device)
else:
    show_dashboard()
