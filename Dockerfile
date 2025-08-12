FROM python:3.12-slim as base

# Prevent interactive prompts & set up cache dirs
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=true \
    PYTHONUNBUFFERED=1

# Install only necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (use requirements for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download all required data/models in one layer
RUN python -m nltk.downloader wordnet omw-1.4 \
 && python -m spacy download en_core_web_sm \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

# CMD ["python", "main.py"]

# ---------- EXTRA ----------
# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]