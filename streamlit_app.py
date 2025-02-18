import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

# --- Data Generation Function ---
def generate_live_data(num_records=100):
    data = {
        'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(num_records)],
        'Driven Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],  # Set to green range
        'Driven non Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],  # Set to green range
        'Motor Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],  # Set to green range
        'Motor non Drive End Bearing': [random.uniform(20, 40) for _ in range(num_records)],  # Set to green range
        'Driving belt alignment': [random.uniform(80, 100) for _ in range(num_records)],  # Set to red range
    }
    return pd.DataFrame(data)

# --- Helper Function for Status Color and Icon ---
def get_status(value, device):
    if device == "Driving belt alignment":
        return "#E74C3C", "❌"  # Always Red for Fault
    else:
        return "#2ECC71", "✔️"  # Always Green for Other Bearings

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
            st.markdown(
                f'<button style="width: 100%; padding: 10px; background-color:{color}; border: none; color: white; font-weight: bold; cursor: pointer; border-radius: 5px;">{icon} {device}</button>',
                unsafe_allow_html=True
            )
            if st.button(f"Select {device}", key=device):
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
