# Sample Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libkrb5-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install arcgis --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt



COPY . .

EXPOSE 5000

CMD python app.py