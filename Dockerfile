# 1. Base image
FROM python:3.11-slim

# 2. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Set working directory
WORKDIR /app

# 5. Copy only requirements first for caching
COPY requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy rest of the application code
COPY . .

# 8. Expose application port
EXPOSE 8000

# 9. Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

