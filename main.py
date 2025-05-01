from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from prophet import Prophet
import pandas as pd
import joblib
import os
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import io

app = FastAPI()

# === Health check ===
@app.get("/")
def root():
    return {"message": "API Time Series Forecasting Aktif 🚀"}

# === Load Model ===
MODEL_PATH = "prophet_model_batam.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file '{MODEL_PATH}' tidak ditemukan.")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Gagal load model: {e}")

# === Load Libur Nasional ===
HOLIDAY_PATH = "holidays_2015_2026_nasional.csv"
try:
    holidays = pd.read_csv(HOLIDAY_PATH)
    holidays = holidays[['holiday', 'ds']]
    holidays['ds'] = pd.to_datetime(holidays['ds'])
    holidays['month'] = holidays['ds'].dt.to_period('M')
    libur_count_per_month = holidays.groupby('month').size().reset_index(name='libur_count')
except Exception:
    holidays = pd.DataFrame(columns=['holiday', 'ds', 'month'])
    libur_count_per_month = pd.DataFrame(columns=['month', 'libur_count'])

# === Request Schema ===
class PredictRequest(BaseModel):
    periods: int = 12

# === Helper: Tambah regresor libur ===
def enrich_with_libur(df):
    df['month'] = df['ds'].dt.to_period('M')
    df = pd.merge(df, libur_count_per_month, on='month', how='left')
    df['libur_count'] = df['libur_count'].fillna(0)
    return df

# === Endpoint: Prediksi Kunjungan ===
@app.post("/predict")
def predict(req: PredictRequest):
    if req.periods < 1 or req.periods > 36:
        raise HTTPException(status_code=400, detail="Periods harus antara 1 dan 36 bulan.")
    try:
        future = model.make_future_dataframe(periods=req.periods, freq='M')
        future = enrich_with_libur(future)
        forecast = model.predict(future)
        hasil = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(req.periods)
        return hasil.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan prediksi: {e}")

# === Endpoint: Insight Libur Nasional ===
@app.get("/insight")
def insight(periods: int = Query(12, ge=1, le=36)):
    try:
        future = model.make_future_dataframe(periods=periods, freq='M')
        future = enrich_with_libur(future)
        forecast = model.predict(future)
        forecast['month'] = forecast['ds'].dt.to_period('M')

        merged = forecast[['month', 'yhat', 'libur_count']]

        with_libur = merged[merged['libur_count'] > 0]
        without_libur = merged[merged['libur_count'] == 0]

        avg_with = with_libur['yhat'].mean() if not with_libur.empty else 0
        avg_without = without_libur['yhat'].mean() if not without_libur.empty else 0

        insight_msg = (
            "Prediksi kunjungan cenderung lebih tinggi saat ada libur nasional."
            if avg_with > avg_without else
            "Libur nasional tidak terlalu berpengaruh signifikan terhadap lonjakan kunjungan."
        )

        return {
            "total_bulan_dengan_libur": len(with_libur),
            "total_bulan_tanpa_libur": len(without_libur),
            "rata_rata_prediksi_bulan_ada_libur": round(avg_with, 2),
            "rata_rata_prediksi_bulan_tidak_ada_libur": round(avg_without, 2),
            "insight": insight_msg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menganalisis insight: {e}")

# === Endpoint: Plot Grafik ===
@app.get("/plot")
def plot_prediction(periods: int = Query(12, ge=1, le=36)):
    try:
        future = model.make_future_dataframe(periods=periods, freq='M')
        future = enrich_with_libur(future)
        forecast = model.predict(future)

        fig = model.plot(forecast)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat plot: {e}")
