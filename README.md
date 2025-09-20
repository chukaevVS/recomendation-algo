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

# Показать текущую конфигурацию
python app.py --show-config

# Запуск в production режиме
python app.py --environment production
```

### Параметры запуска

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--mode` | Режим: api, demo или config | api |
| `--environment` | Окружение: development, staging, production | development |
| `--database` | URL базы данных (переопределяет конфигурацию) | - |
| `--host` | Хост для API (переопределяет конфигурацию) | - |
| `--port` | Порт для API (переопределяет конфигурацию) | - |
| `--debug` | Режим отладки (переопределяет конфигурацию) | - |
| `--approach` | user_based или item_based (переопределяет конфигурацию) | - |
| `--neighbors` | Количество соседей (переопределяет конфигурацию) | - |
| `--show-config` | Показать текущую конфигурацию | - |

## ⚙️ Конфигурация системы

### Файл конфигурации

Система использует централизованный файл `config.py` для управления всеми параметрами:

```python
from config import get_config

# Загрузка конфигурации для development
config = get_config("development")

# Использование конфигурации
print(f"API порт: {config.api.port}")
print(f"База данных: {config.database.url}")
print(f"Алгоритм: {config.recommendation.approach}")
```

### Предустановленные конфигурации

#### Development (по умолчанию)
- SQLite база данных
- Режим отладки включен
- 10 соседей для k-NN
- Подробное логирование

#### Staging
- PostgreSQL база данных
- Режим отладки отключен
- 15 соседей для k-NN
- Логирование в файл

#### Production
- PostgreSQL база данных
- Высокая производительность
- 20 соседей для k-NN
- Безопасные настройки CORS

### Переменные окружения

Создайте файл `.env` на основе `env.example`:

```bash
# Окружение
ENVIRONMENT=development

# База данных
DATABASE_URL=sqlite:///data/recommendations.db

# API
API_PORT=3002
API_DEBUG=false

# Рекомендации
RECOMMENDATION_APPROACH=user_based
RECOMMENDATION_NEIGHBORS=15
```

### Компоненты конфигурации

#### DatabaseConfig
- URL базы данных
- Настройки пула соединений
- Параметры PostgreSQL

#### APIConfig
- Хост и порт сервера
- Настройки CORS
- Лимиты запросов
- Безопасность

#### RecommendationConfig
- Параметры алгоритма k-NN
- Настройки кэширования
- Лимиты рекомендаций

#### LoggingConfig
- Уровень логирования
- Файлы логов
- Ротация логов

#### DataConfig
- Пути к файлам данных
- Настройки генерации
- Валидация данных

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

### Использование конфигурации

```python
from config import get_config

# Загрузка конфигурации
config = get_config("development")

# Создание системы с конфигурацией
system = RecommendationSystemDB(
    database_url=config.database.url,
    approach=config.recommendation.approach,
    n_neighbors=config.recommendation.n_neighbors,
    metric=config.recommendation.metric,
    min_ratings=config.recommendation.min_ratings,
    auto_load=config.recommendation.auto_load
)
```

### Настройка через переменные окружения

```bash
# Установка переменных окружения
export DATABASE_URL="postgresql://user:pass@localhost/recommendations"
export API_PORT=8080
export RECOMMENDATION_NEIGHBORS=20
export ENVIRONMENT=production

# Запуск приложения
python app.py
```

### Переопределение конфигурации

```python
from config import get_config

# Загрузка базовой конфигурации
config = get_config("development")

# Переопределение параметров
config.api.port = 8080
config.recommendation.n_neighbors = 25
config.database.url = "postgresql://user:pass@localhost/recommendations"

# Валидация конфигурации
config.validate()
```

### Рекомендуемые параметры

| Размер данных | n_neighbors | approach | metric | environment |
|---------------|-------------|----------|--------|-------------|
| < 1000 пользователей | 5-10 | user_based | cosine | development |
| 1000-10000 пользователей | 10-20 | user_based | cosine | staging |
| > 10000 пользователей | 15-30 | item_based | cosine | production |

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

---

⭐ **Если проект вам понравился, поставьте звезду на GitHub!** ⭐