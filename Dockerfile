# Use the official Python image from the Docker Hub
FROM python:3.10.6-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy only requirements first to leverage docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Set environment variables for the Django application
COPY .env.development /app/.env

# Expose the port the app runs on
EXPOSE 8000

# Use a non-root user
RUN addgroup --system django && \
    adduser --system --ingroup django django

# Change ownership of the app directory
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
