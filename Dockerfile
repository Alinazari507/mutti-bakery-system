# Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="muttis-bakery@example.com"
LABEL description="Mutti's Bakery - Production Logic Prototype"
LABEL version="1.1"

# Working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY src/ ./src/
COPY data/ ./data/

# Create logs directory and initialize log file
RUN mkdir -p /app/logs && touch /app/logs/app.log

# Set environment variable for Python
ENV PYTHONPATH=/app

# Security: Create non-root system group and user
RUN groupadd -r bakery && useradd -r -g bakery bakery

# Change ownership of the app directory to the bakery user
RUN chown -R bakery:bakery /app

# Switch to non-root user
USER bakery

# Default command to run the application
CMD ["python", "src/main.py"]