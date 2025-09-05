"""
Генератор тестовых данных для рекомендательной системы.

Этот модуль создает реалистичные тестовые данные для демонстрации
работы рекомендательной системы.
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple

try:
    from ..models.data_models import User, Product, Rating
except ImportError:
    from models.data_models import User, Product, Rating


class SampleDataGenerator:
    """Генератор тестовых данных для рекомендательной системы."""
    
    def __init__(self, seed: int = 42):
        """
        Инициализация генератора.
        
        Args:
            seed: Семя для генератора случайных чисел
        """
        random.seed(seed)
        np.random.seed(seed)
        
        # Категории товаров
        self.categories = [
            'Электроника', 'Одежда', 'Книги', 'Спорт', 'Дом и сад',
            'Красота', 'Автомобили', 'Игрушки', 'Продукты', 'Здоровье'
        ]
        
        # Бренды для каждой категории
        self.brands = {
            'Электроника': ['Apple', 'Samsung', 'Sony', 'LG', 'Xiaomi'],
            'Одежда': ['Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo'],
            'Книги': ['АСТ', 'Эксмо', 'Питер', 'МИФ', 'Альпина'],
            'Спорт': ['Nike', 'Adidas', 'Reebok', 'Puma', 'Under Armour'],
            'Дом и сад': ['IKEA', 'Leroy Merlin', 'Hoff', 'Casa', 'Zara Home'],
            'Красота': ['L\'Oreal', 'Maybelline', 'MAC', 'Chanel', 'Dior'],
            'Автомобили': ['Bosch', 'Michelin', 'Castrol', 'Shell', 'Mobil'],
            'Игрушки': ['LEGO', 'Mattel', 'Hasbro', 'Fisher-Price', 'Playmobil'],
            'Продукты': ['Nestle', 'Coca-Cola', 'Pepsi', 'Mars', 'Ferrero'],
            'Здоровье': ['Johnson & Johnson', 'Pfizer', 'Bayer', 'Roche', 'Novartis']
        }
        
        # Имена пользователей
        self.first_names = [
            'Александр', 'Анна', 'Дмитрий', 'Елена', 'Иван', 'Мария',
            'Сергей', 'Ольга', 'Андрей', 'Татьяна', 'Максим', 'Наталья',
            'Алексей', 'Светлана', 'Владимир', 'Екатерина', 'Николай', 'Юлия'
        ]
        
        self.last_names = [
            'Иванов', 'Петров', 'Сидоров', 'Козлов', 'Новиков', 'Морозов',
            'Волков', 'Соловьев', 'Васильев', 'Зайцев', 'Павлов', 'Семенов',
            'Голубев', 'Виноградов', 'Богданов', 'Воробьев', 'Федоров', 'Михайлов'
        ]
    
    def generate_users(self, num_users: int = 50) -> List[User]:
        """
        Генерирует список пользователей.
        
        Args:
            num_users: Количество пользователей для генерации
            
        Returns:
            Список объектов User
        """
        users = []
        
        for i in range(1, num_users + 1):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"
            
            # Генерируем email на основе имени
            email_name = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{email_name}@example.com"
            
            # Случайный возраст от 18 до 65
            age = random.randint(18, 65)
            
            # Случайный пол
            gender = random.choice(['М', 'Ж'])
            
            # Дата регистрации в последние 2 года
            days_ago = random.randint(1, 730)
            registration_date = datetime.now() - timedelta(days=days_ago)
            
            user = User(
                user_id=i,
                name=name,
                email=email,
                age=age,
                gender=gender,
                registration_date=registration_date
            )
            users.append(user)
        
        return users
    
    def generate_products(self, num_products: int = 100) -> List[Product]:
        """
        Генерирует список товаров.
        
        Args:
            num_products: Количество товаров для генерации
            
        Returns:
            Список объектов Product
        """
        products = []
        
        for i in range(1, num_products + 1):
            category = random.choice(self.categories)
            brand = random.choice(self.brands[category])
            
            # Генерируем название товара
            product_names = {
                'Электроника': ['Смартфон', 'Ноутбук', 'Планшет', 'Наушники', 'Телевизор'],
                'Одежда': ['Футболка', 'Джинсы', 'Кроссовки', 'Куртка', 'Платье'],
                'Книги': ['Роман', 'Детектив', 'Фантастика', 'Учебник', 'Биография'],
                'Спорт': ['Кроссовки', 'Мяч', 'Гантели', 'Коврик', 'Велосипед'],
                'Дом и сад': ['Стул', 'Стол', 'Лампа', 'Ваза', 'Подушка'],
                'Красота': ['Помада', 'Тушь', 'Крем', 'Шампунь', 'Парфюм'],
                'Автомобили': ['Масло', 'Фильтр', 'Свечи', 'Шины', 'Аккумулятор'],
                'Игрушки': ['Конструктор', 'Кукла', 'Машинка', 'Пазл', 'Мяч'],
                'Продукты': ['Шоколад', 'Кофе', 'Чай', 'Печенье', 'Сок'],
                'Здоровье': ['Витамины', 'Крем', 'Таблетки', 'Пластырь', 'Термометр']
            }
            
            base_name = random.choice(product_names[category])
            name = f"{brand} {base_name}"
            
            # Случайная цена в зависимости от категории
            price_ranges = {
                'Электроника': (5000, 100000),
                'Одежда': (500, 10000),
                'Книги': (200, 2000),
                'Спорт': (1000, 50000),
                'Дом и сад': (500, 20000),
                'Красота': (300, 5000),
                'Автомобили': (1000, 30000),
                'Игрушки': (200, 5000),
                'Продукты': (50, 1000),
                'Здоровье': (100, 3000)
            }
            
            min_price, max_price = price_ranges[category]
            price = round(random.uniform(min_price, max_price), 2)
            
            # Описание товара
            description = f"Высококачественный {base_name.lower()} от бренда {brand}"
            
            # Наличие на складе (90% товаров в наличии)
            in_stock = random.random() < 0.9
            
            product = Product(
                product_id=i,
                name=name,
                category=category,
                price=price,
                description=description,
                brand=brand,
                in_stock=in_stock
            )
            products.append(product)
        
        return products
    
    def generate_ratings(self, users: List[User], products: List[Product], 
                        avg_ratings_per_user: int = 15) -> List[Rating]:
        """
        Генерирует рейтинги товаров пользователями.
        
        Args:
            users: Список пользователей
            products: Список товаров
            avg_ratings_per_user: Среднее количество рейтингов на пользователя
            
        Returns:
            Список объектов Rating
        """
        ratings = []
        rating_id = 1
        
        for user in users:
            # Количество рейтингов для этого пользователя (от 5 до 25)
            num_ratings = max(5, int(np.random.poisson(avg_ratings_per_user)))
            num_ratings = min(num_ratings, len(products))
            
            # Выбираем случайные товары для оценки
            rated_products = random.sample(products, num_ratings)
            
            for product in rated_products:
                # Генерируем рейтинг с учетом предпочтений пользователя
                rating_value = self._generate_realistic_rating(user, product)
                
                # Время оценки (в последние 6 месяцев)
                days_ago = random.randint(1, 180)
                timestamp = datetime.now() - timedelta(days=days_ago)
                
                # Иногда добавляем отзыв
                review = None
                if random.random() < 0.3:  # 30% рейтингов с отзывами
                    review = self._generate_review(rating_value, product)
                
                rating = Rating(
                    user_id=user.user_id,
                    product_id=product.product_id,
                    rating=rating_value,
                    timestamp=timestamp,
                    review=review
                )
                ratings.append(rating)
                rating_id += 1
        
        return ratings
    
    def _generate_realistic_rating(self, user: User, product: Product) -> float:
        """
        Генерирует реалистичный рейтинг с учетом предпочтений пользователя.
        
        Args:
            user: Пользователь
            product: Товар
            
        Returns:
            Рейтинг от 1.0 до 5.0
        """
        # Базовый рейтинг зависит от категории товара
        category_preferences = {
            'Электроника': 4.2,
            'Одежда': 3.8,
            'Книги': 4.5,
            'Спорт': 4.0,
            'Дом и сад': 3.9,
            'Красота': 3.7,
            'Автомобили': 4.1,
            'Игрушки': 4.3,
            'Продукты': 3.6,
            'Здоровье': 4.0
        }
        
        base_rating = category_preferences.get(product.category, 4.0)
        
        # Добавляем случайную вариацию
        noise = np.random.normal(0, 0.5)
        rating = base_rating + noise
        
        # Ограничиваем рейтинг от 1 до 5
        rating = max(1.0, min(5.0, rating))
        
        # Округляем до 0.5
        rating = round(rating * 2) / 2
        
        return rating
    
    def _generate_review(self, rating: float, product: Product) -> str:
        """
        Генерирует текстовый отзыв на основе рейтинга.
        
        Args:
            rating: Рейтинг товара
            product: Товар
            
        Returns:
            Текст отзыва
        """
        positive_reviews = [
            "Отличный товар, рекомендую!",
            "Качество на высоте, доволен покупкой.",
            "Хорошее соотношение цены и качества.",
            "Быстрая доставка, товар соответствует описанию.",
            "Покупкой доволен, буду заказывать еще."
        ]
        
        neutral_reviews = [
            "Товар нормальный, без особых восторгов.",
            "Качество среднее, но за эти деньги сойдет.",
            "Ожидал большего, но в целом неплохо.",
            "Обычный товар, ничего особенного."
        ]
        
        negative_reviews = [
            "Не рекомендую, качество плохое.",
            "Товар не соответствует описанию.",
            "За эти деньги можно найти лучше.",
            "Разочарован покупкой.",
            "Не стоит своих денег."
        ]
        
        if rating >= 4.0:
            return random.choice(positive_reviews)
        elif rating >= 3.0:
            return random.choice(neutral_reviews)
        else:
            return random.choice(negative_reviews)
    
    def generate_all_data(self, num_users: int = 50, num_products: int = 100, 
                         avg_ratings_per_user: int = 15) -> Tuple[List[User], List[Product], List[Rating]]:
        """
        Генерирует все данные: пользователей, товары и рейтинги.
        
        Args:
            num_users: Количество пользователей
            num_products: Количество товаров
            avg_ratings_per_user: Среднее количество рейтингов на пользователя
            
        Returns:
            Кортеж из списков пользователей, товаров и рейтингов
        """
        print(f"Генерация {num_users} пользователей...")
        users = self.generate_users(num_users)
        
        print(f"Генерация {num_products} товаров...")
        products = self.generate_products(num_products)
        
        print(f"Генерация рейтингов...")
        ratings = self.generate_ratings(users, products, avg_ratings_per_user)
        
        print(f"Сгенерировано:")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Товаров: {len(products)}")
        print(f"  - Рейтингов: {len(ratings)}")
        
        return users, products, ratings


# Функция для быстрого создания тестовых данных
def create_sample_data(num_users: int = 50, num_products: int = 100, 
                      avg_ratings_per_user: int = 15, seed: int = 42) -> Tuple[List[User], List[Product], List[Rating]]:
    """
    Создает тестовые данные для рекомендательной системы.
    
    Args:
        num_users: Количество пользователей
        num_products: Количество товаров
        avg_ratings_per_user: Среднее количество рейтингов на пользователя
        seed: Семя для генератора случайных чисел
        
    Returns:
        Кортеж из списков пользователей, товаров и рейтингов
    """
    generator = SampleDataGenerator(seed=seed)
    return generator.generate_all_data(num_users, num_products, avg_ratings_per_user)
