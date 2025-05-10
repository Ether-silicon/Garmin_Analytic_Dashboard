import streamlit as st
import pandas as pd
import plotly.express as px
from data_parser import parse_csv, parse_fit
import base64

# ---------- Page Configuration ----------
st.set_page_config(page_title="Garmin Dashboard", layout="wide")

# ---------- Sidebar Settings ----------
with st.sidebar:
    st.title("🏃 Garmin Dashboard")
    st.markdown("Upload a `.csv` or `.fit` file exported from Garmin.")
    st.markdown("This dashboard provides:")
    st.markdown("- 📊 Pace per split")
    st.markdown("- ❤️ Heart rate trend")
    st.markdown("- 🎯 Cadence over time")
    st.markdown("- 🧭 GPS route (from FIT)")
    chart_color = st.selectbox("Color Scheme", ["Viridis", "Plasma", "Cividis", "Turbo"])
    apply_smoothing = st.checkbox("Apply smoothing to charts")
    show_pace_zones = st.checkbox("Show Pace Zones")

    st.markdown("### 🛠 Customize Pace Zones")
    zone_1 = st.number_input("Easy (min/km >)", min_value=0.0, value=6.0, step=0.1)
    zone_2 = st.number_input("Endurance (5.00 - X)", min_value=0.0, max_value=zone_1, value=5.0, step=0.1)
    zone_3 = st.number_input("Threshold (4.00 - X)", min_value=0.0, max_value=zone_2, value=4.0, step=0.1)
    zone_4 = st.number_input("Interval (< X)", min_value=0.0, max_value=zone_3, value=0.0, step=0.1)

# ---------- File Upload ----------
st.title("📊 Garmin Health & Performance Dashboard")
file = st.file_uploader("Upload your Garmin .csv or .fit file", type=["csv", "fit"], accept_multiple_files=False)

# ---------- Helper Functions ----------
def pace_str_to_float(pace_str):
    try:
        if isinstance(pace_str, str) and ":" in pace_str:
            min_str, sec_str = pace_str.strip().split(":")
            return int(min_str) + int(sec_str) / 60
    except:
        pass
    return None

def float_to_pace_str(pace_float):
    if pd.isna(pace_float):
        return "-"
    minutes = int(pace_float)
    seconds = int(round((pace_float - minutes) * 60))
    return f"{minutes}'{seconds:02}\""

def add_custom_pace_zone(df, z1, z2, z3, z4):
    def zone(p):
        if pd.isna(p): return "Unknown"
        elif p > z1: return f"Easy (> {z1:.2f})"
        elif p > z2: return f"Endurance ({z2:.2f}-{z1:.2f})"
        elif p > z3: return f"Threshold ({z3:.2f}-{z2:.2f})"
        else: return f"Interval (< {z3:.2f})"
    df['Pace Zone'] = df['Pace_float'].apply(zone)
    return df

