FROM python:3.12-slim AS base

# Prevent interactive prompts & set up cache dirs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/models \
    HF_HOME=/app/models \
    NLTK_DATA=/app/nltk_data

# Install only necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install --upgrade pip
# Install Python dependencies first (for build caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download all required data/models in one layer
RUN python -m nltk.downloader wordnet omw-1.4 \
 && python -m spacy download en_core_web_sm \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy only necessary files (avoid copying .git, venv, __pycache__)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]