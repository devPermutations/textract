# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Build a minimal image running the ExtractText FastAPI server on port 6060
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system-level dependencies required by pdf2image, Tesseract & Poppler
# NOTE: You may wish to tailor these packages to your distro size/performance.
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        poppler-utils \
        libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Python dependencies
# Copy dependency descriptors first for efficient Docker layer caching.
# ---------------------------------------------------------------------------
COPY requirements.txt pyproject.toml README.md ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Copy the rest of the source code and install the package itself
# ---------------------------------------------------------------------------
COPY . .

RUN pip install --no-cache-dir --editable .

# Expose the FastAPI port
EXPOSE 6060

# ---------------------------------------------------------------------------
# Start the server
# ---------------------------------------------------------------------------
CMD ["uvicorn", "extracttext.server:app", "--host", "0.0.0.0", "--port", "6060"] 