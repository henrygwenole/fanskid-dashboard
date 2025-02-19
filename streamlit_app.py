import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq

# Configuration
DATA_FILE = "data/Data 150-F-0/51.txt"  # **REPLACE WITH YOUR ACTUAL FILE PATH**
SAMPLING_RATE = 100  # Hz
SIGNAL_FREQUENCY = 50  # Hz  (This might need adjustment based on your data)

# 1. Load Real Data (Adapt this to your file format)
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

# 2. Generate Synthetic Data (Use real data statistics)
def generate_synthetic_data(real_data, desired_duration_minutes=60, sampling_rate=SAMPLING_RATE):
    if real_data.empty or "driven_pulley" not in real_data.columns:
        st.warning("Real data is missing or doesn't contain 'driven_pulley'. Using default synthetic data.")
        num_records = int(desired_duration_minutes * 60 * sampling_rate)
        time_intervals = np.linspace(0, desired_duration_minutes * 60, num_records)
        synthetic_signal = np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals) + np.random.normal(0, 0.5, num_records)
        start_time = datetime.now() - timedelta(minutes=desired_duration_minutes)
        timestamps = [start_time + timedelta(seconds=i / sampling_rate) for i in range(num_records)]
        return pd.DataFrame({'timestamp': timestamps, 'Driving belt alignment': synthetic_signal})

    mean_real = real_data["driven_pulley"].mean()
    std_real = real_data["driven_pulley"].std()

    num_records = int(desired_duration_minutes * 60 * sampling_rate)
    time_intervals = np.linspace(0, desired_duration_minutes * 60, num_records)

    synthetic_signal = np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals) * std_real + mean_real + np.random.normal(0, std_real * 0.2, num_records)

    start_time = datetime.now() - timedelta(minutes=desired_duration_minutes)
    timestamps = [start_time + timedelta(seconds=i / sampling_rate) for i in range(num_records)]

    return pd.DataFrame({'timestamp': timestamps, 'Driving belt alignment': synthetic_signal})


# 3. Compute FFT (Improved)
def compute_fft(signal, sample_rate=100):
    N = len(signal)
    T = 1 / sample_rate
    yf = np.fft.fft(signal)
    xf = np.fft.fftfreq(N, T)[:N // 2]  # Positive frequencies only
    return xf, np.abs(yf[:N // 2])  # Return frequencies and magnitudes

# ... (Rest of the code remains the same)

def show_data():
    st.title("Live Data - Driving Belt Alignment")

    if synthetic_data.empty:
        st.error("No data available for visualization.")
        return

    # Time Range Selection
    time_range = st.selectbox("Select Time Range", ["Last 1 min", "Last 2 min", "Last 10 min", "Last 30 min", "Last 1 hour"])

    now = datetime.now()
    if time_range == "Last 1 min":
        time_limit = now - timedelta(minutes=1)
    elif time_range == "Last 2 min":
        time_limit = now - timedelta(minutes=2)
    elif time_range == "Last 10 min":
        time_limit = now - timedelta(minutes=10)
    elif time_range == "Last 30 min":
        time_limit = now - timedelta(minutes=30)
    elif time_range == "Last 1 hour":
        time_limit = now - timedelta(hours=1)

    filtered_data = synthetic_data[synthetic_data['timestamp'] >= time_limit]

    if filtered_data.empty:
        st.warning(f"No data available for the selected time range ({time_range}).")
        return

    # Time-domain plot (using filtered data)
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=filtered_data['timestamp'], y=filtered_data['Driving belt alignment'], mode='lines', name='Synthetic Data'))
    st.plotly_chart(fig_time)

    # Frequency-domain analysis (using filtered data and improved FFT)
    freq, magnitude = compute_fft(filtered_data['Driving belt alignment'], SAMPLING_RATE)  # Use improved FFT

    fig_freq = go.Figure()
    fig_freq.add_trace(go.Scatter(x=freq, y=magnitude, mode='lines', name='Synthetic Data (Faulty)', line=dict(color='red')))  # Plot using freq and magnitude
    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
    st.plotly_chart(fig_freq)

    st.dataframe(filtered_data[['timestamp', 'Driving belt alignment']])

    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

# ... (Rest of the code remains the same)