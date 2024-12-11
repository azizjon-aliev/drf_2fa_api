# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim-bookworm

# Set environment variables with a default value for DJANGO_ENV
ARG DJANGO_ENV=development

ENV DJANGO_ENV=${DJANGO_ENV} \
    PROJECT_DIR="/code" \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends --no-install-suggests -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR $PROJECT_DIR

# Copy the project files
COPY ./src ${PROJECT_DIR}/src/
COPY ./manage.py ${PROJECT_DIR}/
COPY ./scripts ${PROJECT_DIR}/scripts/
COPY ./requirements.txt ${PROJECT_DIR}/
COPY ./.env ${PROJECT_DIR}/

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Make the entrypoint script executable
RUN chmod +x ${PROJECT_DIR}/scripts/entrypoint.sh

# Expose the application port
EXPOSE 8000

# Define the entry point
CMD ["./scripts/entrypoint.sh"]
