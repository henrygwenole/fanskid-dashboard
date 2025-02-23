import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import random
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq

# Data generation
def generate_live_data(num_records=100, sampling_rate=100):
    time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
    data = {
        'timestamp': [datetime.now() - timedelta(seconds=i) for i in range(num_records)],
        'Driven Drive End Bearing': np.sin(2 * np.pi * 10 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Motor Drive End Bearing': np.sin(2 * np.pi * 20 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Driven non Drive End Bearing': np.sin(2 * np.pi * 30 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Motor non Drive End Bearing': np.sin(2 * np.pi * 40 * time_intervals) + np.random.normal(0, 0.5, num_records),
        'Driving belt alignment': np.sin(2 * np.pi * 50 * time_intervals) + np.random.normal(0, 0.5, num_records),
    }
    return pd.DataFrame(data)

data = generate_live_data()

st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")

if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

# Motor and belt drive details
MOTOR_SPEED = 2952  # rpm
FAN_SPEED = 2000  # rpm
DRIVER_DIA = 160  # mm
DRIVEN_DIA = 236  # mm
BELT_FREQ = (MOTOR_SPEED / 60) * (DRIVER_DIA / DRIVEN_DIA)  # Hz


def get_status(device):
    return ("#E74C3C", "❌") if device == "Driving belt alignment" else ("#2ECC71", "✔️")


def show_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    for device in data.columns[1:]:
        color, icon = get_status(device)
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            st.markdown(
                f'<div style="background-color:{color}; padding:15px; border-radius:5px; color:white; font-weight:bold;">{icon} {device}</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.image("assets/icons/data_icon.svg", width=30)
            if st.button("View Data", key=f"data_{device}"):
                st.session_state.selected_device = device
                st.rerun()
        with col3:
            st.image("assets/icons/maintenance_icon.svg", width=30)
            if st.button("Maintenance", key=f"maint_{device}"):
                if device == "Driving belt alignment":
                    st.markdown('<a href="https://nmis.frontline.io/s/6u615mm" target="_blank" style="text-decoration:none; font-weight:bold; color:#007BFF;">Maintenance Instructions</a>', unsafe_allow_html=True)
                else:
                    st.markdown("[Maintenance Instructions](#)")  # Placeholder link


def show_data(device_name):
    st.title(f"Live Data - {device_name}")
    
    # Time-domain plot
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=data['timestamp'], y=data[device_name], mode='lines+markers', name=device_name))
    st.plotly_chart(fig_time)
    
    # Frequency-domain analysis using FFT
    sampling_rate = 100  # Hz
    num_samples = len(data)
    signal = data[device_name].values
    freq_values = fftfreq(num_samples, d=1/sampling_rate)[:num_samples//2]
    fft_values = abs(fft(signal))[:num_samples//2]
    
    fig_freq = go.Figure()
    fig_freq.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='FFT Magnitude'))
    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
    st.plotly_chart(fig_freq)
    
    # Data Table
    st.dataframe(data[['timestamp', device_name]])
    
    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()


if st.session_state.selected_device:
    show_data(st.session_state.selected_device)
else:
    show_dashboard()
