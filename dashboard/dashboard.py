import pandas as pd
import streamlit as st
import plotly.express as px

# Set konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Berbagi Sepeda",
    page_icon="🚲",
    layout="wide"
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    # Memuat dataset gabungan dari file CSV
    combined_df = pd.read_csv('dashboard/combined.csv')
    
    # Mengonversi kolom tanggal ke datetime
    combined_df['dteday'] = pd.to_datetime(combined_df['dteday'])
    
    # Memetakan kolom kategorikal
    season_map = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
    weathersit_map = {1: 'Cerah', 2: 'Berkabut', 3: 'Hujan/Salju Ringan', 4: 'Hujan/Salju Lebat'}
    weekday_map = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}
    
    combined_df['season_name'] = combined_df['season'].map(season_map)
    combined_df['weathersit_name'] = combined_df['weathersit'].map(weathersit_map)
    combined_df['weekday_name'] = combined_df['weekday'].map(weekday_map)
    
    # Membuat day_df dengan menggabungkan combined_df berdasarkan tanggal
    day_df = combined_df.groupby('dteday').agg({
        'season': 'first',
        'yr': 'first',
        'mnth': 'first',
        'holiday': 'first',
        'weekday': 'first',
        'workingday': 'first',
        'weathersit': 'first',
        'temp': 'mean',
        'atemp': 'mean',
        'hum': 'mean',
        'windspeed': 'mean',
        'cnt': 'sum',
        'casual': 'sum',
        'registered': 'sum',
        'season_name': 'first',
        'weathersit_name': 'first',
        'weekday_name': 'first'
    }).reset_index()
    
    return combined_df, day_df

# Memuat data
combined_df, day_df = load_data()

# Judul dan deskripsi
st.title("🚲 Dashboard Analisis Berbagi Sepeda")
st.markdown("""
Dashboard ini menyajikan analisis data berbagi sepeda untuk memahami pola penggunaan dan faktor-faktor yang mempengaruhi penyewaan sepeda.
""")

# Sidebar untuk filter
st.sidebar.header("Filter")

