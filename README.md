# 🧭 API Prediksi Kunjungan Wisatawan Bulanan (Prophet + FastAPI)

Proyek ini membangun REST API menggunakan FastAPI untuk memprediksi jumlah kunjungan wisatawan ke suatu lokasi (contoh: Kota Batam) berdasarkan data time series bulanan dan pengaruh hari libur nasional.

Model utama yang digunakan adalah **Facebook Prophet**, dengan tambahan regresor berupa jumlah libur nasional setiap bulan (`libur_count`).

---

## 🚀 Fitur

- Prediksi jumlah kunjungan `n` bulan ke depan.
- Insight perbandingan prediksi saat ada libur vs. tidak ada libur.
- Plot prediksi dalam bentuk grafik.
- Response real-time via FastAPI.

---

## 🏗️ Arsitektur

- **Model**: Prophet (dilatih dengan data kunjungan wisata dan libur nasional)
- **Backend**: FastAPI
- **Input Tambahan**: Regressor jumlah libur nasional (`libur_count`) per bulan

---

## 🔌 API Endpoint

### 🔮 `POST /predict`

Prediksi jumlah kunjungan wisatawan untuk beberapa bulan ke depan.

**Request Body**:
```json
{
  "periods": 6
}
Response:


[
  {
    "ds": "2025-01-31",
    "yhat": 74000.5,
    "yhat_lower": 51000.2,
    "yhat_upper": 97000.8
  },
  ...
]
💡 GET /insight?periods=6
Memberikan insight prediksi berdasarkan jumlah hari libur nasional tiap bulan.

Query Param:

periods: jumlah bulan yang akan diprediksi dan dianalisis (default = 12)

Response:

{
  "total_bulan_dengan_libur": 4,
  "total_bulan_tanpa_libur": 2,
  "rata_rata_prediksi_bulan_ada_libur": 72000.53,
  "rata_rata_prediksi_bulan_tidak_ada_libur": 68000.42,
  "insight": "Prediksi kunjungan cenderung lebih tinggi saat ada libur nasional."
}
📈 GET /plot?periods=6
Menghasilkan grafik plot prediksi dalam format PNG.

Query Param:

periods: jumlah bulan yang diplot (default = 12)

Response:

File gambar image/png yang berisi grafik hasil prediksi Prophet

🏥 GET /
Health check endpoint untuk mengetahui apakah API aktif:

{
  "message": "API Time Series Forecasting Aktif 🚀"
}

🧪 Contoh Curl
# Prediksi 6 bulan ke depan
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"periods": 6}'

# Ambil insight prediksi
curl http://localhost:8080/insight?periods=6

# Download plot prediksi
curl http://localhost:8080/plot?periods=6 --output plot.png

📝 Catatan Tambahan
Periode prediksi (periods) bisa antara 1 hingga 36 bulan.

Model dapat dilatih ulang dengan train_model.py jika dataset baru tersedia.

Untuk visualisasi di frontend, endpoint /plot bisa langsung ditampilkan sebagai gambar.