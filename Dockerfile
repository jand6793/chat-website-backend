# Use an official Python 3.11 runtime as a base image
FROM python:3.11

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    postgresql \
    postgresql-contrib

# Set the working directory in the container to /app
WORKDIR /chat-website-backend

# Clone the repository
RUN git clone https://github.com/jand6793/chat-website-backend.git

# Copy requirements.txt to the working directory
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Make the container's port 8000 available to the outside world
EXPOSE 8000

# Start PostgreSQL service and setup the database and start the server
CMD service postgresql start && python src/app/database/connection/setup.py && uvicorn src.app.api.server:app
