import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq
from scipy.signal.windows import hann

# VERY IMPORTANT: This MUST be outside any functions and at the very top
if "page_configured" not in st.session_state:
    st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")
    st.session_state.page_configured = True

# Configuration (REPLACE WITH YOUR FILE PATH)
DATA_FILE = "data/Data 150-F-0/51.txt"  # **REPLACE WITH YOUR ACTUAL FILE PATH**
SAMPLING_RATE = 100  # Hz
SIGNAL_FREQUENCY = 50  # Hz

# Load real data (with caching)
@st.cache_data
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

# Generate synthetic data (ADJUSTED)
def generate_synthetic_data(real_data, desired_duration_minutes=60, sampling_rate=SAMPLING_RATE):
    num_records = int(desired_duration_minutes * 60 * sampling_rate)
    time_intervals = np.linspace(0, desired_duration_minutes * 60, num_records)

    amplitude = 0.4  # Adjust amplitude to control the signal range
    synthetic_signal = amplitude * np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals)

    noise_std = 0.1  # Adjust standard deviation to control noise level
    synthetic_signal += np.random.normal(0, noise_std, num_records)

    dc_offset = 0.0  # Adjust if you want to shift the signal up or down
    synthetic_signal += dc_offset

    start_time = datetime.now() - timedelta(minutes=desired_duration_minutes)
    timestamps = [start_time + timedelta(seconds=i / sampling_rate) for i in range(num_records)]

    return pd.DataFrame({'timestamp': timestamps, 'Driving belt alignment': synthetic_signal})


# FFT computation with windowing and caching
@st.cache_data
def compute_fft(signal, sampling_rate=SAMPLING_RATE, max_freq=5000, zero_padding_factor=1):
    if signal.empty:
        return np.array([]), np.array([])

    signal_np = signal.to_numpy()
    num_samples = len(signal_np)
    window = hann(num_samples)
    windowed_signal = signal_np * window
    padded_signal = np.pad(windowed_signal, (0, num_samples * (zero_padding_factor - 1)), 'constant')
    fft_values = np.abs(fft(padded_signal))[:len(padded_signal) // 2]
    freq_values = fftfreq(len(padded_signal), d=1 / sampling_rate)[:len(padded_signal) // 2]
    mask = freq_values <= max_freq
    return freq_values[mask], fft_values[mask]

# Load data (outside the show_dashboard function)
real_data = load_real_data(DATA_FILE)
synthetic_data = generate_synthetic_data(real_data, desired_duration_minutes=60)

# Streamlit app logic
if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

def show_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

    with col1:
        st.markdown('<div style="background-color:#E74C3C; padding:15px; border-radius:5px; color:white; font-weight:bold;">❌ Driving belt alignment</div>', unsafe_allow_html=True)
    with col2:
        if st.button("View Data", key="data_belt"):
            st.session_state.selected_device = "Driving belt alignment"
            st.rerun()
    with col3:
        if st.button("Maintenance", key="maint_belt"):
            st.markdown(f"[Maintenance Instructions](#)")  # Placeholder link

def show_data():
    st.title("Live Data - Driving Belt Alignment")
    if synthetic_data.empty:
        st.error("No data available for visualization.")
        return

    time_range = st.selectbox("Select Time Range", ["Last 1 min", "Last 2 min", "Last 10 min", "Last 30 min", "Last 1 hour"])
    now = datetime.now()
    time_limits = {"Last 1 min": now - timedelta(minutes=1), "Last 2 min": now - timedelta(minutes=2), "Last 10 min": now - timedelta(minutes=10), "Last 30 min": now - timedelta(minutes=30), "Last 1 hour": now - timedelta(hours=1)}
    filtered_data = synthetic_data[synthetic_data['timestamp'] >= time_limits[time_range]]

    if filtered_data.empty:
        st.warning(f"No data available for the selected time range ({time_range}).")
        return

    # Debugging prints (keep these for monitoring)
    print(f"Min signal value: {filtered_data['Driving belt alignment'].min()}")
    print(f"Max signal value: {filtered_data['Driving belt alignment'].max()}")
    print(f"Std dev signal value: {filtered_data['Driving belt alignment'].std()}")
    print(f"Mean signal value: {filtered_data['Driving belt alignment'].mean()}")


    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=filtered_data['timestamp'], y=filtered_data['Driving belt alignment'], mode='lines', name='Synthetic Data'))
    fig_time.update_layout(yaxis_range=[-0.6, 0.6])  # Explicitly set y-axis range
    st.plotly_chart(fig_time)

    freq_values, fft_values = compute_fft(filtered_data['Driving belt alignment'], max_freq=5000, zero_padding_factor=2)
    fig_freq = go.Figure()
    if freq_values.size > 0 and fft_values.size > 0:
        fig_freq.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='Synthetic Data (Faulty)', line=dict(color='red')))
    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude", xaxis_range=[0, 5000])
    st.plotly_chart(fig_freq)

    st.dataframe(filtered_data[['timestamp', 'Driving belt alignment']])

    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

if st.session_state.selected_device:
    show_data()
else:
    show_dashboard()