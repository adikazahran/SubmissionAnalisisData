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
st.sidebar.header("📊 Bike Sharing Report")
pilih_analisis = st.sidebar.radio(
    "📈 Pilih Analisis:",
    ("Pola Aktivitas Per Jam", "Korelasi Antar Variabel")
)
tampil_data = st.sidebar.checkbox("🧾 Show Raw Data", value=False)
st.sidebar.markdown("---")
st.sidebar.markdown("👤 **Muhammad Adika Zahran**")

# Tab untuk Pola Aktivitas Per Hours
tab_dashboard, tab_insight = st.tabs(["📊 Dashboard Utama", "💡 Tentang & Insight"])
if pilih_analisis == "Pola Aktivitas Per Jam":
    with tab_insight:
        st.markdown("""
        ## 📝 Tentang Dashboard
        Pertanyaan Analisis:
        
        1. 🚀 **Pola Aktivitas Per Jam**  
           Bagaimana pola aktivitas per jam dalam hour.csv berbeda antara hari kerja dan akhir pekan, serta jam berapa saja yang merupakan puncak dan masa sepi dalam periode data terakhir?            
        """)
    
    if bike_icon:
        st_lottie(bike_icon, height=200, key="bike")
    st.header("🕒 Pola Aktivitas Per Jam")

    try:
        hour_df = pd.read_csv('data/hour.csv')
        hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
        hour_df['day_of_week'] = hour_df['dteday'].dt.dayofweek
        hour_df['is_weekend'] = hour_df['day_of_week'] >= 5

        summary = hour_df.groupby(['hr', 'is_weekend'])['cnt'].mean().reset_index()
        summary['day_type'] = np.where(summary['is_weekend'], 'Weekend', 'Weekday')

        fig, ax = plt.subplots(figsize=(10,6))
        sns.lineplot(data=summary, x='hr', y='cnt', hue='day_type', marker='o', ax=ax)
        ax.set_title("🚲 Aktivitas Per Jam: Weekday vs. Weekend")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata Aktivitas")
        ax.set_xticks(range(0,24))
        st.pyplot(fig)

        overall = hour_df.groupby("hr")['cnt'].mean()
        peak = overall.idxmax()
        quiet = overall.idxmin()
        peak_count = overall.max()
        quiet_count = overall.min()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚀 Peak Hour", f"Jam {peak}", f"{peak_count:.0f} peminjaman")
        with col2:
            st.metric("🌙 Quiet Hour", f"Jam {quiet}", f"{quiet_count:.0f} peminjaman")

        if tampil_data:
            st.subheader("📊 Data Summary Hourly")
            st.dataframe(summary)
    except FileNotFoundError:
        st.error("❌ File *hour.csv* tidak ditemukan. Pastikan file ada di folder `data`.")
    except pd.errors.ParserError:
        st.error("⚠️ File *hour.csv* tidak bisa diproses. Periksa format dan struktur datanya.")
    except Exception as e:
        st.error(f"⚠️ Terjadi kesalahan: {e}")

    st.markdown("""
            ## 📊 Insight 
            - **Pola Aktivitas Per Jam :** Analisis menunjukkan bahwa aktivitas mencapai puncaknya pada jam 17 (5 sore), yang menandakan waktu ideal untuk memaksimalkan layanan, mengoptimalkan sumber daya, dan meluncurkan promosi guna menangani lonjakan permintaan. Sebaliknya, jam 4 pagi merupakan waktu dengan aktivitas paling rendah, sehingga sangat tepat untuk melakukan pemeliharaan sistem atau update tanpa mengganggu pengalaman pelanggan.        
            """)

            
# Tab untuk Korelasi Antar Variabel
if pilih_analisis == "Korelasi Antar Variabel":
    with tab_insight:
        st.markdown("""
        ## 📝 Tentang Dashboard
        Pertanyaan Analisis:

        2. 📊 **Korelasi Antar Variabel**  
        Bagaimana hubungan antar variabel dalam day.csv dan hour.csv, dan bagaimana korelasi tersebut dapat memberikan insight untuk perbaikan strategi bisnis?
        
        """)

    st.header("🔗 Korelasi Antar Variabel")
    if bike_icon:
        st_lottie(bike_icon, height=200, key="bike")
        
    try:
        day_df = pd.read_csv('data/day.csv')
        day_df['dteday'] = pd.to_datetime(day_df['dteday'])
        corr_day = day_df.corr(numeric_only=True)

        st.subheader("🌡️ Matriks Korelasi - Data Harian (day.csv)")
        fig_day, ax_day = plt.subplots(figsize=(10,8))
        sns.heatmap(corr_day, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_day)
        st.pyplot(fig_day)

        hour_df = pd.read_csv('data/hour.csv')
        corr_hour = hour_df.corr(numeric_only=True)

        st.subheader("🌡️ Matriks Korelasi - Data Per Jam (hour.csv)")
        fig_hour, ax_hour = plt.subplots(figsize=(10,8))
        sns.heatmap(corr_hour, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_hour)
        st.pyplot(fig_hour)

        if tampil_data:
            st.subheader("📊 Matriks Korelasi Mentah")
            st.dataframe(corr_day)
            st.dataframe(corr_hour)
    except FileNotFoundError:
        st.error("❌ File *day.csv* atau *hour.csv* tidak ditemukan.")
    except pd.errors.ParserError:
        st.error("⚠️ File tidak bisa diproses. Periksa format datanya.")
    except Exception as e:
        st.error(f"⚠️ Terjadi kesalahan: {e}")

    st.markdown("""
        ## 📊 Insight 
        - **Korelasi Antar Variabel :** Suhu (temp) dan jumlah pengguna (cnt) memiliki korelasi positif, artinya semakin hangat suhu, semakin banyak peminjaman sepeda. Sebaliknya, kelembaban tinggi (hum) sedikit mengurangi aktivitas peminjaman.
        """)

with st.expander("📚 Lihat Penjelasan Tambahan"):
    st.markdown("""
        **📈 Dashboard Interaktif:**  
        Dashboard ini dirancang untuk mengeksplorasi data Bike Sharing. Gunakan kontrol di sidebar untuk memilih analisis yang ingin dilihat. Data mentah bisa ditampilkan dengan mencentang opsi yang tersedia.
        """)