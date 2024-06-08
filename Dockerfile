FROM python:3.9

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright
RUN pip3 install playwright
# RUN playwright install --with-deps chromium

# Set the working directory in the container
WORKDIR /app



COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the application files to the container
COPY . /app

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python3", "app.py"]