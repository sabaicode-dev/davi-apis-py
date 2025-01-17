# Use the official Python image from the Docker Hub
FROM python:3.10.6-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Set environment variables for the Django application
COPY .env.development /app/.env

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
