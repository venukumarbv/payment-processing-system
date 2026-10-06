# 1. Use a lightweight Python 3.10 image
FROM python:3.12-slim

# 2. Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures logs are sent straight to the terminal (no buffering)
ENV PYTHONUNBUFFERED=1
# Sets the Python path so 'from src.core...' imports work perfectly
ENV PYTHONPATH=/app/services/ingestion_service

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install System Dependencies for Microsoft ODBC Driver
# We need curl and gnupg2 to download the Microsoft keys
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unzip \
    ca-certificates \
    && curl -sS -O https://packages.microsoft.com/keys/microsoft.asc \
    && gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg microsoft.asc \
    && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. The command to start the microservice
CMD ["python", "services/ingestion_service/src/main.py"]
