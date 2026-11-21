FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Cài thư viện trước khi copy code để Docker dùng lại layer này khi chỉ sửa code.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Không chạy bằng root. Thư mục data/ chứa SQLite, được mount volume ở docker-compose.yml.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p data \
    && chown -R appuser:appuser data
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
