# Use an official Python image as a base
FROM --platform=linux/amd64 python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    sudo \
    && rm -rf /var/lib/apt/lists/*
    
# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo ./aws/install \
    && rm -rf awscliv2.zip

# Install any additional dependencies for your application
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Expose the port for your app
EXPOSE 5001

# Command to run the app
CMD ["python", "app.py"]
