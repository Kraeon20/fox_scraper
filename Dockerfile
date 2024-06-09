FROM python:3.10.7

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the application files to the container
COPY . /app

# Install Playwright
RUN pip install playwright
RUN playwright install
RUN playwright install-deps

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]