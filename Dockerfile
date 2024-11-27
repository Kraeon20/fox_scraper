FROM python:3.10.7

# Install necessary system dependencies
# RUN apt-get update && apt-get install -y \
#     curl \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install Playwright and its dependencies
RUN pip install playwright
RUN playwright install
# RUN playwright install-deps chromium
RUN playwright install-deps

# Copy the rest of the application files to the container
COPY . /app

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "app:app", "-b", ":8000", "--timeout", "600", "--workers=3", "--threads=3", "--worker-connections=1000", "--worker-class=gevent"]