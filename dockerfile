FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /var/www/kalinuxsec

# Копируем файлы приложения в контейнер
COPY ./kalinuxv1/kalinuxsec /var/www/kalinuxsec

# Устанавливаем зависимости системы
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apache2 \
    nginx \
    curl \
    unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r /var/www/kalinuxsec/requirements.txt

# Делаем файлы скриптов исполняемыми
RUN chmod +x /var/www/kalinuxsec/kalinux_security/static/public/download/tools/*

# Открываем необходимые порты
EXPOSE 80 443

# Указываем точку входа для запуска приложения
CMD ["gunicorn", "-k", "eventlet", "--workers", "10", "--bind", "unix:/var/www/kalinuxsec/kalidev.sock", "-m", "007", "app:app"]
