# Dockerfile
# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the action files
COPY requirements.txt /app/requirements.txt
COPY src/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Run the main script as the entry point
ENTRYPOINT ["python", "/app/src/entrypoint.py"]
