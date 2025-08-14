# Multi-stage build to reduce final image size
FROM python:3.12-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download models and data
RUN python -m nltk.downloader wordnet omw-1.4 \
 && python -m spacy download en_core_web_sm \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Production stage - clean slate
FROM python:3.12-slim AS production

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/models \
    HF_HOME=/app/models \
    NLTK_DATA=/app/nltk_data \
    PATH="/app/.local/bin:$PATH"

# Only install runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/models /app/models
COPY --from=builder /app/nltk_data /app/nltk_data

# Create .dockerignore to exclude unnecessary files
# Copy only application code (make sure you have a .dockerignore)
COPY main.py .
COPY requirements.txt .
# Add other necessary files here, avoid copying everything with COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
 && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]