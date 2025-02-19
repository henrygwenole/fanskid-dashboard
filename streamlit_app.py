import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from scipy.fftpack import fft, fftfreq

# Configuration - Moved to the top for easy modification
DATA_FILE = "data/Data 150-F-0/51.txt"
SAMPLING_RATE = 100  # Hz
SYNTHETIC_DATA_POINTS = 200  # Increased for smoother plots
SIGNAL_FREQUENCY = 50 # Hz, frequency of the sine wave used in synthetic data generation

# Load real data
def load_real_data(file_path):
    try:
        df = pd.read_csv(file_path, sep="\t", header=None, names=["reading", "bearing_block", "driven_pulley"])
        if df.empty:
            st.error(f"Error: The file {file_path} is empty.")
            return pd.DataFrame(columns=["reading", "bearing_block", "driven_pulley"])  # Return empty DataFrame
        return df
    except FileNotFoundError:
        st.error(f"Error: File {file_path} not found.")
        return pd.DataFrame(columns=["reading", "bearing_block", "driven_pulley"]) # Return empty DataFrame


# Generate synthetic data (Improved)
def generate_synthetic_data(real_data, num_records=SYNTHETIC_DATA_POINTS, sampling_rate=SAMPLING_RATE):
    if real_data.empty or "driven_pulley" not in real_data.columns: #Handle missing column.
        st.warning("Real data is missing or doesn't contain 'driven_pulley'. Using default synthetic data.")
        time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
        synthetic_signal = np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals) + np.random.normal(0, 0.5, num_records) # Default signal
        return pd.DataFrame({'timestamp': [datetime.now() - timedelta(seconds=i) for i in range(num_records)], 'Driving belt alignment': synthetic_signal})

    time_intervals = np.linspace(0, num_records / sampling_rate, num_records)
    mean_real = real_data["driven_pulley"].mean() # directly access the driven pulley column
    std_real = real_data["driven_pulley"].std()
    synthetic_signal = np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_intervals) * std_real + mean_real + np.random.normal(0, std_real * 0.2, num_records) # Added noise control
    return pd.DataFrame({'timestamp': [datetime.now() - timedelta(seconds=i) for i in range(num_records)], 'Driving belt alignment': synthetic_signal})



# FFT computation (Improved)
def compute_fft(signal, sampling_rate=SAMPLING_RATE):
    if signal.empty:
        return np.array([]), np.array([])
    num_samples = len(signal)
    freq_values = fftfreq(num_samples, d=1/sampling_rate)[:num_samples//2]
    fft_values = np.abs(fft(signal))[:num_samples//2] # Use np.abs for magnitude
    return freq_values, fft_values


# Load data
real_data = load_real_data(DATA_FILE)
synthetic_data = generate_synthetic_data(real_data)

# Streamlit app
st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")

if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

def show_dashboard():
    # ... (rest of the dashboard code remains the same)

def show_data():
    st.title("Live Data - Driving Belt Alignment")

    if synthetic_data.empty:
        st.error("No data available for visualization.")
        return

    # Time-domain plot
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=synthetic_data['timestamp'], y=synthetic_data['Driving belt alignment'], mode='lines', name='Synthetic Data')) #Removed markers for cleaner lines
    st.plotly_chart(fig_time)

    # Frequency-domain analysis
    freq_values, fft_values = compute_fft(synthetic_data['Driving belt alignment'])
    freq_values_real, fft_values_real = compute_fft(real_data['driven_pulley']) if not real_data.empty and "driven_pulley" in real_data.columns else (np.array([]), np.array([]))


    fig_freq = go.Figure()

    if freq_values_real.size > 0 and fft_values_real.size > 0:
        fig_freq.add_trace(go.Scatter(x=freq_values_real, y=fft_values_real, mode='lines', name='Real Data (Good)', line=dict(color='blue'))) # Changed color to blue
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