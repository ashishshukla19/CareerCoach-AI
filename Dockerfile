# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc ffmpeg curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the rest of the application code
COPY . /code

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]