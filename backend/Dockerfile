FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    libx11-xcb1 \
    libxrender1 \
    libxfixes3 \
    libxcursor1 \
    libxinerama1 \
    libxcb-dri3-0 \
    libxcb-shm0 \
    libpci3 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install .
RUN python -m playwright install chromium

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
