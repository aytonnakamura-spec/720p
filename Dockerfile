FROM python:3.11-slim

WORKDIR /app

# FFmpeg এবং অন্যান্য প্রয়োজনীয় টুল ইনস্টল করা
RUN apt-get update && apt-get install -y ffmpeg curl && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Gunicorn রান করা (৫ মিনিট টাইমআউট সহ যাতে বড় ভিডিওর সময় এরর না আসে)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]
