# Multi-stage Dockerfile for Fikrly Django Application
# Stage 1: Build stage
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    gettext \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install Python dependencies (copy only requirements to leverage cache)
COPY requirements.txt requirements-prod.txt ./
# Use explicit --no-cache-dir for deterministic installs and smaller layers
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-prod.txt


# Stage 2: Runtime stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    gettext \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder (system-wide)
COPY --from=builder /usr/local /usr/local

# Set working directory
WORKDIR /app

# Copy project files
COPY --chown=appuser:appuser . .

# Make scripts executable
RUN chmod +x docker/scripts/*.sh || true

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files (will be overridden by volume in production)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "myproject.wsgi:application"]
