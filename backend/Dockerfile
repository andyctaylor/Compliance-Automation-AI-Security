# Development Dockerfile for Django backend
FROM python:3.13-slim-bookworm

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # PostgreSQL client for database connections
    postgresql-client \
    # Build dependencies for some Python packages
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    # Useful for debugging
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements/development.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application code
COPY . /app/

# Create directory for logs (HIPAA requirement)
RUN mkdir -p /app/logs

# Don't run as root (security best practice)
RUN useradd -m django && chown -R django:django /app
USER django

# Expose Django's default port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]