# ChaosCore API Gateway - Multi-Architecture Dockerfile
# Supports AMD64 and ARM64 architectures

# Build stage
FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder

# Set build arguments
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH

# Print build info
RUN echo "Building on $BUILDPLATFORM for $TARGETPLATFORM ($TARGETOS/$TARGETARCH)"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Build wheel packages for dependencies
RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt

# Final stage
FROM --platform=$TARGETPLATFORM python:3.12-slim

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app && adduser --system --group app

# Copy wheels and application code
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/ /app/

# Install Python packages
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Change ownership to the non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set labels
LABEL org.opencontainers.image.title="ChaosCore API Gateway" \
      org.opencontainers.image.description="API Gateway for ChaosCore platform" \
      org.opencontainers.image.version="0.1.1" \
      org.opencontainers.image.source="https://github.com/ChaosChain/chaoschain-governance-os" \
      org.opencontainers.image.authors="ChaosChain Labs" \
      org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      org.opencontainers.image.architecture="${TARGETARCH}" \
      maintainer="ChaosChain Labs <info@chaoschain.org>"

# Start the application
CMD ["python", "-m", "uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"] 