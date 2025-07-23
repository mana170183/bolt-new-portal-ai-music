FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    gnupg \
    lsb-release \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    && rm -rf /var/lib/apt/lists/*

# Configure FreeTDS for SQL Server connectivity  
RUN echo "[FreeTDS]\nDescription = v0.95 with protocol v7.2\nDriver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\nUsageCount = 1" > /etc/odbcinst.ini

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for audio output
RUN mkdir -p /app/generated_audio && chmod 755 /app/generated_audio
RUN mkdir -p /tmp/generated_audio && chmod 755 /tmp/generated_audio

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]