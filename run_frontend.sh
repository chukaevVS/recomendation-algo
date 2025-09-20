#!/bin/bash

# Скрипт для запуска фронтенда рекомендательной системы

echo "🎨 ЗАПУСК ФРОНТЕНДА РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ"
echo "=" * 50

# Проверяем, что мы в правильной директории
if [ ! -d "frontend" ]; then
    echo "❌ Папка frontend не найдена. Запустите скрипт из корня проекта."
    exit 1
fi

# Переходим в папку фронтенда
cd frontend

# Проверяем наличие package.json
if [ ! -f "package.json" ]; then
    echo "❌ Файл package.json не найден в папке frontend"
    exit 1
fi

# Проверяем наличие node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Установка зависимостей..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей"
        exit 1
    fi
fi

# Проверяем, что API сервер запущен
echo "🔍 Проверка API сервера..."
if curl -s http://localhost:3002/health > /dev/null; then
    echo "✅ API сервер доступен на порту 3002"
else
    echo "⚠️  API сервер недоступен на порту 3002"
    echo "💡 Запустите API сервер командой: python3 app.py"
    echo "⏳ Продолжаем запуск фронтенда..."
fi

echo ""
echo "🚀 Запуск фронтенда..."
echo "📱 Приложение будет доступно по адресу: http://localhost:3000"
echo "🔗 API сервер должен быть запущен на: http://localhost:3002"
echo ""
echo "⏹️  Для остановки нажмите Ctrl+C"
echo "=" * 50

# Запускаем фронтенд
npm start
