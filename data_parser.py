import gpxpy
from fitparse import FitFile
import pandas as pd
import io

def parse_gpx(file):
    gpx = gpxpy.parse(file)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    'time': point.time,
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                })
    return data

def parse_fit(file):
    fitfile = FitFile(file)
    records = []
    for record in fitfile.get_messages('record'):
        row = {}
        for data in record:
            row[data.name] = data.value
        records.append(row)

    df = pd.DataFrame(records)
    df['time'] = pd.to_datetime(df['timestamp'])

    if 'position_lat' in df.columns:
        df['latitude'] = df['position_lat'] * (180 / 2**31)
        df['longitude'] = df['position_long'] * (180 / 2**31)

    if 'speed' in df.columns:
        df['Pace_float'] = 16.6667 / df['speed']  # Convert m/s to min/km
        df['Avg_Pacemin/km'] = df['Pace_float'].apply(
            lambda x: f"{int(x)}:{int((x % 1) * 60):02}" if pd.notnull(x) else None
        )
    else:
        df['Pace_float'] = None
        df['Avg_Pacemin/km'] = None

    return df


import pandas as pd
import io
import csv

def parse_csv(file):
    raw = file.getvalue().decode("utf-8")
    dialect = csv.Sniffer().sniff(raw.splitlines()[0])
    df = pd.read_csv(io.StringIO(raw), delimiter=dialect.delimiter)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
    return df