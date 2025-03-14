import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Load data
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

# Sidebar untuk filter
st.sidebar.header("Filter Data")

# Filter tanggal
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

min_date = df_day['dteday'].min()
max_date = df_day['dteday'].max()

start_date = st.sidebar.date_input("Tanggal Mulai", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Tanggal Akhir", max_date, min_value=min_date, max_value=max_date)

# Filter musim dan cuaca
selected_season = st.sidebar.selectbox(
    "Pilih Musim",
    options=['All'] + list(df_day['season'].unique()),
    index=0
)

selected_weather = st.sidebar.selectbox(
    "Pilih Kondisi Cuaca",
    options=['All'] + list(df_day['weathersit'].unique()),
    index=0
)

# Filter data berdasarkan pilihan
filtered_day = df_day[(df_day['dteday'] >= pd.to_datetime(start_date)) & (df_day['dteday'] <= pd.to_datetime(end_date))]
filtered_hour = df_hour[(df_hour['dteday'] >= pd.to_datetime(start_date)) & (df_hour['dteday'] <= pd.to_datetime(end_date))]

if selected_season != 'All':
    filtered_day = filtered_day[filtered_day['season'] == selected_season]
    filtered_hour = filtered_hour[filtered_hour['season'] == selected_season]

if selected_weather != 'All':
    filtered_day = filtered_day[filtered_day['weathersit'] == selected_weather]
    filtered_hour = filtered_hour[filtered_hour['weathersit'] == selected_weather]

# Tampil Dataset
st.write("**Data Per Hari**")
with st.expander("Data preview"):
    st.write(filtered_day)

st.write("**Data Per Jam**")
with st.expander("Data preview"):
    st.write(filtered_hour)

# Grafik Suhu per Musim
st.subheader("Rata-rata Suhu per Musim")
season_avgs = filtered_day.groupby("season")["temp"].mean().reset_index()
season_avgs.columns = ["season", "avg_temp"]

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

ax.set_title(f"Rata-rata Suhu per Musim (Filter: {selected_season}, {selected_weather})")
ax.set_xlabel("Musim")
ax.set_ylabel("Suhu Rata-Rata (°C)")
ax.grid(axis="y", linestyle="--", alpha=0.7)

st.pyplot(fig)

# Korelasi jumlah rental dengan musim dan cuaca
avg_rentals = filtered_day.groupby(["season", "weathersit"])["cnt"].mean().reset_index()

pivot_table = avg_rentals.pivot(index="season", columns="weathersit", values="cnt")

pivot_table.plot(kind="bar", figsize=(8, 5))

plt.xlabel("Musim")
plt.ylabel("Rata-rata Jumlah Rental")
plt.title("Rata-rata Jumlah Rental Berdasarkan Musim dan Cuaca")
plt.legend(title="Kondisi Cuaca")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.show()

st.pyplot(plt.gcf())

# Pie Chart Perbandingan Hari Kerja vs Libur 
st.header("Rata-rata penyewaan sepeda berdasarkan hari kerja vs hari libur")

total_workday = filtered_day[filtered_day["workingday"] == "Working Day"].shape[0]
total_weekend = filtered_day[filtered_day["workingday"] == "Weekend/Holiday"].shape[0]
total_workday_rentals = filtered_day[filtered_day["workingday"] == "Working Day"]["cnt"].sum()
total_weekend_rentals = filtered_day[filtered_day["workingday"] == "Weekend/Holiday"]["cnt"].sum()
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

ax.set_title('Perbandingan Penyewaan', fontsize=12, pad=20)
ax.axis('equal')

st.pyplot(fig)

# Grafik Tren Harian (Per Jam)
st.subheader("Pola Pemakaian Sepeda dalam Sehari")
hourly_avg = filtered_hour.groupby(["hr", "workingday"])["cnt"].mean().reset_index()

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

plt.title(f"Penyewaan Sepeda (Filter: {selected_season}, {selected_weather})")
plt.xlabel("Jam", fontsize=12)
plt.ylabel("Rata-rata Penyewaan Sepeda", fontsize=12)
plt.xticks(range(24), [f"{h:02d}:00" for h in range(24)], rotation=45)
plt.ylim(0, 800)
plt.grid(linestyle='--', alpha=0.7)
plt.legend(title="Hari", labels=["Hari Libur", "Hari Kerja"], loc="upper left")

st.pyplot(plt)
