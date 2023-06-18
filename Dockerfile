# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requerimientos al contenedor
COPY requirements.txt .

# Instala las dependencias especificadas en el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual al directorio /app en el contenedor
COPY . .

# Expone el puerto 8501 para acceder a la aplicación Streamlit
EXPOSE 80

# Ejecuta el comando para iniciar la aplicación
CMD ["streamlit", "run", "--server.port", "80", "main.py"]