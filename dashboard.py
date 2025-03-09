import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Fungsi untuk memuat data (gunakan cache agar lebih cepat)
@st.cache
def load_data():
    df_day = pd.read_csv("data/day.csv")
    df_hour = pd.read_csv("data/hour.csv")
    df_day['dteday'] = pd.to_datetime(df_day['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    return df_day, df_hour

df_day, df_hour = load_data()

# Mapping untuk musim dan kondisi cuaca
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_mapping = {1: "Clear", 2: "Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}

# Menambahkan kolom 'Season' dan 'Weather' ke df_day
df_day["Season"] = df_day["season"].map(season_mapping)
df_day["Weather"] = df_day["weathersit"].map(weather_mapping)

# Judul Aplikasi
st.title("Analisis Data Penyewaan Sepeda")
st.markdown("Dashboard interaktif untuk mengeksplorasi data penyewaan sepeda.")

# Pilihan analisis di sidebar
analisis = st.sidebar.selectbox(
    "Pilih Analisis:",
    ("Analisis Musim dan Cuaca", "Analisis Hari Kerja vs Akhir Pekan", "Heatmap Korelasi")
)

if analisis == "Analisis Musim dan Cuaca":
    st.header("Analisis Musim dan Cuaca")
    
    # Hitung rata-rata penyewaan berdasarkan musim dan kondisi cuaca
    avg_rentals = df_day.groupby(["season", "weathersit"])["cnt"].mean().reset_index()
    avg_rentals["Season"] = avg_rentals["season"].map(season_mapping)
    avg_rentals["Weather"] = avg_rentals["weathersit"].map(weather_mapping)
    
    # Membuat tabel pivot
    pivot_table = avg_rentals.pivot(index="Season", columns="Weather", values="cnt")
    st.subheader("Tabel Pivot: Rata-rata Penyewaan (dalam unit)")
    st.dataframe(pivot_table.style.format("{:.1f}"))
    
    # Plot batang
    fig, ax = plt.subplots(figsize=(8,5))
    pivot_table.plot(kind="bar", ax=ax)
    ax.set_xlabel("Musim")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.set_title("Rata-rata Penyewaan Berdasarkan Musim dan Cuaca")
    ax.legend(title="Kondisi Cuaca")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    st.pyplot(fig)
    
elif analisis == "Analisis Hari Kerja vs Akhir Pekan":
    st.header("Analisis Hari Kerja vs Akhir Pekan")
    
    # Analisis menggunakan df_day (data harian)
    total_workday = df_day[df_day["workingday"] == 1]["cnt"].sum()
    total_weekend = df_day[df_day["workingday"] == 0]["cnt"].sum()
    mean_workday = total_workday / df_day[df_day["workingday"] == 1].shape[0]
    mean_weekend = total_weekend / df_day[df_day["workingday"] == 0].shape[0]
    
    # Buat DataFrame analisis
    workday_analysis = pd.DataFrame({
        "Kategori": ["Hari Kerja", "Akhir Pekan"],
        "Jumlah Hari": [df_day[df_day["workingday"] == 1].shape[0], df_day[df_day["workingday"] == 0].shape[0]],
        "Total Penyewaan": [total_workday, total_weekend],
        "Rata-rata Penyewaan per Hari": [mean_workday, mean_weekend]
    })
    
    st.subheader("Tabel Analisis Hari Kerja vs Akhir Pekan")
    st.dataframe(workday_analysis.style.format({"Rata-rata Penyewaan per Hari": "{:.1f}"}))
    
    # Pie Chart: Persentase rata-rata penyewaan
    fig1, ax1 = plt.subplots(figsize=(6,6))
    labels = workday_analysis["Kategori"]
    sizes = workday_analysis["Rata-rata Penyewaan per Hari"]
    # Gunakan explode untuk menekankan hari kerja jika diinginkan
    explode = (0.1, 0)
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", explode=explode, startangle=90, colors=["skyblue", "salmon"])
    ax1.set_title("Persentase Rata-rata Penyewaan per Hari")
    st.pyplot(fig1)
    
    # Bar Chart: Rata-rata penyewaan per hari
    fig2, ax2 = plt.subplots(figsize=(6,5))
    ax2.bar(workday_analysis["Kategori"], workday_analysis["Rata-rata Penyewaan per Hari"], color=["skyblue", "salmon"])
    ax2.set_xlabel("Kategori Hari")
    ax2.set_ylabel("Rata-rata Penyewaan")
    ax2.set_title("Rata-rata Penyewaan Hari Kerja vs Akhir Pekan")
    for i, v in enumerate(workday_analysis["Rata-rata Penyewaan per Hari"]):
        ax2.text(i, v + 50, f"{v:.1f}", ha="center", fontsize=10)
    st.pyplot(fig2)
    
elif analisis == "Heatmap Korelasi":
    st.header("Heatmap Korelasi")
    
    # Hitung korelasi antar variabel
    corr = df_day[["cnt", "season", "weathersit", "temp", "hum", "windspeed"]].corr()
    fig3, ax3 = plt.subplots(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax3, linewidths=0.5)
    ax3.set_title("Heatmap Korelasi")
    st.pyplot(fig3)
    
# Menampilkan insight
st.markdown("### Insight:")
st.markdown("""
- **Analisis Musim dan Cuaca:**  
  Rata-rata penyewaan sepeda tertinggi terjadi pada musim tertentu dengan kondisi cuaca cerah. Tabel pivot dan grafik batang menunjukkan bahwa cuaca yang baik secara konsisten meningkatkan penyewaan di berbagai musim.

- **Analisis Hari Kerja vs Akhir Pekan:**  
  Meskipun total penyewaan pada hari kerja lebih tinggi karena jumlah hari kerja yang lebih banyak, rata-rata penyewaan per hari tidak jauh berbeda antara hari kerja dan akhir pekan. Ini menunjukkan bahwa sepeda digunakan untuk keperluan komuter sekaligus aktivitas rekreasi.

- **Heatmap Korelasi:**  
  Korelasi positif yang kuat antara suhu (temp) dan penyewaan, serta korelasi negatif antara kelembapan (hum) dan penyewaan, mengindikasikan bahwa cuaca yang nyaman (hangat dan kering) sangat mendukung penggunaan sepeda.
""")
