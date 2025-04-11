FROM python:3.12-slim-bookworm AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    meson \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN  pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT [ "python","app.py" ]

