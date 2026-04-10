# Instrucciones para Docker
# Usa una imagen base de Python 3.10 "slim", un version ligera de python para servidores
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y fuerza a que la consola muestre los prints en tiempo real
ENV PYTTHONDONTWRITEBUTECODE=1
ENV PYTHONUNBUFFERED=1

# Se crear una carpeta de trabajo dentro del contenedor
WORKDIR /app

# Instalmos solamente el archivo de dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del codigo en el contenedor
COPY . .

# El comando por defecto que ejecutara el contenedor al encenderse
CMD ["python", "main.py"]
