FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["sh", "-c", "flask --app app init-db && gunicorn wsgi:application --bind 0.0.0.0:10000 --workers 3 --threads 2 --timeout 120"]
