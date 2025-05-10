import pandas as pd
from geopy.distance import geodesic
from datetime import timedelta

def compute_metrics(data):
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    
    if len(df) < 2:
        return {"Error": "Not enough data."}, df

    # Calculate distances
    df['distance'] = [0] + [
        geodesic((df.loc[i-1, 'latitude'], df.loc[i-1, 'longitude']),
                 (df.loc[i, 'latitude'], df.loc[i, 'longitude'])).meters
        for i in range(1, len(df))
    ]

    df['cum_distance_km'] = df['distance'].cumsum() / 1000

    # Time delta in seconds
    df['duration_s'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds()

    # Pace min/km
    df['pace'] = df['duration_s'] / 60 / df['cum_distance_km']
    df['pace'] = df['pace'].replace([float('inf'), -float('inf')], None)

    # Elevation gain
    df['elevation_gain'] = df['elevation'].diff().clip(lower=0)
    elevation_gain = df['elevation_gain'].sum()

    total_dist = df['distance'].sum() / 1000
    duration = df['time'].iloc[-1] - df['time'].iloc[0]
    avg_speed = total_dist / (duration.total_seconds() / 3600)

    return {
        "Total Distance (km)": f"{total_dist:.2f}",
        "Total Duration": str(timedelta(seconds=int(duration.total_seconds()))),
        "Average Speed (km/h)": f"{avg_speed:.2f}",
        "Elevation Gain (m)": f"{elevation_gain:.2f}"
    }, df

def enrich_health_metrics(df):
    result = {}

    if 'heart_rate' in df.columns:
        result["Max HR"] = df['heart_rate'].max()
        result["Avg HR"] = df['heart_rate'].mean()

    if 'cadence' in df.columns or 'cadence_running' in df.columns:
        cadence_col = 'cadence' if 'cadence' in df.columns else 'cadence_running'
        result["Avg Cadence (spm)"] = df[cadence_col].mean()

    if 'speed' in df.columns:
        df['pace'] = 16.6667 / df['speed']  # pace in min/km
        result["Avg Pace (min/km)"] = df['pace'].mean()

    return result