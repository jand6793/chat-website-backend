# Use an official Python 3.11 runtime as a base image
FROM python:3.11

# Set the working directory in the container to /chat-website-backend
WORKDIR /chat-website-backend

# Set build-time variables
ARG POSTGRES_PASSWORD
ARG BACKEND_PASSWORD

# Set environment variables
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV BACKEND_PASSWORD=${BACKEND_PASSWORD}

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    postgresql \
    postgresql-contrib \
    sudo

# Create a directory for the postgres database
RUN mkdir -p /var/run/postgresql && chown -R postgres:postgres /var/run/postgresql

# # Clone the repository
RUN git clone https://github.com/APills/KUCS351Group2.git
RUN git checkout website-gui

# Copy the rest of the application code to the working directory
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Make the container's ports 8000 and 5432 available to the outside world
EXPOSE 8000 5432

# Set the password for the 'postgres' user, create backend user, and setup the database
RUN chmod +x setup.sh
RUN chmod +x run_server.sh

# Start the postgresql server, and start the application
CMD cd /chat-website-backend && ./setup.sh && ./run_server.sh
# CMD ["sh", "-c", "/chat-website-backend/setup.sh && /chat-website-backend/run_server.sh"]
