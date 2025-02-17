import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

# --- Data Generation Function ---
def generate_live_data(num_records=100):
    data = {
        'fanskid_id': ['FSK-001' for _ in range(num_records)],
        'value': [random.uniform(20, 100) for _ in range(num_records)],
        'date_column': [datetime.now() - timedelta(minutes=i) for i in range(num_records)]
    }
    return pd.DataFrame(data)

# --- Sidebar ---
st.sidebar.header("Fanskid Monitoring")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 60, 10)

fanskid_df = generate_live_data()
date_range = st.sidebar.date_input("Date Range", value=(fanskid_df['date_column'].min(), fanskid_df['date_column'].max()))

# --- Main Content ---
st.title("Fanskid Monitoring Dashboard")

filtered_df = fanskid_df
if date_range:
    filtered_df = filtered_df[(filtered_df['date_column'].dt.date >= date_range[0]) & (filtered_df['date_column'].dt.date <= date_range[1])]

fig = go.Figure(data=[go.Scatter(x=filtered_df['date_column'], y=filtered_df['value'], mode='lines+markers')])
st.plotly_chart(fig)

st.dataframe(filtered_df)
st.button("Refresh Data", on_click=st.experimental_rerun)