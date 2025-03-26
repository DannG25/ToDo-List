FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

# dependencias del sistema a instalar
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# dependencias de Python a instalar
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Permisos para la base de datos SQLite
RUN mkdir -p /var/lib/sqlite && \
    touch /code/db.sqlite3 && \
    chmod 777 /code/db.sqlite3

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Copiar el proyecto
COPY . .


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Si usas requirements-dev para desarrollo
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Puerto
EXPOSE 8000