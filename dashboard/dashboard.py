import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_lottie import st_lottie 
import requests

# Fungsi untuk memuat animasi Lottie
def load_lottieurl(url):
    try:
        r = requests.get(url)
        r.raise_for_status()  
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Gagal memuat animasi: {e}")
        return None

# Load ikon animasi
bike_icon = load_lottieurl('https://assets9.lottiefiles.com/packages/lf20_fcfjwiyb.json')

# Judul Dashboard
st.title("🚲 Dashboard Analisis Data Bike Sharing")

# Sidebar untuk navigasi dan kontrol
st.sidebar.header("📊 Filter Data")
st.sidebar.markdown("**Pilih Rentang Tanggal:**")

# Memuat data
try:
    hour_df = pd.read_csv('data/hour.csv')
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    min_date = hour_df['dteday'].min()
    max_date = hour_df['dteday'].max()

    # Filter tanggal interaktif
    start_date, end_date = st.sidebar.date_input(
        "Rentang Tanggal:", [min_date, max_date], min_value=min_date, max_value=max_date
    )

    # Filter tambahan: musim dan cuaca
    st.sidebar.markdown("**Filter Tambahan:**")
    season_options = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_options = {1: 'Clear', 2: 'Cloudy', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'}

    selected_season = st.sidebar.multiselect("Musim:", options=season_options.values(), default=season_options.values())
    selected_weather = st.sidebar.multiselect("Cuaca:", options=weather_options.values(), default=weather_options.values())

    # Mapping filter ke dataset
    reverse_season = {v: k for k, v in season_options.items()}
    reverse_weather = {v: k for k, v in weather_options.items()}

    filtered_df = hour_df[(hour_df['dteday'] >= pd.Timestamp(start_date)) & (hour_df['dteday'] <= pd.Timestamp(end_date))]
    filtered_df = filtered_df[filtered_df['season'].isin([reverse_season[s] for s in selected_season])]
    filtered_df = filtered_df[filtered_df['weathersit'].isin([reverse_weather[w] for w in selected_weather])]

    st.sidebar.markdown("---")
    st.sidebar.markdown("👤 **Muhammad Adika Zahran**")

    # Visualisasi Pola Aktivitas Per Jam
    st.header("🕒 Pola Aktivitas Per Jam")

    filtered_df['day_of_week'] = filtered_df['dteday'].dt.dayofweek
    filtered_df['is_weekend'] = filtered_df['day_of_week'] >= 5

    summary = filtered_df.groupby(['hr', 'is_weekend'])['cnt'].mean().reset_index()
    summary['day_type'] = np.where(summary['is_weekend'], 'Weekend', 'Weekday')

    fig, ax = plt.subplots(figsize=(10,6))
    sns.lineplot(data=summary, x='hr', y='cnt', hue='day_type', marker='o', ax=ax)
    ax.set_title("🚲 Aktivitas Per Jam: Weekday vs. Weekend")
    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata Aktivitas")
    ax.set_xticks(range(0,24))
    st.pyplot(fig)

    # Peak dan Quiet Hour
    overall = filtered_df.groupby("hr")['cnt'].mean()
    peak = overall.idxmax()
    quiet = overall.idxmin()
    peak_count = overall.max()
    quiet_count = overall.min()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🚀 Peak Hour", f"Jam {peak}", f"{peak_count:.0f} peminjaman")
    with col2:
        st.metric("🌙 Quiet Hour", f"Jam {quiet}", f"{quiet_count:.0f} peminjaman")

    # Korelasi Antar Variabel
    st.header("🔗 Korelasi Antar Variabel")
    corr_hour = filtered_df.corr(numeric_only=True)

    fig_hour, ax_hour = plt.subplots(figsize=(10,8))
    sns.heatmap(corr_hour, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_hour)
    st.pyplot(fig_hour)

    with st.expander("📚 Lihat Penjelasan Tambahan"):
        st.markdown("""
        **📈 Dashboard Interaktif:**  
        Dashboard ini dirancang untuk mengeksplorasi data Bike Sharing. Gunakan sidebar untuk memilih rentang tanggal, musim, dan cuaca yang ingin dilihat. Semua visualisasi akan otomatis terupdate berdasarkan filter yang dipilih.
        """)

except FileNotFoundError:
    st.error("❌ File *hour.csv* tidak ditemukan. Pastikan file ada di folder `data`.")
except pd.errors.ParserError:
    st.error("⚠️ File *hour.csv* tidak bisa diproses. Periksa format dan struktur datanya.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")
