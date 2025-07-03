import pandas as pd
import numpy as np
import requests
from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt

# === Configurazione ===
open_meteo_url = "https://api.open-meteo.com/v1/forecast"
lat_easybeer = 45.44859
lon_easybeer = 9.16068

# === Interfaccia Streamlit ===
st.set_page_config(page_title="Easy Meteo", layout="centered")

# Logo al posto del titolo
st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://github.com/Dagame71/meteo_easybeer/blob/main/Logo_EM.png?raw=true' width='300'>
    </div>
    """,
    unsafe_allow_html=True
)

# 🔄 Aggiornamento automatico ogni 5 minuti
st_autorefresh(interval=300000, key="meteo-refresh")

# === Funzione meteo ===
def scarica_meteo_openmeteo(lat, lon):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "precipitation", "cloudcover"],
            "forecast_days": 3,
            "current_weather": True,
            "timezone": "auto"
        }
        resp = requests.get(open_meteo_url, params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Errore meteo Open-Meteo: {e}")
        return None

# === Recupero dati meteo ===
openmeteo = scarica_meteo_openmeteo(lat_easybeer, lon_easybeer)

# === Striscia meteo attuale sotto il logo ===
if openmeteo and "current_weather" in openmeteo:
    meteo_attuale = openmeteo["current_weather"]
    temp_attuale = meteo_attuale["temperature"]
    codice_meteo = meteo_attuale["weathercode"]

    # Icona e descrizione in base al codice meteo (approssimativo)
    if codice_meteo in [0, 1]:
        icona = "☀️"
        descr_nuvole = "Sereno"
    elif codice_meteo in [2, 3]:
        icona = "⛅"
        descr_nuvole = "Poco nuvoloso"
    else:
        icona = "☁️"
        descr_nuvole = "Nuvoloso"

    # Precipitazione stimata dal primo dato orario
    precip_attuale = openmeteo["hourly"]["precipitation"][0] if "precipitation" in openmeteo["hourly"] else 0
    if precip_attuale > 0:
        pioggia = f" - 💧 {precip_attuale:.1f} mm di pioggia"
    else:
        pioggia = ""

    st.markdown(
        f"""
        <div style='text-align: center; padding: 10px; background-color: #f0f0f0; border-radius: 10px; margin-bottom: 20px;'>
            <b>{icona} {temp_attuale:.1f}°C - {descr_nuvole}{pioggia}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

# === Visualizzazione previsioni ===
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
    descrizione_precip = lambda x: f"{x:.1f} mm di pioggia" if x > 0 else ""

    oggi = datetime.now().date()
    ora_attuale = datetime.now()

    for giorno in giorni:
        if giorno == oggi:
            label = "Oggi"
        elif giorno == oggi + pd.Timedelta(days=1):
            label = "Domani"
        elif giorno == oggi + pd.Timedelta(days=2):
            label = "Dopodomani"
        else:
            label = giorno.strftime("%d/%m/%Y")

        with st.expander(f"Previsioni per {label}"):
            df_giorno = df[df["day"] == giorno]

            # Se è oggi, mostra solo le previsioni future rispetto all'ora attuale
            if giorno == oggi:
                df_giorno = df_giorno[df_giorno["time"] >= ora_attuale]

            if df_giorno.empty:
                st.write("Nessuna previsione disponibile per le prossime ore.")
            else:
                # Mostra grafico della temperatura
                st.write("Andamento temperatura:")
                plt.figure()
                plt.plot(df_giorno["hour"], df_giorno["temp"], marker="o")
                plt.title("Temperatura oraria")
                plt.ylabel("°C")
                plt.xticks(rotation=45)
                st.pyplot(plt)

                # Mostra previsioni con icone ed emoji
                for _, row in df_giorno.iterrows():
                    if row["cloud"] < 20:
                        icona = "☀️"
                    elif row["cloud"] < 50:
                        icona = "⛅"
                    else:
                        icona = "☁️"

                    descr_nuvole = descrizione_nuvole(row["cloud"])
                    descr_precip = descrizione_precip(row["precip"])

                    if row["precip"] > 0:
                        st.write(f"{row['hour']} - {row['temp']:.1f}°C - {icona} {descr_nuvole} - 💧 {descr_precip}")
                    else:
                        st.write(f"{row['hour']} - {row['temp']:.1f}°C - {icona} {descr_nuvole}")

else:
    st.error("Dati meteo non disponibili.")