def download_dataframe(df, filename="summary.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download Summary CSV</a>'
    return href

# ---------- Main Dashboard ----------
if file:
    ext = file.name.split(".")[-1].lower()

    if ext == "csv":
        df = parse_csv(file)
        df = df[df['Laps'].str.lower() != 'summary']
        df['Pace_float'] = df['Avg_Pacemin/km'].apply(pace_str_to_float)
        avg_pace_float = df['Pace_float'].mean()
        df['Avg_HR'] = pd.to_numeric(df['Avg_HRbpm'], errors='coerce')
        df['Cadence'] = pd.to_numeric(df['Avg_Run_Cadencespm'], errors='coerce')
        df['Distance'] = pd.to_numeric(df['Distancekm'], errors='coerce')
        source = "csv"

    elif ext == "fit":
        df = parse_fit(file)
        if 'speed' in df.columns:
            df['Pace_float'] = 16.6667 / df['speed']
            df['Avg_Pacemin/km'] = df['Pace_float'].apply(float_to_pace_str)
        else:
            df['Pace_float'] = None
            df['Avg_Pacemin/km'] = None
        df['Avg_HR'] = pd.to_numeric(df.get('heart_rate'), errors='coerce')
        df['Cadence'] = pd.to_numeric(df.get('cadence'), errors='coerce')
        df['Distance'] = pd.to_numeric(df.get('distance'), errors='coerce')
        avg_pace_float = df['Pace_float'].mean()
        source = "fit"
    else:
        st.error("Unsupported file type.")
        st.stop()

    if show_pace_zones:
        df = add_custom_pace_zone(df, zone_1, zone_2, zone_3, zone_4)

    if apply_smoothing:
        df['Avg_HR'] = df['Avg_HR'].rolling(window=5, min_periods=1).mean()
        df['Cadence'] = df['Cadence'].rolling(window=5, min_periods=1).mean()
        df['Pace_float'] = df['Pace_float'].rolling(window=5, min_periods=1).mean()

    # ---------- Summary Metrics ----------
    st.subheader("📌 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Distance (km)", round(df['Distance'].max() / 1000, 2) if source == "fit" else round(df['Distance'].sum(), 2))
    col2.metric("Avg Pace (min/km)", float_to_pace_str(avg_pace_float))
    col3.metric("Avg Heart Rate", f"{int(df['Avg_HR'].mean())} bpm" if df['Avg_HR'].notna().any() else "-")

    st.markdown(download_dataframe(df), unsafe_allow_html=True)
    st.divider()

    # ---------- 2x2 Dashboard Layout ----------
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.markdown("### 🏃 Pace per Lap / Time")
        if df['Pace_float'].notna().sum() > 0:
            color_param = 'Pace Zone' if show_pace_zones else 'Pace_float'
            fig = px.bar(df,
                         x='Laps' if source == "csv" else df['time'].dt.strftime('%H:%M:%S'),
                         y='Pace_float',
                         color=color_param,
                         text='Avg_Pacemin/km',
                         color_continuous_scale=chart_color if not show_pace_zones else None,
                         labels={'Pace_float': 'Pace (min/km)'})
            fig.update_layout(yaxis_title="Pace (min/km)", xaxis_title="Lap/Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No pace data available to visualize.")

    with col2:
        st.markdown("### ❤️ Heart Rate")
        if df['Avg_HR'].notna().sum() > 0:
            fig_hr = px.line(df,
                             x='Laps' if source == "csv" else 'time',
                             y='Avg_HR',
                             title="Heart Rate", markers=True)
            fig_hr.update_yaxes(title="BPM")
            st.plotly_chart(fig_hr, use_container_width=True)
        else:
            st.info("No heart rate data.")

    with col3:
        st.markdown("### 🎯 Cadence")
        if df['Cadence'].notna().sum() > 0:
            fig_cad = px.line(df,
                              x='Laps' if source == "csv" else 'time',
                              y='Cadence',
                              title="Cadence (spm)", markers=True)
            fig_cad.update_yaxes(title="spm")
            st.plotly_chart(fig_cad, use_container_width=True)
        else:
            st.info("No cadence data.")

    with col4:
        st.markdown("### 🧭 Route Map / Extra Metrics")
        if source == "fit" and 'latitude' in df.columns:
            gps_df = df[['latitude', 'longitude']].dropna()
            gps_df.columns = ['lat', 'lon']
            st.map(gps_df)
        else:
            st.info("Route map available only for FIT files with GPS data.")

    # ---------- Advanced Visualizations ----------
    st.subheader("📊 Custom X-Y Chart Comparison")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) >= 2:
        x_axis = st.selectbox("Select X-axis", options=numeric_cols, index=0)
        y_axis = st.selectbox("Select Y-axis", options=numeric_cols, index=1)
        fig_compare = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", trendline="ols")
        st.plotly_chart(fig_compare, use_container_width=True)

    # ---------- Pie Chart Zone Breakdown ----------
    if show_pace_zones and 'Pace Zone' in df.columns:
        st.subheader("🧩 Time in Each Pace Zone")
        zone_summary = df['Pace Zone'].value_counts().reset_index()
        zone_summary.columns = ['Zone', 'Count']
        fig_pie = px.pie(zone_summary, values='Count', names='Zone', title="Distribution of Time in Pace Zones")
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("Please upload a Garmin .csv or .fit file to begin.")
