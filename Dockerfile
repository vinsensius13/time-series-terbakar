# === Gunakan image Python yang ringan ===
FROM python:3.10-slim

# === Set working directory ===
WORKDIR /app

# === Salin file requirements dan install dependencies ===
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# === Salin semua file project ke dalam container ===
COPY . .

# === Expose port yang digunakan FastAPI (harus sama dengan di CMD) ===
EXPOSE 8080

# === Perintah untuk menjalankan server saat container start ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
