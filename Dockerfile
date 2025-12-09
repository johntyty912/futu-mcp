# Multi-stage Docker build for Futu MCP Server
FROM python:3.12-slim AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy uv from builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy installed dependencies from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src ./src
COPY pyproject.toml ./

# Create non-root user for security
RUN useradd -m -u 1000 futu && \
    chown -R futu:futu /app

# Switch to non-root user
USER futu

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    FUTU_HOST=host.docker.internal \
    FUTU_PORT=11111

# Note: stdio mode doesn't expose ports or use health checks
# The server communicates via stdin/stdout with MCP clients

# Run the server in stdio mode
CMD ["python", "-m", "futu_mcp.server"]
