# Dockerfile
FROM python:3.9.18-bullseye

# Expose port
EXPOSE 8000

# Enable Python buffered write
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Change working directory
WORKDIR /app

# Copy requirements-production.txt file to install
COPY ./requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Copy necessary files
COPY . .

# Run Django server directly
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000","src.asgi:application"]
# Dockerfile
FROM python:3.9.18-bullseye

# Expose port
EXPOSE 8000

# Enable Python buffered write
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Change working directory
WORKDIR /app

# Copy requirements-production.txt file to install
COPY ./requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Copy necessary files
COPY . .

# Run Django server directly
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000","src.asgi:application"]
