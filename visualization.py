import streamlit as st
import plotly.express as px

def plot_summary_charts(df):
    if 'cum_distance_km' not in df:
        st.warning("Missing data for plotting.")
        return

    col1, col2 = st.columns(2)

    with col1:
        fig_pace = px.line(df, x='cum_distance_km', y='pace', title="Pace (min/km)", markers=True)
        fig_pace.update_yaxes(title="Pace (min/km)")
        st.plotly_chart(fig_pace, use_container_width=True)

    with col2:
        fig_elev = px.line(df, x='cum_distance_km', y='elevation', title="Elevation Profile", markers=True)
        fig_elev.update_yaxes(title="Elevation (m)")
        st.plotly_chart(fig_elev, use_container_width=True)

def plot_heart_rate(df):
    if 'heart_rate' in df.columns:
        fig = px.line(df, x='time', y='heart_rate', title="Heart Rate Over Time")
        st.plotly_chart(fig, use_container_width=True)

def plot_cadence(df):
    cadence_col = None
    if 'cadence' in df.columns:
        cadence_col = 'cadence'
    elif 'cadence_running' in df.columns:
        cadence_col = 'cadence_running'

    if cadence_col:
        fig = px.line(df, x='time', y=cadence_col, title="Cadence Over Time (spm)")
        st.plotly_chart(fig, use_container_width=True)
