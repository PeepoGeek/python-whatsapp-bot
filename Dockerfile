# Set base image (host OS)
FROM --platform=linux/amd64 python:3.12-alpine

# Por defecto, escucha en el puerto 5000
EXPOSE 5000/tcp

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de dependencias al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio local al directorio de trabajo
COPY . .

# Especifica el comando para ejecutar al iniciar el contenedor usando gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "run:app"]
