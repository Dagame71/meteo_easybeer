
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import streamlit as st

# === Configurazione ===
open_meteo_url = "https://api.open-meteo.com/v1/forecast"
lat_easybeer = 45.44859
lon_easybeer = 9.16068

# === Funzioni ===
def scarica_meteo_openmeteo(lat, lon):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "precipitation", "cloudcover"],
            "forecast_days": 3,
            "timezone": "auto"
        }
        resp = requests.get(open_meteo_url, params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Errore meteo Open-Meteo: {e}")
        return None

# === Interfaccia Streamlit ===
st.set_page_config(page_title="Easy Meteo", layout="centered")
st.title("Easy Meteo")

openmeteo = scarica_meteo_openmeteo(lat_easybeer, lon_easybeer)

if openmeteo:
    df = pd.DataFrame({
        "time": pd.to_datetime(openmeteo["hourly"]["time"]),
        "temp": openmeteo["hourly"]["temperature_2m"],
        "precip": openmeteo["hourly"]["precipitation"],
        "cloud": openmeteo["hourly"]["cloudcover"]
    })

    df["day"] = df["time"].dt.date
    df["hour"] = df["time"].dt.strftime("%H:%M")

    giorni = df["day"].unique()

    descrizione_nuvole = lambda x: "Sereno" if x < 20 else "Poco nuvoloso" if x < 50 else "Molto nuvoloso"
    descrizione_precip = lambda x: "No precipitazioni" if x == 0 else f"{x:.1f} mm di pioggia"

    for giorno in giorni:
        with st.expander(f"Previsioni per il {giorno}"):
            df_giorno = df[df["day"] == giorno]

            for _, row in df_giorno.iterrows():
                descr_nuvole = descrizione_nuvole(row["cloud"])
                descr_precip = descrizione_precip(row["precip"])
                st.write(f"{row['hour']} - {row['temp']:.1f}°C - {descr_nuvole} - {descr_precip}")
else:
    st.error("Dati meteo non disponibili.")
