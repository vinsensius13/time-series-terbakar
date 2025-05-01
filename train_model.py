import pandas as pd
from prophet import Prophet
import joblib

# === 1. Load data pengunjung ===
df = pd.read_csv("dataset_prophet_kunjungan_wisatawan.csv")
df.columns = ['ds', 'y']
df['ds'] = pd.to_datetime(df['ds'])
df['month'] = df['ds'].dt.to_period('M')

# === 2. Load dan proses data libur nasional ===
libur = pd.read_csv("holidays_2015_2026_nasional.csv")

if set(['holiday', 'ds', 'lower_window', 'upper_window']).issubset(libur.columns):
    libur = libur[['ds', 'holiday']]
else:
    libur = libur[['holiday_date', 'holiday_name', 'is_national_holiday']]
    libur.columns = ['ds', 'holiday', 'is_national']
    libur = libur[libur['is_national'] == True][['ds', 'holiday']]

libur['ds'] = pd.to_datetime(libur['ds'])
libur['month'] = libur['ds'].dt.to_period('M')

# === 3. Hitung jumlah libur per bulan dan gabungkan sebagai regressor ===
libur_per_bulan = libur.groupby('month').size().reset_index(name='libur_count')
df = pd.merge(df, libur_per_bulan, on='month', how='left')
df['libur_count'] = df['libur_count'].fillna(0)

# === 4. Buat model Prophet dengan regressor ===
model = Prophet()
model.add_regressor('libur_count')
model.fit(df[['ds', 'y', 'libur_count']])

# === 5. Simpan model ===
joblib.dump(model, "prophet_model_batam.pkl")

print("✅ Training selesai. Model dengan regressor disimpan sebagai 'prophet_model_batam.pkl'")
