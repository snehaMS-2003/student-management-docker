# Use official Python slim runtime for minimal image footprint
FROM python:3.11-slim

# Set environment variables: avoid bytecode writing and unbuffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies if required (e.g. curl for health check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies first for efficient layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Expose Flask application port
EXPOSE 5000

# Run Flask application
CMD ["python", "run.py"]

