# Specify Ubuntu 22.04 as the base image of our Docker container
FROM ubuntu:22.04

# Set a non-interactive frontend for apt (prevents tzdata from prompting)
ENV DEBIAN_FRONTEND=noninteractive

# Update and upgrade packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y wget gnupg2 software-properties-common curl

# Add deadsnakes PPA to install Python 3.12
# Replace with the Python version you have used for this project
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.12 python3-pip

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install a virtual environment:
RUN pip install virtualenv
RUN virtualenv /opt/venv

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Environment variable to detect Docker
ENV DOCKER_ENV=true  

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY src/ /app

# Install any needed packages specified in requirements.txt
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run main.py when the container launches
CMD ["python", "main.py"]