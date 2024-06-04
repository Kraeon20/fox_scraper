FROM mcr.microsoft.com/playwright:v1.43.0-jammy

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "app:app"]