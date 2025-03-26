FROM mcr.microsoft.com/devcontainers/python:3.10

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
