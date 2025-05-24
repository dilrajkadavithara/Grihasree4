# Use the official Python image.
FROM python:3.11-slim

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies (for mysqlclient, Pillow, etc.)
RUN apt-get update && \
    apt-get install -y gcc pkg-config default-libmysqlclient-dev libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of your project files into the container
COPY . /app/

# Collect static files for WhiteNoise
RUN python manage.py collectstatic --noinput

# The port Railway expects
EXPOSE 8000

# Start the Django application with Gunicorn
CMD gunicorn grihasree_project.wsgi:application --bind 0.0.0.0:8000
