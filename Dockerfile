FROM python:3.12-slim

# Prevent Python from writing .pyc files
# and ensure logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application directory inside the container.
WORKDIR /app

# Install system dependencies required by
# common Python scientific/ML packages.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specification first.
# This allows Docker to cache the dependency layer.
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY src/ ./src/
COPY database/ ./database/
COPY tests/ ./tests/

# Copy the retrieval/data artifacts required
# by the application.
COPY data/ ./data/

# Expose FastAPI/Uvicorn port.
EXPOSE 8000

# Start the API.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]