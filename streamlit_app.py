import streamlit as st
import pandas as pd
import plotly.graph_objects as go
<<<<<<< HEAD
import numpy as np
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq
from scipy.signal.windows import hann

# VERY IMPORTANT: This MUST be outside any functions and at the very top
if "page_configured" not in st.session_state:
    st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")
    st.session_state.page_configured = True
=======
import random
from datetime import datetime, timedelta

# Data generation
def generate_live_data(num_records=100):
    data = {
        'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(num_records)],
        'Driven Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],
        'Motor Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],
        'Driven non Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],
        'Motor non Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],
        'Driving belt alignment': [random.uniform(80, 100) for _ in range(num_records)],
    }
    return pd.DataFrame(data)
>>>>>>> parent of fd13548 (Update streamlit_app.py)

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

# Generate synthetic data (ADJUSTED - with np.clip())
def generate_synthetic_data(real_data, desired_duration_minutes=60, sampling_rate=SAMPLING_RATE):
    num_records = int(desired_duration_minutes * 60 * sampling_rate)
    time_intervals = np.linspace(0, desired_duration_minutes * 60, num_records)

    amplitude = 0.5  # Maximum possible amplitude
    frequency = SIGNAL_FREQUENCY  # Your signal frequency
    synthetic_signal = amplitude * np.sin(2 * np.pi * frequency * time_intervals)

    noise_std_percentage = 0.1  # 10% of the maximum amplitude
    noise_std = amplitude * noise_std_percentage
    synthetic_signal += np.random.normal(0, noise_std, num_records)

    # Ensure the signal stays within +/- 0.5 (clipping):
    synthetic_signal = np.clip(synthetic_signal, -0.5, 0.5)

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

<<<<<<< HEAD
=======
# Motor and belt drive details
MOTOR_SPEED = 2952  # rpm
FAN_SPEED = 2000  # rpm
DRIVER_DIA = 160  # mm
DRIVEN_DIA = 236  # mm
BELT_FREQ = (MOTOR_SPEED / 60) * (DRIVER_DIA / DRIVEN_DIA)  # Hz

def get_status(device):
    return ("#E74C3C", "❌") if device == "Driving belt alignment" else ("#2ECC71", "✔️")

>>>>>>> parent of fd13548 (Update streamlit_app.py)
def show_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

<<<<<<< HEAD
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
    st.plotly_chart(fig_time)  # No need to set y-axis range here anymore

    freq_values, fft_values = compute_fft(filtered_data['Driving belt alignment'], max_freq=5000, zero_padding_factor=2)
    fig_freq = go.Figure()
    if freq_values.size > 0 and fft_values.size > 0:
        fig_freq.add_trace(go.Scatter(x=freq_values, y=fft_values, mode='lines', name='Synthetic Data (Faulty)', line=dict(color='red')))
    fig_freq.update_layout(title="Frequency Domain Analysis", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude", xaxis_range=[0, 5000])
    st.plotly_chart(fig_freq)

    st.dataframe(filtered_data[['timestamp', 'Driving belt alignment']])

=======
def show_data(device_name):
    st.title(f"Live Data - {device_name}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data[device_name], mode='lines+markers', name=device_name))
    if device_name == "Driving belt alignment":
        frequencies = [BELT_FREQ, MOTOR_SPEED / 60, FAN_SPEED / 60, 50]  # Belt, Shaft, Fan, Line Frequencies
        for freq in frequencies:
            fig.add_shape(type='line', x0=min(data['timestamp']), x1=max(data['timestamp']), y0=freq, y1=freq,
                          line=dict(color='red', dash='dot'))
    st.plotly_chart(fig)
    st.dataframe(data[['timestamp', device_name]])
>>>>>>> parent of fd13548 (Update streamlit_app.py)
    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

if st.session_state.selected_device:
    show_data()
else:
    show_dashboard()