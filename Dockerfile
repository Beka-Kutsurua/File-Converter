FROM ghcr.io/python/cpython:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    tesseract-ocr \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p conversion/static/uploads conversion/static/converted

ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run"]
