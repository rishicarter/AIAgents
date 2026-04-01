# Use slim Python image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies (no dev)
ENV UV_NO_DEV=1

RUN uv sync --locked

# 👇 IMPORTANT: make venv python default
ENV PATH="/app/.venv/bin:$PATH"

# Run your app WITHOUT uv
CMD ["python", "-m", "app.main"]