# 🛍️ Рекомендательная система для интернет-магазина

Простая и эффективная рекомендательная система, использующая алгоритм k-NN (k ближайших соседей) для предоставления персонализированных рекомендаций товаров в интернет-магазине.

## 📋 Содержание

- [Особенности](#особенности)
- [Технологический стек](#технологический-стек)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Структура проекта](#структура-проекта)
- [Использование](#использование)
- [API документация](#api-документация)
- [Примеры](#примеры)
- [Алгоритм](#алгоритм)
- [Конфигурация](#конфигурация)
- [Тестирование](#тестирование)
- [Вклад в проект](#вклад-в-проект)
- [Лицензия](#лицензия)

## ✨ Особенности

- 🤖 **k-NN алгоритм**: Использует проверенный алгоритм машинного обучения
- 👥 **User-based рекомендации**: Рекомендации на основе похожих пользователей
- 📦 **Item-based рекомендации**: Рекомендации на основе похожих товаров
- 🔍 **Поиск похожих объектов**: Находит похожих пользователей и товары
- 📊 **Предсказание рейтингов**: Предсказывает, как пользователь оценит товар
- 🌐 **RESTful API**: Готовый к использованию веб-API
- 📈 **Аналитика**: Статистика и анализ данных
- 🔧 **Легкая настройка**: Простая конфигурация параметров
- 📝 **Подробная документация**: Полное описание всех функций

## 🛠 Технологический стек

- **Python 3.8+**
- **NumPy** - математические операции
- **Pandas** - работа с данными
- **Scikit-learn** - алгоритмы машинного обучения
- **Flask** - веб-фреймворк для API
- **Flask-CORS** - поддержка CORS

## 🚀 Установка

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

## ⚡ Быстрый старт

### Демонстрация системы

```bash
python examples/demo.py
```

### Запуск API сервера

```bash
python src/api/flask_api.py
```

После запуска API будет доступен по адресу: `http://localhost:5000`

### Простой пример использования

```python
from src.recommendation_system import create_demo_system

# Создаем демонстрационную систему
system = create_demo_system()

# Получаем рекомендации для пользователя
recommendations = system.get_recommendations(user_id=1, n_recommendations=5)

for rec in recommendations:
    print(f"{rec['name']}: {rec['predicted_rating']:.2f}")
```

## 📁 Структура проекта

```
RecommendationSystem/
├── src/                          # Исходный код
│   ├── models/                   # Модели данных
│   │   └── data_models.py
│   ├── algorithms/               # Алгоритмы рекомендаций
│   │   └── knn_recommender.py
│   ├── data/                     # Генерация тестовых данных
│   │   └── sample_data.py
│   ├── api/                      # Web API
│   │   └── flask_api.py
│   └── recommendation_system.py  # Главный класс системы
├── examples/                     # Примеры использования
│   └── demo.py
├── tests/                        # Тесты
├── requirements.txt              # Зависимости
├── TODO.md                       # План разработки
└── README.md                     # Документация
```

## 💻 Использование

### Создание системы

```python
from src.recommendation_system import RecommendationSystem

# Создание системы с пользовательскими параметрами
system = RecommendationSystem(
    approach='user_based',  # или 'item_based'
    n_neighbors=10,
    metric='cosine',        # 'cosine', 'euclidean', 'manhattan'
    min_ratings=5
)

# Загрузка тестовых данных
system.load_sample_data(
    num_users=100,
    num_products=200,
    avg_ratings_per_user=20
)

# Обучение модели
system.train_model()
```

### Получение рекомендаций

```python
# Рекомендации для пользователя
recommendations = system.get_recommendations(
    user_id=1,
    n_recommendations=10,
    include_metadata=True
)

# Предсказание рейтинга
predicted_rating = system.predict_rating(user_id=1, product_id=50)

# Поиск похожих пользователей (только для user_based)
similar_users = system.get_similar_users(user_id=1, n_similar=5)

# Поиск похожих товаров (только для item_based)
similar_items = system.get_similar_items(product_id=10, n_similar=5)
```

### Работа с данными

```python
# Добавление нового рейтинга
system.add_rating(
    user_id=1,
    product_id=100,
    rating=4.5,
    review="Отличный товар!"
)

# Получение популярных товаров
popular_items = system.get_popular_items(n_items=10)

# Статистика системы
stats = system.get_system_stats()
```

## 🌐 API документация

### Базовые эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Информация об API |
| GET | `/health` | Проверка состояния |
| GET | `/stats` | Статистика системы |

### Рекомендации

| Метод | URL | Описание | Параметры |
|-------|-----|----------|-----------|
| GET | `/users/{user_id}/recommendations` | Рекомендации для пользователя | `n_recommendations`, `include_metadata` |
| GET | `/users/{user_id}/similar` | Похожие пользователи | `n_similar` |
| GET | `/products/{product_id}/similar` | Похожие товары | `n_similar` |
| GET | `/products/popular` | Популярные товары | `n_items` |

### Данные

| Метод | URL | Описание | Тело запроса |
|-------|-----|----------|--------------|
| POST | `/ratings` | Добавить рейтинг | `{"user_id": 1, "product_id": 10, "rating": 4.5}` |
| POST | `/predict` | Предсказать рейтинг | `{"user_id": 1, "product_id": 10}` |
| GET | `/users/{user_id}/profile` | Профиль пользователя | - |

### Примеры API запросов

```bash
# Получить рекомендации
curl "http://localhost:5000/users/1/recommendations?n_recommendations=5"

# Добавить рейтинг
curl -X POST "http://localhost:5000/ratings" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "product_id": 10, "rating": 4.5, "review": "Отлично!"}'

# Предсказать рейтинг
curl -X POST "http://localhost:5000/predict" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "product_id": 20}'
```

## 📚 Примеры

### Пример 1: Базовое использование

```python
from src.recommendation_system import create_demo_system

# Создаем систему с демонстрационными данными
system = create_demo_system()

# Получаем рекомендации
recs = system.get_recommendations(user_id=1, n_recommendations=5)
print("Рекомендации:")
for i, rec in enumerate(recs, 1):
    print(f"{i}. {rec['name']} - рейтинг: {rec['predicted_rating']:.2f}")
```

### Пример 2: Сравнение подходов

```python
# User-based система
user_system = create_demo_system(approach='user_based')
user_recs = user_system.get_recommendations(user_id=1, n_recommendations=5)

# Item-based система
item_system = create_demo_system(approach='item_based')
item_recs = item_system.get_recommendations(user_id=1, n_recommendations=5)

print("User-based рекомендации:", [r['name'] for r in user_recs])
print("Item-based рекомендации:", [r['name'] for r in item_recs])
```

### Пример 3: Анализ похожести

```python
# Для user-based системы
similar_users = system.get_similar_users(user_id=1, n_similar=3)
print("Похожие пользователи:")
for user in similar_users:
    print(f"- {user['name']}: схожесть {user['similarity']:.3f}")

# Для item-based системы (нужно переключить подход)
system_item = create_demo_system(approach='item_based')
similar_items = system_item.get_similar_items(product_id=1, n_similar=3)
print("Похожие товары:")
for item in similar_items:
    print(f"- {item['name']}: схожесть {item['similarity']:.3f}")
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

### Обработка холодного старта

- **Новые пользователи**: рекомендации на основе популярных товаров
- **Новые товары**: используются средние рейтинги по категориям
- **Разреженные данные**: фильтрация пользователей/товаров с минимальным количеством рейтингов

## ⚙️ Конфигурация

### Параметры системы

```python
system = RecommendationSystem(
    approach='user_based',      # 'user_based' или 'item_based'
    n_neighbors=10,             # Количество соседей (5-20 оптимально)
    metric='cosine',            # Метрика схожести
    min_ratings=5               # Минимум рейтингов для учета
)
```

### Параметры k-NN алгоритма

```python
from src.algorithms.knn_recommender import KNNRecommender

recommender = KNNRecommender(
    n_neighbors=10,
    metric='cosine',
    approach='user_based',
    min_ratings=5,
    algorithm='auto'            # 'auto', 'ball_tree', 'kd_tree', 'brute'
)
```

### Генерация тестовых данных

```python
from src.data.sample_data import create_sample_data

users, products, ratings = create_sample_data(
    num_users=100,              # Количество пользователей
    num_products=200,           # Количество товаров
    avg_ratings_per_user=15,    # Среднее количество рейтингов на пользователя
    seed=42                     # Семя для воспроизводимости
)
```

## 🧪 Тестирование

### Запуск демонстрации

```bash
python examples/demo.py
```

### Тестирование API

```bash
# Запуск API сервера
python src/api/flask_api.py

# В другом терминале
curl http://localhost:5000/health
```

### Создание собственных тестов

```python
import pytest
from src.recommendation_system import create_demo_system

def test_recommendations():
    system = create_demo_system()
    recs = system.get_recommendations(user_id=1, n_recommendations=5)
    assert len(recs) <= 5
    assert all('predicted_rating' in rec for rec in recs)
```

## 📊 Производительность

### Рекомендуемые параметры

| Размер данных | n_neighbors | approach | metric |
|---------------|-------------|----------|--------|
| < 1000 пользователей | 5-10 | user_based | cosine |
| 1000-10000 пользователей | 10-20 | user_based | cosine |
| > 10000 пользователей | 15-30 | item_based | cosine |

### Оптимизация

- **Для больших данных**: используйте `item_based` подход
- **Для разреженных данных**: увеличьте `min_ratings`
- **Для быстрых рекомендаций**: уменьшите `n_neighbors`

## 🔧 Расширение системы

### Добавление новых метрик

```python
from sklearn.metrics.pairwise import manhattan_distances

class CustomKNNRecommender(KNNRecommender):
    def _get_sklearn_metric(self):
        if self.metric == 'manhattan':
            return 'manhattan'
        return super()._get_sklearn_metric()
```

### Интеграция с базой данных

```python
import sqlite3
from src.models.data_models import User, Product, Rating

def load_from_database():
    conn = sqlite3.connect('shop.db')
    
    # Загрузка пользователей
    users_df = pd.read_sql('SELECT * FROM users', conn)
    users = [User(**row) for _, row in users_df.iterrows()]
    
    # Аналогично для товаров и рейтингов
    # ...
    
    return users, products, ratings
```

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
- Сообщество Python за поддержку и вдохновение

---

⭐ **Если проект вам понравился, поставьте звезду на GitHub!** ⭐
