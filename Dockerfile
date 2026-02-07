# ---- Base image ----
FROM python:3.12-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# System deps (optional but often helpful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ---- Install Python deps ----
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# ---- Copy app code ----
COPY . /code

# Cloud Run uses PORT env var; default to 8080 for local
ENV PORT=8080

# Expose port (mostly for local; Cloud Run ignores EXPOSE)
EXPOSE 8080

# Start server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
