# GSD HQ LMS — multi-arch image, runs on a Raspberry Pi 4B (arm64) via OMV Compose.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake the hashed static files into the image (no DB needed for this step).
RUN DATA_DIR=/tmp/build-data python manage.py collectstatic --noinput

# The SQLite DB and uploaded files live on the mounted volume at /data.
ENV DATA_DIR=/data
VOLUME /data

EXPOSE 8000
CMD ["python", "start.py"]
