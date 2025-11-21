FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/appdb
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

EXPOSE 8000 8501
