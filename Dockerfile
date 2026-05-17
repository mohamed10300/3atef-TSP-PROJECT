FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install chromium --with-deps

COPY backend/ ./backend/

RUN mkdir -p backend/reports backend/uploads

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