# Filter rentang tanggal
min_date = combined_df['dteday'].min().date()
max_date = combined_df['dteday'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Mengonversi ke datetime untuk filter
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Filter dataframe berdasarkan tanggal
filtered_combined_df = combined_df[(combined_df['dteday'] >= start_date) & (combined_df['dteday'] <= end_date)]

# Filter dan regenerasi day_df berdasarkan data gabungan yang difilter
filtered_day_df = filtered_combined_df.groupby('dteday').agg({
    'season': 'first',
    'yr': 'first',
    'mnth': 'first',
    'holiday': 'first',
    'weekday': 'first',
    'workingday': 'first',
    'weathersit': 'first',
    'temp': 'mean',
    'atemp': 'mean',
    'hum': 'mean',
    'windspeed': 'mean',
    'cnt': 'sum',
    'casual': 'sum',
    'registered': 'sum',
    'season_name': 'first',
    'weathersit_name': 'first',
    'weekday_name': 'first'
}).reset_index()

# Filter musim
selected_seasons = st.sidebar.multiselect(
    "Pilih musim",
    options=combined_df['season_name'].unique(),
    default=combined_df['season_name'].unique()
)

# Filter cuaca
selected_weather = st.sidebar.multiselect(
    "Pilih kondisi cuaca",
    options=combined_df['weathersit_name'].unique(),
    default=combined_df['weathersit_name'].unique()
)

# Menerapkan filter
if selected_seasons:
    filtered_combined_df = filtered_combined_df[filtered_combined_df['season_name'].isin(selected_seasons)]
    filtered_day_df = filtered_day_df[filtered_day_df['season_name'].isin(selected_seasons)]

if selected_weather:
    filtered_combined_df = filtered_combined_df[filtered_combined_df['weathersit_name'].isin(selected_weather)]
    filtered_day_df = filtered_day_df[filtered_day_df['weathersit_name'].isin(selected_weather)]

# Menampilkan metrik utama
st.header("Metrik Utama")
col1, col2, col3, col4 = st.columns(4)

total_rentals = filtered_day_df['cnt'].sum()
avg_daily_rentals = filtered_day_df['cnt'].mean()
max_daily_rentals = filtered_day_df['cnt'].max()
total_days = filtered_day_df.shape[0]

col1.metric("Total Penyewaan", f"{total_rentals:,}")
col2.metric("Rata-rata Penyewaan Harian", f"{avg_daily_rentals:.2f}")
col3.metric("Penyewaan Harian Maksimum", f"{max_daily_rentals:,}")
col4.metric("Jumlah Hari Dianalisis", f"{total_days}")

# Membuat tab untuk analisis berbeda
tab1, tab2, tab3 = st.tabs(["Analisis Musiman", "Pola Harian", "Dampak Cuaca"])

with tab1:
    st.header("Pola Penyewaan Sepeda Berdasarkan Musim")
    
    # Penyewaan berdasarkan musim
    seasonal_rentals = filtered_day_df.groupby('season_name')['cnt'].mean().reset_index()
    
    fig = px.bar(
        seasonal_rentals, 
        x='season_name', 
        y='cnt',
        color='season_name',
        labels={'cnt': 'Rata-rata Penyewaan', 'season_name': 'Musim'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Musim'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tren bulanan
    filtered_day_df['month'] = filtered_day_df['dteday'].dt.month
    filtered_day_df['month_name'] = filtered_day_df['dteday'].dt.strftime('%B')
    
    # Terjemahkan nama bulan ke Bahasa Indonesia
    month_map = {
        'January': 'Januari', 
        'February': 'Februari', 
        'March': 'Maret', 
        'April': 'April', 
        'May': 'Mei', 
        'June': 'Juni', 
        'July': 'Juli', 
        'August': 'Agustus', 
        'September': 'September', 
        'October': 'Oktober', 
        'November': 'November', 
        'December': 'Desember'
    }
    filtered_day_df['month_name_id'] = filtered_day_df['month_name'].map(month_map)
    
    monthly_rentals = filtered_day_df.groupby('month_name_id')['cnt'].mean().reset_index()
    
    # Pastikan bulan dalam urutan yang benar
    months_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    monthly_rentals['month_name_id'] = pd.Categorical(monthly_rentals['month_name_id'], categories=months_order)
    monthly_rentals = monthly_rentals.sort_values('month_name_id')
    
    fig = px.line(
        monthly_rentals, 
        x='month_name_id', 
        y='cnt',
        markers=True,
        labels={'cnt': 'Rata-rata Penyewaan', 'month_name_id': 'Bulan'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Bulan'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Pola Harian dan Per Jam")
    
    # Penyewaan berdasarkan jam
    hourly_rentals = filtered_combined_df.groupby('hr')['cnt'].mean().reset_index()
    
    fig = px.line(
        hourly_rentals, 
        x='hr', 
        y='cnt',
        markers=True,
        labels={'cnt': 'Rata-rata Penyewaan', 'hr': 'Jam'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Jam'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Penyewaan berdasarkan hari dalam seminggu
    weekday_rentals = filtered_day_df.groupby('weekday_name')['cnt'].mean().reset_index()
    
    # Pastikan hari dalam urutan yang benar
    days_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    weekday_rentals['weekday_name'] = pd.Categorical(weekday_rentals['weekday_name'], categories=days_order)
    weekday_rentals = weekday_rentals.sort_values('weekday_name')
    
    fig = px.bar(
        weekday_rentals, 
        x='weekday_name', 
        y='cnt',
        color='weekday_name',
        labels={'cnt': 'Rata-rata Penyewaan', 'weekday_name': 'Hari'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Hari'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap jam vs hari
    hourly_weekday = filtered_combined_df.groupby(['weekday_name', 'hr'])['cnt'].mean().reset_index()
    hourly_weekday_pivot = hourly_weekday.pivot(index='hr', columns='weekday_name', values='cnt')
    
    # Pastikan hari dalam urutan yang benar
    hourly_weekday_pivot = hourly_weekday_pivot[days_order]
    
    fig = px.imshow(
        hourly_weekday_pivot,
        labels=dict(x="Hari", y="Jam", color="Rata-rata Penyewaan"),
        x=hourly_weekday_pivot.columns,
        y=hourly_weekday_pivot.index,
        aspect="auto",
        title="Rata-rata Penyewaan Sepeda Berdasarkan Jam dan Hari"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Analisis Dampak Cuaca")
    
    # Penyewaan berdasarkan kondisi cuaca
    weather_rentals = filtered_day_df.groupby('weathersit_name')['cnt'].mean().reset_index()
    
    fig = px.bar(
        weather_rentals, 
        x='weathersit_name', 
        y='cnt',
        color='weathersit_name',
        labels={'cnt': 'Rata-rata Penyewaan', 'weathersit_name': 'Kondisi Cuaca'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Dampak suhu
    fig = px.scatter(
        filtered_day_df, 
        x='temp', 
        y='cnt',
        color='season_name',
        labels={'cnt': 'Total Penyewaan', 'temp': 'Suhu (Ternormalisasi)', 'season_name': 'Musim'},
        title='Penyewaan Sepeda vs. Suhu',
        trendline='ols'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Dampak kelembaban
    fig = px.scatter(
        filtered_day_df, 
        x='hum', 
        y='cnt',
        color='season_name',
        labels={'cnt': 'Total Penyewaan', 'hum': 'Kelembaban (Ternormalisasi)', 'season_name': 'Musim'},
        title='Penyewaan Sepeda vs. Kelembaban',
        trendline='ols'
    )
    st.plotly_chart(fig, use_container_width=True)

# Analisis Lanjutan - Bagian klasterisasi
st.header("Analisis Lanjutan: Pengelompokan Pola Penggunaan")

# Membuat fitur untuk klasterisasi
hour_features = filtered_combined_df.groupby('hr')['cnt'].mean().reset_index()
hour_features.columns = ['hour', 'avg_rentals']

# Klasterisasi manual berdasarkan pola per jam
# Mendefinisikan 4 klaster berdasarkan volume penyewaan
hour_features['cluster'] = pd.cut(
    hour_features['avg_rentals'],
    bins=4,
    labels=['Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi']
)

# Visualisasi klaster
fig = px.scatter(
    hour_features,
    x='hour',
    y='avg_rentals',
    color='cluster',
    labels={'hour': 'Jam', 'avg_rentals': 'Rata-rata Penyewaan', 'cluster': 'Tingkat Penggunaan'},
    title='Jam Dikelompokkan Berdasarkan Tingkat Penggunaan'
)
st.plotly_chart(fig, use_container_width=True)

# Menambahkan penjelasan untuk klaster
st.subheader("Analisis Klaster Per Jam")
st.write("""
Berdasarkan rata-rata penyewaan sepeda per jam, kita dapat mengidentifikasi pola penggunaan yang berbeda sepanjang hari:
- **Penggunaan Sangat Tinggi**: Jam-jam puncak ketika sistem berbagi sepeda mengalami permintaan maksimum
- **Penggunaan Tinggi**: Jam dengan permintaan yang signifikan tetapi tidak puncak
- **Penggunaan Sedang**: Periode permintaan moderat
- **Penggunaan Rendah**: Waktu ketika sedikit sepeda disewa, biasanya cocok untuk pemeliharaan dan redistribusi
""")

# Kesimpulan
st.header("Kesimpulan")
st.write("""
Berdasarkan analisis kami, dapat ditarik kesimpulan berikut tentang pola berbagi sepeda:

1. **Dampak Musiman**: 
   - Penyewaan sepeda tertinggi terjadi pada Musim Panas dan Musim Gugur, dengan penggunaan yang jauh lebih rendah di Musim Dingin.
   - Suhu memiliki korelasi positif yang kuat dengan penyewaan sepeda.

2. **Pola Harian**:
   - Penggunaan hari kerja menunjukkan pola perjalanan yang jelas dengan puncak selama jam sibuk pagi dan sore.
   - Penggunaan akhir pekan lebih merata sepanjang hari dengan satu puncak di tengah hari.

3. **Dampak Cuaca**:
   - Kondisi cuaca cerah menyebabkan penyewaan sepeda yang jauh lebih tinggi.
   - Kelembaban tinggi dan curah hujan berdampak negatif pada penggunaan sepeda.

4. **Rekomendasi**:
   - Optimalkan ketersediaan sepeda selama jam penggunaan puncak dengan memastikan sepeda yang cukup di stasiun populer.
   - Terapkan jadwal pemeliharaan selama jam penggunaan rendah untuk meminimalkan gangguan.
   - Pertimbangkan kampanye promosi selama musim dengan penggunaan lebih rendah untuk mendorong penyewaan.
   - Kembangkan strategi harga responsif cuaca untuk menyeimbangkan permintaan selama kondisi cuaca buruk.
""")

# Menambahkan footer dengan informasi pembuat
st.markdown("---")
st.markdown("Dibuat oleh Zidan Mubarak untuk Dicoding Indonesia - Belajar Analisis Data dengan Python")