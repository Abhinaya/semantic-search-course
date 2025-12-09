# Multi-stage build for Product Search API
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies only (not the package itself)
RUN uv pip install --system fastapi uvicorn[standard] elasticsearch pydantic pydantic-settings python-dotenv

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check - just check if server responds (don't check ES or index)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
