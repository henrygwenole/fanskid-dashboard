import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
                st.markdown(f"[Maintenance Instructions](#)")  # Placeholder link

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
    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

if st.session_state.selected_device:
    show_data(st.session_state.selected_device)
else:
    show_dashboard()
