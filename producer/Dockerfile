# Dockerfile for Producer

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run producer.py when the container launches
CMD ["python3", "producer.py", "--kafka-broker", "kafka1:9093"]

