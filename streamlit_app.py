import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # For interactive charts

# --- Page Configuration ---
st.set_page_config(
    page_title="Fanskid Monitoring Dashboard",  # Your title
    page_icon=":bar_chart:",  # Your icon
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
@st.cache_data  # Cache the data for efficiency
def load_fanskid_data(data_path):  # Path to your data
    """Loads and preprocesses fanskid monitoring data."""
    try:
        df = pd.read_csv(data_path)  # Adjust for your data format (CSV, Excel, etc.)
        # --- Data Preprocessing (Important!) ---
        # 1. Convert date/time columns:
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower(): # Identify potential date columns
                try:
                    df[col] = pd.to_datetime(df[col]) # Try to convert to datetime
                except:
                    st.warning(f"Could not convert column '{col}' to datetime.")
        # 2. Add any calculated columns (e.g., derived metrics):
        # Example: df['efficiency'] = df['output'] / df['input']
        # 3. Handle missing values if needed:
        # df.fillna(0, inplace=True)  # Example: Fill with 0
        # df.dropna(inplace=True)    # Example: Remove rows with missing data
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {data_path}")
        return None  # Return None if file not found
    except Exception as e: # Catch other potential errors
        st.error(f"An error occurred during data loading: {e}")
        return None

# --- Load your data ---
DATA_PATH = "fanskid_data.csv"  # Now points to the file in the same directory
fanskid_df = load_fanskid_data(DATA_PATH)

if fanskid_df is None: # Exit if data loading failed
    st.stop()

# --- Sidebar ---
st.sidebar.header("Fanskid Monitoring")

# Add your sidebar filters and controls here
# Example:
selected_fanskids = st.sidebar.multiselect("Select Fanskids", fanskid_df['fanskid_id'].unique())
date_range = st.sidebar.date_input("Date Range", value=(fanskid_df['date_column'].min(), fanskid_df['date_column'].max())) # Replace 'date_column'


# --- Main Content ---
st.title("Fanskid Monitoring Dashboard")

# Filter data based on sidebar selections
filtered_df = fanskid_df.copy() # Make a copy to avoid SettingWithCopyWarning
if selected_fanskids:
    filtered_df = filtered_df[filtered_df['fanskid_id'].isin(selected_fanskids)]
if date_range:
    filtered_df = filtered_df[(filtered_df['date_column'] >= date_range[0]) & (filtered_df['date_column'] <= date_range[1])] # Replace 'date_column'

# --- Charts and Metrics ---
# Example Chart 1: Fanskid Performance Over Time (Plotly)
st.header("Fanskid Performance")
if not filtered_df.empty:
    fig = go.Figure()
    for fanskid in selected_fanskids: # Or however you want to group your data
        fanskid_data = filtered_df[filtered_df['fanskid_id'] == fanskid]
        fig.add_trace(go.Scatter(
            x=fanskid_data['date_column'],  # Replace with your date/time column
            y=fanskid_data['performance_metric'], # Replace with your performance metric
            mode='lines',
            name=fanskid,
            connectgaps=True
        ))
    fig.update_layout(title="Fanskid Performance Over Time", xaxis_title="Time", yaxis_title="Performance")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected criteria.")

# Example Metric 1: Average Performance
st.header("Key Metrics")
if not filtered_df.empty:
    avg_performance = filtered_df['performance_metric'].mean()
    st.metric("Average Performance", f"{avg_performance:.2f}")
else:
    st.info("No data available for the selected criteria.")

# Add more charts and metrics as needed

# --- Data Table (Optional) ---
if st.checkbox("Show Data Table"):
    st.dataframe(filtered_df)