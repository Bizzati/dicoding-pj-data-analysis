import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(
    page_title="Rental Bicycle Tren",
    page_icon="📊"
)
st.title("Rental Bicycle Trend 🚲")
st.markdown(
    """
    _The core data set is related to the two-year historical log 
    corresponding to years 2011 and 2012 from Capital Bikeshare system, Washington D.C., USA 
    which is publicly available in http://capitalbikeshare.com/system-data_
    """
)
df_day = pd.read_csv("https://raw.githubusercontent.com/Bizzati/dicoding-pj-data-analysis/refs/heads/main/Dashboard/main_day.csv")
df_hour = pd.read_csv("https://raw.githubusercontent.com/Bizzati/dicoding-pj-data-analysis/refs/heads/main/Dashboard/main_hour.csv")

# Mapping raw data
season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weather_map = {1: 'Clear', 2: 'Cloudy', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'}
workingday_map = {1: 'Working Day', 0: 'Weekend/Holiday'}

# Transformasi data
def transform_df(df, is_hourly=False):
    df['season'] = df['season'].map(season_map)
    df['workingday'] = df['workingday'].map(workingday_map)
    df['weathersit'] = df['weathersit'].map(weather_map)
    df['temp'] = df['temp'] * 41
    df['hum'] = df['hum'] * 100
    df['windspeed'] = df['windspeed'] * 67
    df = df.round(2)
    if is_hourly:
        df['hr'] = df['hr'].apply(lambda x: f"{x:02d}:00")
    return df

df_day = transform_df(df_day)
df_hour = transform_df(df_hour, is_hourly=True)

day_temp = df_day.copy()
hour_temp = df_hour.copy()
hour_temp.columns = ["date","season","hour","day status","weather","temp °C","humidity %", "windspeed Km/h","rents"] 
day_temp.columns = ["date","season","day status","weather","temp °C","humidity %", "windspeed Km/h","rents"]

st.write(
        """
        Dashboard ini akan menampilkan analisis trend jumlah rental sepeda berdasarkan hari, musim, dan cuaca. 
        Perlu diketahui data berikut ini telah dipilah sesuai kepentingan analisis.
        """
)
#Tampil Dataset
st.write("**Data Per Hari**")
with st.expander("Data preview"):
    st.write(day_temp)

st.write("**Data Per Jam**")
with st.expander("Data preview"):
    st.write(hour_temp)

st.subheader("Kondisi cuaca per musim")

season_avgs = df_day.groupby("season")["temp"].mean().reset_index()
season_avgs.columns = ["season", "avg_temp"]

# Plotting grafik suhu
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(season_avgs["season"], season_avgs["avg_temp"], color="#1f77b4")

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.1f}°C",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax.set_title("Rata-rata Suhu per Musim")
ax.set_xlabel("Musim")
ax.set_ylabel("Suhu Rata-Rata (°C)")
ax.grid(axis="y", linestyle="--", alpha=0.7)

st.pyplot(fig)

plt.figure(figsize=(12, 6))
sns.countplot(
    data=df_day,
    x='season',
    hue='weathersit',
    palette='viridis',
    order=['Fall','Spring', 'Summer', 'Winter']
)

# Plotting seasonal weather
plt.title('Distribusi Kondisi Cuaca per Musim', fontsize=14, pad=20)
plt.xlabel('Musim')
plt.ylabel('Jumlah Hari')
plt.grid(axis='y', linestyle='--', alpha=0.3)

plt.legend(
    title='Kondisi Cuaca',
    bbox_to_anchor=(1.05, 1),
    loc='upper left'
)

st.pyplot(plt.gcf())

st.header("Tren kondisi hari dengan penyewaan sepeda")

total_workday = df_day[df_day["workingday"] == "Working Day"].shape[0]
total_weekend = df_day[df_day["workingday"] == "Weekend/Holiday"].shape[0]
total_workday_rentals = df_day[df_day["workingday"] == "Working Day"]["cnt"].sum()
total_weekend_rentals = df_day[df_day["workingday"] == "Weekend/Holiday"]["cnt"].sum()
mean_workday_rentals = total_workday_rentals / total_workday
mean_weekend_rentals = total_weekend_rentals / total_weekend

labels = [
    f"Workday\n({total_workday_rentals} days)\n{mean_workday_rentals:.0f} rentals/hari",
    f"Holiday\n({total_weekend_rentals} days)\n{mean_weekend_rentals:.0f} rentals/hari"
]

colors = ['#1f77b4', '#ff7f0e']
explode = (0.05, 0)

# Plot pie chart
fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(
    [mean_workday_rentals, mean_weekend_rentals],
    labels=labels,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    explode=explode,
    shadow=True,
    textprops={'fontsize': 10}
)

ax.set_title('Perbandingan Rata-Rata Penyewaan Sepeda per Hari:\nHari Kerja vs Hari Libur', fontsize=12, pad=20)
ax.axis('equal')

st.pyplot(fig)

st.subheader("Tren pemakaian sepeda dalam sehari")

df_hour['season'] = df_hour['season'].astype(str)
df_hour['weathersit'] = df_hour['weathersit'].astype(str)
df_hour = pd.concat([df_hour, df_hour.assign(season='All')])
df_hour = pd.concat([df_hour, df_hour.assign(weathersit='All')])

# dropdown
col1, col2 = st.columns(2)
selected_season = col1.selectbox("Pilih Musim", options=df_hour['season'].unique(), index=0)
selected_weather = col2.selectbox("Pilih Kondisi Cuaca", options=df_hour['weathersit'].unique(), index=0)
filtered_data = df_hour[(df_hour['season'] == selected_season) & (df_hour['weathersit'] == selected_weather)]
hourly_avg = filtered_data.groupby(["hr", "workingday"])["cnt"].mean().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(
    data=hourly_avg,
    x="hr",
    y="cnt",
    hue="workingday",
    palette=["#ff7f0e", "#1f77b4"],
    style="workingday",
    markers=True,
    dashes=False,
    linewidth=2.5
)

# Plotting graf per hari
plt.title(f"Penyewaan Sepeda dalam rentang hari (Musim: {selected_season}, Cuaca: {selected_weather})")
plt.xlabel("Jam", fontsize=12)
plt.ylabel("Rata-rata Penyewaan Sepeda", fontsize=12)
plt.xticks(range(24), [f"{h:02d}:00" for h in range(24)], rotation=45)
plt.ylim(0, 800)
plt.grid(linestyle='--', alpha=0.7)
plt.legend(title="Hari", labels=["Hari Libur", "Hari Kerja"], loc="upper left")

st.pyplot(plt)