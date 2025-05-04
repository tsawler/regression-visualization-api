FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements first (for better cache utilization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify gunicorn is installed
RUN pip show gunicorn || (echo "Gunicorn not installed correctly" && exit 1)

COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default command for development
CMD ["python", "app.py"]