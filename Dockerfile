# Use official Python 3.10 image
FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Set work directory
WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 5000

# Start the app using Gunicorn
CMD ["gunicorn", "backend.app:app", "--bind", "0.0.0.0:5000"]
