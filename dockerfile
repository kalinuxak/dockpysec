FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости системы
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY ./flaskapp /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create directory for Gunicorn socket
RUN mkdir -p /var/run/flaskapp && \
    chmod 755 /var/run/flaskapp

# Expose the application port (if needed)
EXPOSE 5000

# Указываем точку входа для запуска приложения
CMD ["gunicorn", "-k", "eventlet", "--workers", "10", "--bind", "unix:/var/www/kalinuxsec/kalidev.sock", "-m", "007", "app:app"]
