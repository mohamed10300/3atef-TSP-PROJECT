FROM python:3.11-slim

WORKDIR /app

# System deps: build tools + PostgreSQL client + Chromium browser dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    # Playwright / Chromium system libraries
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libx11-6 libx11-xcb1 libxcb1 libxext6 \
    libxi6 libxtst6 ca-certificates fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install browser binaries only (system deps already installed above)
RUN python -m playwright install chromium

COPY backend/ ./backend/

RUN mkdir -p backend/reports backend/uploads

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
