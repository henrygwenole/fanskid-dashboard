import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq

# Configuration
DATA_FILE = "data/Data 150-F-0/51.txt"  # Replace with your actual file path
SAMPLING_RATE = 100  # Hz
SYNTHETIC_DATA_POINTS = 200
SIGNAL_FREQUENCY = 50  # Hz

# Load real data
def load_real_data(file_path):
    try:
        df = pd.read_csv(file_path, sep="\t", header=None, names=["reading", "bearing_block", "driven_pulley"])
        if df.empty:
            st.error(f"Error: The file {file_path} is empty.")
            return pd.DataFrame(columns=["reading", "bearing_block", "driven_pulley"])
        return df
    except FileNotFoundError:
        st.error(f"Error: File {file_path} not found.")
        return pd.DataFrame(columns=["reading", "bearing_block", "driven_pulley"])

# Generate synthetic data
def generate_synthetic_data(real_data, num_records=SYNTHETIC_DATA_POINTS, sampling_rate=SAMPLING_RATE):
    if real_data.empty or "driven_pulley" not in real_data.columns:
        st.warning("Real data is missing or doesn't contain 'driven_pulley'. Using default synthetic data.")
        time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
        synthetic_signal = np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals) + np.random.normal(0, 0.5, num_records)
        return pd.DataFrame({'timestamp': [datetime.now() - timedelta(seconds=i) for i in range(num_records)], 'Driving belt alignment': synthetic_signal})

    time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
    mean_real = real_data["driven_pulley"].mean()
    std_real = real_data["driven_pulley"].std()
    synthetic_signal = np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals) * std_real + mean_real + np.random.normal(0, std_real * 0.2, num_records)
    return pd.DataFrame({'timestamp': [datetime.now() - timedelta(seconds=i) for i in range(num_records)], 'Driving belt alignment': synthetic_signal})

# FFT computation
def compute_fft(signal, sampling_rate=SAMPLING_RATE):
    if signal.empty:
        return np.array([]), np.array([])
    num_samples = len(signal)
    freq_values = fftfreq(num_samples, d=1/sampling_rate)[:num_samples//2]
    fft_values = np.abs(fft(signal))[:num_samples//2]
    return freq_values, fft_values

# Load data
real_data = load_real_data(DATA_FILE)
synthetic_data = generate_synthetic_data(real_data)

# Streamlit app
st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")

if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

def show_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

    with col1:
        st.markdown(
            f'<div style="background-color:#E74C3C; padding:15px; border-radius:5px; color:white; font-weight:bold;">❌ Driving belt alignment</div>',
            unsafe_allow_html=True
        )
    with col2:
        # You'll need to place your actual image files in a directory accessible to Streamlit.
        st.image("assets/icons/data_icon.svg", width=30)  # Make sure the path is correct
        if st.button("View Data", key="data_belt"):
            st.session_state.selected_device = "Driving belt alignment"
            st.rerun()
    with col3:
        st.image("assets/icons/maintenance_icon.svg", width=30) # Make sure the path is correct
        if st.button("Maintenance", key="maint_belt"):
            st.markdown(f"[Maintenance Instructions](#)")  # Placeholder link


def show_data():
    st.title("Live Data - Driving Belt Alignment")

    if synthetic_data.empty:
        st.error("No data available for visualization.")
        return

    # Time-domain plot
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=synthetic_data['timestamp'], y=synthetic_data['Driving belt alignment'], mode='lines', name='Synthetic Data'))
    st.plotly_chart(fig_time)

    # Frequency-domain analysis
    freq_values, fft_values = compute_fft(synthetic_data['Driving belt alignment'])
    freq_values_real, fft_values_real = compute_fft(real_data['driven_pulley']) if not real_data.empty and "driven_pulley" in real_data.columns else (np.array([]), np.array([]))

    fig_freq = go.Figure()

    if freq_values_real.size > 0 and fft_values_real.size > 0:
        fig_freq.add_trace(go.Scatter(x=freq_values_real, y=fft_values_real, mode='lines', name='Real Data (Good)', line=dict(color='blue')))
    if freq_values.size > 0 and fft_values.size > 0:
        fig_freq.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='Synthetic Data (Faulty)', line=dict(color='red')))

    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
    st.plotly_chart(fig_freq)

    st.dataframe(synthetic_data[['timestamp', 'Driving belt alignment']])

    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()


if st.session_state.selected_device:
    show_data()
else:
    show_dashboard()