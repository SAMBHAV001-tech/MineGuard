# Use official lightweight Python 3.10 base image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (needed for rasterio, numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port (Render maps this automatically)
EXPOSE 10000

# Command to run the app
# 👇 Change "app.main:app" to your FastAPI app location if different
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
