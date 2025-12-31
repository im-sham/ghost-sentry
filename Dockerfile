# Use Python 3.11 for Lattice SDK compatibility
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python project in editable mode
RUN pip install --no-cache-dir -e .

# Expose API port
EXPOSE 8000

# Run API by default
CMD ["uvicorn", "ghost_sentry.api:app", "--host", "0.0.0.0", "--port", "8000"]
