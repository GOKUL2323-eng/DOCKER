# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create persistent data directory and declare it as a volume
RUN mkdir -p /data
VOLUME ["/data"]

# Copy the requirements file from backend folder
COPY backend/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend folders into the container
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Set working directory to backend folder to run the server
WORKDIR /app/backend

# Create non-root user for security and grant permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /data
USER appuser

# Command to run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
