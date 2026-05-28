# Используем легковесный и стабильный образ Python
FROM python:3.12-slim

# Настраиваем переменные окружения, чтобы Python не создавал .pyc файлы 
# и сразу выводил логи в терминал (без буферизации)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные библиотеки, необходимые для сборки pillow и работы с сетью
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Обновляем менеджер пакетов pip
RUN pip install --no-cache-dir --upgrade pip

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем все библиотеки из вашего списка
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта в контейнер
COPY . .

# Открываем стандартный порт
EXPOSE 8000

# Запускаем проект через uvicorn (замените profguide.asgi на ваше имя, если оно отличается)
CMD ["uvicorn", "profguide.wsgi:application", "--host", "0.0.0.0", "--port", "8000", "--interface", "wsgi"]