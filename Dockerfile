# ---- Build Stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
FROM python:3.12-slim

WORKDIR /app
# Create a non-root user and group
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

# Copy only installed packages and app code
COPY --from=builder /install /usr/local
COPY . .

RUN chown -R appuser:appuser /app

# Clean up unnecessary files
RUN  apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER appuser

ENTRYPOINT [ "gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "app:app" ]
    