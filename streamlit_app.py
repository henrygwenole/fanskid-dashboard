import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Fanskid Monitoring Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Loading ---
try:
    with open('style.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("style.css not found. Using default Streamlit styling.")

# --- Data Loading ---
@st.cache_data
def load_fanskid_data(data_path):
    """Loads and preprocesses fanskid monitoring data."""
    try:
        df = pd.read_csv(data_path)
        # --- Data Preprocessing (Crucial!) ---
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception as e:
                    st.warning(f"Could not convert column '{col}' to datetime: {e}")
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {data_path}")
        return None
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# --- Load your data ---
DATA_PATH = "fanskid_data.csv" # Or the actual path to your CSV
fanskid_df = load_fanskid_data(DATA_PATH)

if fanskid_df is None:
    st.stop()

# --- Sidebar ---
st.sidebar.header("Fanskid Monitoring")

# Example filters (adapt to your data)
if 'fanskid_id' in fanskid_df.columns: # Check if the column exists
    selected_fanskids = st.sidebar.multiselect("Select Fanskids", fanskid_df['fanskid_id'].unique())
else:
    st.warning("Column 'fanskid_id' not found in data.")
    selected_fanskids = # Initialize to empty list

if 'date_column' in fanskid_df.columns:
    date_range = st.sidebar.date_input("Date Range", value=(fanskid_df['date_column'].min(), fanskid_df['date_column'].max()))
else:
    st.warning("Column 'date_column' not found in data.")
    date_range = None

# --- Main Content ---
st.title("Fanskid Monitoring Dashboard")

# Filter data (handle missing columns)
filtered_df = fanskid_df.copy()
if selected_fanskids and 'fanskid_id' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['fanskid_id'].isin(selected_fanskids)]
if date_range and 'date_column' in filtered_df.columns:
    filtered_df = filtered_df[(filtered_df['date_column'] >= date_range) & (filtered_df['date_column'] <= date_range)]

# --- Charts and Metrics (handle missing data) ---
# Example Chart: Fanskid Performance Over Time
st.header("Fanskid Performance")

if not filtered_df.empty and 'date_column' in filtered_df.columns and 'performance_metric' in filtered_df.columns:
    fig = go.Figure()
    for fanskid in selected_fanskids:
        fanskid_data = filtered_df[filtered_df['fanskid_id'] == fanskid]
        fig.add_trace(go.Scatter(
            x=fanskid_data['date_column