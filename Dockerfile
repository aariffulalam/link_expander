# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# install git
RUN apt-get update && apt-get install -y git

# # Copy the current directory contents into the container
# COPY . /app

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Expose port 8000 for the FastAPI app
# EXPOSE 8000

# # Run the FastAPI app
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
