FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN  pip install --no-cache-dir -r requirements.txt
COPY . .
#ENTRYPOINT [ "python", "app.py"] 
ENTRYPOINT [ "gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "app:app"]

