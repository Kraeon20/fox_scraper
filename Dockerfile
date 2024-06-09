FROM python:3.12-bookworm

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Install Playwright
RUN pip3 install playwright \
    playwright install --with-deps

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