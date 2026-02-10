# Dockerfile: Management Layer
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (for psycopg2/grpc)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose HTTP and gRPC ports
EXPOSE 8000
EXPOSE 50051

# Start script
CMD ["sh", "-c", "python main.py"]
