FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Install build tools and common system dependencies
RUN apt-get update && apt-get install -y \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean

COPY . .

ENTRYPOINT [ "gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "app:app" ]