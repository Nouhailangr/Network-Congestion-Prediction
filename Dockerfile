# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install system dependencies for building Python packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    pkg-config \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install the required Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pandas openpyxl tensorflow
RUN pip install keras==3.4.1 tensorflow==2.17.0



# Copy the rest of the application code into the container
COPY . .

# Install dependencies
RUN pip install pytest flask

# Create results directory
RUN mkdir -p /test-results && chmod 777 /test-results

# Expose the port the app runs on
EXPOSE 5001

# Define the command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
