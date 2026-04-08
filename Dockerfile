# Instrucciones para Docker
# Usa una imagen base de Python 3.10
FROM mcr.microsoft.com/devcontainers/python:3.10

# Installar dependencias del sistema
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
