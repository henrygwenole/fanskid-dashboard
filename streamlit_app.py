import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

# --- Data Generation Function ---
def generate_live_data(num_records=100):
    data = {
        'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(num_records)],
        'Driven Drive End Bearing': [random.uniform(20, 100) for _ in range(num_records)],
        'Driven non Drive End Bearing': [random.uniform(20, 100) for _ in range(num_records)],
        'Motor Drive End Bearing': [random.uniform(20, 100) for _ in range(num_records)],
        'Motor non Drive End Bearing': [random.uniform(20, 100) for _ in range(num_records)],
        'Driving belt alignment': [random.uniform(20, 100) for _ in range(num_records)],
    }
    return pd.DataFrame(data)

# --- Helper Function for Status Color and Icon ---
def get_status(value, device):
    if device == "Driving belt alignment":
        return "#E74C3C", "❌"  # Always Red for Fault
    elif value < 40:
        return "#2ECC71", "✔️"  # Green, Checkmark
    elif value < 70:
        return "#F39C12", "⚠️"  # Orange, Warning
    else:
        return "#E74C3C", "❌"  # Red, Cross

# --- Main App ---
st.set_page_config(page_title="Fanskid Monitoring Dashboard", layout="wide")

if "selected_device" not in st.session_state:
    st.session_state.selected_device = None

data = generate_live_data()

def show_device_dashboard():
    st.title("Fanskid Monitoring Dashboard")
    col1, col2, col3 = st.columns(3)
    
    for i, device in enumerate(data.columns[1:]):
        avg_value = data[device].mean()
        color, icon = get_status(avg_value, device)
        col = [col1, col2, col3][i % 3]

        with col:
            button_style = f"background-color:{color}; color:white; font-weight:bold; padding:10px; width:100%; border-radius:5px; border:none; cursor:pointer;"
            if st.markdown(
                f'<button style="{button_style}" onclick="window.location.reload();">{icon} {device}</button>',
                unsafe_allow_html=True
            ):
                st.session_state.selected_device = device
                st.rerun()

def show_device_data(device_name):
    st.title(f"Live Data - {device_name}")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data[device_name], mode='lines+markers', name=device_name))
    
    st.plotly_chart(fig)
    st.dataframe(data[['timestamp', device_name]])
    
    if st.button("Back to Dashboard"):
        st.session_state.selected_device = None
        st.rerun()

if st.session_state.selected_device:
    show_device_data(st.session_state.selected_device)
else:
    show_device_dashboard()
