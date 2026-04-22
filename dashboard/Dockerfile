FROM python:3.12-slim

# Avoid .pyc and force unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build deps for psycopg2-binary compilation fallback (usually not needed,
# but keeps the image resilient if the wheel isn't available for the arch).
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Install only the runtime deps the dashboard actually needs. Avoids pulling
# the full Airflow stack from requirements.txt into this image.
RUN pip install \
      streamlit==1.56.0 \
      pandas==3.0.2 \
      plotly==6.7.0 \
      SQLAlchemy==2.0.49 \
      psycopg2-binary==2.9.11 \
      python-dotenv==1.2.2

# Copy the Streamlit app in last so source edits don't bust the pip cache layer.
COPY app.py /app/app.py

EXPOSE 8501

# Healthcheck hits Streamlit's built-in endpoint.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
