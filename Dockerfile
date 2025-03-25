# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD echo "Starting application..." && \
    echo "Environment variables:" && \
    env && \
    echo "Running uvicorn..." && \
    uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug 