# 🛍️ Рекомендательная система для интернет-магазина

Простая и эффективная рекомендательная система с поддержкой базы данных, использующая алгоритм k-NN (k ближайших соседей) для предоставления персонализированных рекомендаций товаров в интернет-магазине.

## 📋 Содержание

- [Особенности](#особенности)
- [Технологический стек](#технологический-стек)
- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Генерация данных](#генерация-данных)
- [Создание базы данных](#создание-базы-данных)
- [Запуск системы](#запуск-системы)
- [API документация](#api-документация)
- [Архитектура системы](#архитектура-системы)
- [Примеры использования](#примеры-использования)
- [Конфигурация](#конфигурация)
- [Настройка PostgreSQL](#настройка-postgresql)
- [Устранение неполадок](#устранение-неполадок)
- [Вклад в проект](#вклад-в-проект)

## ✨ Особенности

- 🤖 **k-NN алгоритм**: Использует проверенный алгоритм машинного обучения
- 👥 **User-based рекомендации**: Рекомендации на основе похожих пользователей
- 📦 **Item-based рекомендации**: Рекомендации на основе похожих товаров
- 🗄️ **Поддержка БД**: SQLite и PostgreSQL
- 🔄 **Дообучение модели**: Автоматическое обновление рекомендаций при добавлении данных
- 🌐 **RESTful API**: Готовый к использованию веб-API
- 📊 **Аналитика**: Статистика и анализ данных
- 🔧 **Легкая настройка**: Простая конфигурация параметров
- 📈 **Масштабируемость**: Поддержка больших объемов данных

## 🛠 Технологический стек

- **Python 3.8+**
- **NumPy** - математические операции
- **Pandas** - работа с данными
- **Scikit-learn** - алгоритмы машинного обучения
- **Flask** - веб-фреймворк для API
- **Flask-CORS** - поддержка CORS
- **SQLAlchemy** - ORM для работы с БД
- **SQLite/PostgreSQL** - базы данных

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Генерация тестовых данных

```bash
python data_generator/ecommerce_data_generator.py
```

### 3. Создание базы данных

```bash
python src/database/db_models.py
```

### 4. Запуск системы

```bash
# Запуск API сервера
python app.py

# Или демонстрация системы
python app.py --mode demo
```

**API доступен по адресу:** http://localhost:3002

## 📦 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/recommendation-system.git
cd recommendation-system
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

**Основные зависимости:**
- pandas
- numpy
- scikit-learn
- flask
- flask-cors
- sqlalchemy
- psycopg2-binary (для PostgreSQL)

## 🎯 Генерация данных

### Автоматическая генерация тестовых данных

```bash
python data_generator/ecommerce_data_generator.py
```

**Результат:**
- `data/users.csv` - 1000 пользователей с демографическими данными
- `data/products.csv` - 500 товаров из 6 категорий (Смартфоны, Ноутбуки, Планшеты, Наушники, Умные часы, Фототехника)
- `data/ratings.csv` - 20000+ рейтингов с реалистичными предпочтениями

**Статистика:**
```
📊 Статистика:
  - Средний рейтинг: 4.47
  - Плотность матрицы: 0.0401
  - Категории товаров: 6
  - Бренды: 17
```

## 🗄️ Создание базы данных

### Автоматическое создание из CSV

```bash
python src/database/db_models.py
```

**Результат:**
- `data/recommendations.db` - SQLite база данных
- Таблицы: users, products, ratings
- Все данные загружены из CSV файлов

### Проверка базы данных

```bash
sqlite3 data/recommendations.db
.tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM ratings;
.quit
```

## 🚀 Запуск системы

### Единая точка входа

```bash
# Запуск API сервера (по умолчанию)
python app.py

# Запуск API сервера на другом порту
python app.py --port 8080

# Запуск с PostgreSQL
python app.py --database postgresql://user:pass@localhost/recommendations

# Запуск без автоматического обучения модели
python app.py --no-auto-load

# Запуск в режиме отладки
python app.py --debug

# Демонстрация системы
python app.py --mode demo
```

### Параметры запуска

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--mode` | Режим: api или demo | api |
| `--database` | URL базы данных | SQLite |
| `--host` | Хост для API | 0.0.0.0 |
| `--port` | Порт для API | 3002 |
| `--debug` | Режим отладки | False |
| `--approach` | user_based или item_based | user_based |
| `--neighbors` | Количество соседей | 15 |

## 🌐 API документация

### Базовые эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Информация об API |
| GET | `/health` | Проверка состояния |
| GET | `/stats` | Статистика системы |
| GET | `/db-stats` | Статистика базы данных |

### Рекомендации

| Метод | URL | Описание | Параметры |
|-------|-----|----------|-----------|
| GET | `/users/{user_id}/recommendations` | Рекомендации для пользователя | `n_recommendations`, `include_metadata` |
| GET | `/users/{user_id}/similar` | Похожие пользователи | `n_similar` |
| GET | `/users/{user_id}/profile` | Профиль пользователя | - |
| GET | `/products/{product_id}/similar` | Похожие товары | `n_similar` |
| GET | `/products/popular` | Популярные товары | `n_items` |

### Управление данными

| Метод | URL | Описание | Тело запроса |
|-------|-----|----------|--------------|
| POST | `/ratings` | Добавить рейтинг | `{"user_id": 1, "product_id": 10, "rating": 4.5}` |
| POST | `/products` | Добавить товар | `{"product_id": 501, "name": "iPhone 15", "category": "Смартфоны", "price": 89999}` |
| POST | `/users` | Добавить пользователя | `{"user_id": 1001, "name": "Иван", "email": "ivan@example.com"}` |
| POST | `/retrain` | Переобучить модель | Query: `force=true`, `async=true` |
| POST | `/ratings/batch` | Добавить несколько рейтингов | `{"ratings": [...]}` |
| POST | `/products/batch` | Добавить несколько товаров | `{"products": [...]}` |

### Примеры API запросов

```bash
# Получить рекомендации
curl "http://localhost:3002/users/1/recommendations?n_recommendations=5"

# Добавить рейтинг
curl -X POST "http://localhost:3002/ratings" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "product_id": 10, "rating": 4.5, "review": "Отлично!"}'

# Добавить новый товар
curl -X POST "http://localhost:3002/products" \
     -H "Content-Type: application/json" \
     -d '{
       "product_id": 503,
       "name": "MacBook Pro M3",
       "category": "Ноутбуки",
       "price": 149999.99,
       "brand": "Apple"
     }'

# Переобучить модель
curl -X POST "http://localhost:3002/retrain?force=true&async=true"
```

## 🏗️ Архитектура системы

### Структура проекта

```
recomendation-algo/
├── app.py                           # Единая точка входа
├── requirements.txt                 # Зависимости
├── data/                           # Данные
│   ├── users.csv                   # Пользователи
│   ├── products.csv                # Товары
│   ├── ratings.csv                 # Рейтинги
│   └── recommendations.db          # SQLite БД
├── data_generator/                 # Генератор данных
│   └── ecommerce_data_generator.py
├── src/                            # Исходный код
│   ├── models/                     # Модели данных
│   │   └── data_models.py
│   ├── algorithms/                 # Алгоритмы рекомендаций
│   │   └── knn_recommender.py
│   ├── database/                   # Модули БД
│   │   ├── db_models.py            # Модели БД
│   │   └── db_loader.py            # Загрузчик БД
│   ├── api/                        # Web API
│   │   └── flask_api_db.py         # API с БД
│   └── recommendation_system_db.py # Система с БД
└── docs/                           # Документация
    └── ARCHITECTURE.md             # Архитектура системы
```

### Компоненты системы

1. **RecommendationSystemDB** - Основной класс системы
2. **HybridDataManager** - Управление данными с кэшированием
3. **DatabaseManager** - Работа с базой данных
4. **KNNRecommender** - Алгоритм рекомендаций
5. **RecommendationAPIDB** - RESTful API
6. **Data Models** - Модели данных (User, Product, Rating)

## 💻 Примеры использования

### Программное использование

```python
from src.recommendation_system_db import RecommendationSystemDB

# Создание системы с автоматической загрузкой данных
system = RecommendationSystemDB(
    database_url=None,  # SQLite по умолчанию
    approach='user_based',
    n_neighbors=15,
    auto_load=True  # Автоматически загрузить данные и обучить модель
)

# Получение рекомендаций
recommendations = system.get_recommendations(user_id=1, n_recommendations=10)

# Добавление нового товара
from src.models.data_models import Product
new_product = Product(
    product_id=504,
    name="AirPods Pro 2",
    category="Наушники",
    price=24999.99,
    brand="Apple"
)
system.add_product(new_product)

# Переобучение модели
system.retrain_model()
```

### Работа с API

```python
import requests

# Получение рекомендаций
response = requests.get("http://localhost:3002/users/1/recommendations")
recommendations = response.json()

# Добавление рейтинга
rating_data = {
    "user_id": 1,
    "product_id": 504,
    "rating": 4.5,
    "review": "Отличные наушники!"
}
response = requests.post("http://localhost:3002/ratings", json=rating_data)

# Переобучение модели
response = requests.post("http://localhost:3002/retrain?force=true&async=true")
```

## ⚙️ Конфигурация

### Параметры системы

```python
system = RecommendationSystemDB(
    database_url=None,              # URL базы данных
    approach='user_based',          # 'user_based' или 'item_based'
    n_neighbors=15,                 # Количество соседей (5-30 оптимально)
    metric='cosine',                # Метрика схожести
    min_ratings=5,                  # Минимум рейтингов для учета
    auto_load=True                  # Автоматическая загрузка данных
)
```

### Рекомендуемые параметры

| Размер данных | n_neighbors | approach | metric |
|---------------|-------------|----------|--------|
| < 1000 пользователей | 5-10 | user_based | cosine |
| 1000-10000 пользователей | 10-20 | user_based | cosine |
| > 10000 пользователей | 15-30 | item_based | cosine |

## 🐘 Настройка PostgreSQL

### 1. Установка PostgreSQL

```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Создание базы данных

```sql
-- Подключение к PostgreSQL
psql -U postgres

-- Создание базы данных
CREATE DATABASE recommendations;
CREATE USER rec_user WITH PASSWORD 'rec_password';
GRANT ALL PRIVILEGES ON DATABASE recommendations TO rec_user;

-- Подключение к новой базе
\c recommendations rec_user
```

### 3. Использование PostgreSQL в системе

```bash
# Запуск с PostgreSQL
python app.py --database postgresql://rec_user:rec_password@localhost:5432/recommendations
```

### 4. Загрузка данных в PostgreSQL

```python
from src.database.db_models import create_database_from_csv

# Создание БД PostgreSQL из CSV
database_url = "postgresql://rec_user:rec_password@localhost:5432/recommendations"
db_manager = create_database_from_csv(
    users_csv="data/users.csv",
    products_csv="data/products.csv", 
    ratings_csv="data/ratings.csv",
    database_url=database_url
)
```

## 🧪 Тестирование

### Автоматическое тестирование

```bash
# Демонстрация системы
python app.py --mode demo

# Тестирование API
python examples/api_db_test.py
```

### Ручное тестирование

```bash
# Проверка состояния системы
curl http://localhost:3002/health
curl http://localhost:3002/stats

# Получение рекомендаций
curl "http://localhost:3002/users/1/recommendations?n_recommendations=5"
```

## 🚨 Устранение неполадок

### Проблемы с БД

**Ошибка:** `database is locked`
```bash
# Остановить все процессы, использующие БД
pkill -f flask_api_db.py
rm -f data/recommendations.db
python src/database/db_models.py
```

**Ошибка:** `table already exists`
```bash
# Пересоздать БД
rm -f data/recommendations.db
python src/database/db_models.py
```

### Проблемы с API

**Ошибка:** `Port already in use`
```bash
# Найти и остановить процесс
lsof -ti:3002 | xargs kill -9
python app.py
```

**Ошибка:** `Module not found`
```bash
# Проверить PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python app.py
```

## 🧮 Алгоритм

### k-NN (k Nearest Neighbors)

Система использует алгоритм k ближайших соседей для создания рекомендаций:

#### User-based подход:
1. **Построение матрицы пользователь-товар** из рейтингов
2. **Центрирование данных** (вычитание среднего рейтинга пользователя)
3. **Поиск k похожих пользователей** с помощью метрики схожести
4. **Предсказание рейтинга** как взвешенное среднее рейтингов соседей
5. **Генерация рекомендаций** на основе предсказанных рейтингов

#### Item-based подход:
1. **Построение матрицы товар-пользователь** (транспонированная)
2. **Центрирование данных** (вычитание среднего рейтинга товара)
3. **Поиск k похожих товаров** с помощью метрики схожести
4. **Предсказание рейтинга** на основе рейтингов пользователя для похожих товаров
5. **Генерация рекомендаций** на основе предсказанных рейтингов

### Метрики схожести

- **Косинусное расстояние** (по умолчанию) - хорошо для разреженных данных
- **Евклидово расстояние** - классическая метрика
- **Манхэттенское расстояние** - устойчиво к выбросам

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта!

### Как внести вклад:

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Области для улучшения:

- 🔍 Новые алгоритмы рекомендаций (Matrix Factorization, Deep Learning)
- 📊 Улучшенные метрики качества
- 🗄️ Интеграция с различными базами данных
- 🚀 Оптимизация производительности
- 📝 Расширение документации
- 🧪 Дополнительные тесты

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [Issues](https://github.com/your-username/recommendation-system/issues)
2. Создайте новый Issue с подробным описанием
3. Посмотрите примеры в папке `examples/`
4. Изучите код в папке `src/`

## 🙏 Благодарности

- Scikit-learn за отличную библиотеку машинного обучения
- Flask за простой веб-фреймворк
- Pandas и NumPy за мощные инструменты для работы с данными
- SQLAlchemy за удобную ORM
- Сообщество Python за поддержку и вдохновение

---

⭐ **Если проект вам понравился, поставьте звезду на GitHub!** ⭐