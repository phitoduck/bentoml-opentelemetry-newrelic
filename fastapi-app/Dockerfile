# Use the official Python 3.9 image as a parent image
FROM python:3.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV DOWNSTREAM_API_TARGETS=""
ENV PYTHONUNBUFFERED=1

# Copy the local requirements.txt file to the container
COPY ./requirements.txt ./

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the container
COPY ./ ./

# Specify the command to run on container start
# CMD ["opentelemetry-instrument", "--", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--log-level", "info",]
CMD opentelemetry-instrument -- gunicorn -k uvicorn.workers.UvicornWorker main:APP --bind "0.0.0.0:8000" --log-level "info"
