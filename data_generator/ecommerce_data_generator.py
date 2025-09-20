"""
Генератор реалистичных данных для онлайн магазина электроники.

Создает CSV файлы с пользователями, товарами и рейтингами
для демонстрации рекомендательной системы.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os


class EcommerceDataGenerator:
    """Генератор данных для онлайн магазина электроники."""
    
    def __init__(self, seed: int = 42):
        """Инициализация генератора."""
        random.seed(seed)
        np.random.seed(seed)
        
        # Категории товаров
        self.categories = {
            'Смартфоны': {
                'brands': ['Apple', 'Samsung', 'Xiaomi', 'Huawei', 'OnePlus'],
                'price_range': (15000, 150000),
                'popularity': 0.25
            },
            'Ноутбуки': {
                'brands': ['Apple', 'ASUS', 'Lenovo', 'HP', 'Dell'],
                'price_range': (30000, 300000),
                'popularity': 0.20
            },
            'Планшеты': {
                'brands': ['Apple', 'Samsung', 'Huawei', 'Lenovo'],
                'price_range': (8000, 80000),
                'popularity': 0.15
            },
            'Наушники': {
                'brands': ['Apple', 'Sony', 'Sennheiser', 'Bose', 'JBL'],
                'price_range': (1000, 50000),
                'popularity': 0.18
            },
            'Умные часы': {
                'brands': ['Apple', 'Samsung', 'Huawei', 'Amazfit'],
                'price_range': (5000, 60000),
                'popularity': 0.12
            },
            'Фототехника': {
                'brands': ['Canon', 'Nikon', 'Sony', 'Fujifilm'],
                'price_range': (20000, 200000),
                'popularity': 0.10
            }
        }
        
        # Имена пользователей
        self.first_names = [
            'Александр', 'Анна', 'Дмитрий', 'Елена', 'Иван', 'Мария',
            'Сергей', 'Ольга', 'Андрей', 'Татьяна', 'Максим', 'Наталья',
            'Алексей', 'Светлана', 'Владимир', 'Екатерина', 'Николай', 'Юлия',
            'Артем', 'Виктория', 'Павел', 'Анастасия', 'Роман', 'Дарья'
        ]
        
        self.last_names = [
            'Иванов', 'Петров', 'Сидоров', 'Козлов', 'Новиков', 'Морозов',
            'Волков', 'Соловьев', 'Васильев', 'Зайцев', 'Павлов', 'Семенов',
            'Голубев', 'Виноградов', 'Богданов', 'Воробьев', 'Федоров', 'Михайлов',
            'Орлов', 'Лебедев', 'Соколов', 'Медведев', 'Егоров', 'Козлов'
        ]
        
        # Города России
        self.cities = [
            'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
            'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону',
            'Уфа', 'Красноярск', 'Воронеж', 'Пермь', 'Волгоград'
        ]
        
        # Домены email
        self.email_domains = ['gmail.com', 'yandex.ru', 'mail.ru', 'rambler.ru']
    
    def generate_users(self, num_users: int = 1000) -> pd.DataFrame:
        """Генерирует пользователей."""
        print(f"Генерация {num_users} пользователей...")
        
        users_data = []
        
        for i in range(1, num_users + 1):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"
            
            # Email (уникальный)
            email_name = f"{first_name.lower()}.{last_name.lower()}"
            if i > 1:  # Добавляем номер для уникальности
                email_name += f"{i}"
            email = f"{email_name}@{random.choice(self.email_domains)}"
            
            # Демографические данные
            age = random.randint(18, 65)
            gender = random.choice(['М', 'Ж'])
            
            # Локация
            city = random.choice(self.cities)
            
            # Дата регистрации (последние 3 года)
            days_ago = random.randint(1, 1095)
            registration_date = datetime.now() - timedelta(days=days_ago)
            
            # Предпочтения по категориям (на основе возраста и пола)
            preferences = self._generate_user_preferences(age, gender)
            
            users_data.append({
                'user_id': i,
                'name': name,
                'email': email,
                'age': age,
                'gender': gender,
                'city': city,
                'registration_date': registration_date.strftime('%Y-%m-%d'),
                'preferred_categories': '|'.join(preferences)
            })
        
        return pd.DataFrame(users_data)
    
    def _generate_user_preferences(self, age: int, gender: str) -> List[str]:
        """Генерирует предпочтения пользователя на основе возраста и пола."""
        preferences = []
        
        # Базовые предпочтения по возрасту
        if age < 25:
            preferences.extend(['Смартфоны', 'Наушники', 'Умные часы'])
        elif age < 35:
            preferences.extend(['Смартфоны', 'Ноутбуки', 'Планшеты'])
        elif age < 50:
            preferences.extend(['Ноутбуки', 'Фототехника'])
        else:
            preferences.extend(['Планшеты', 'Фототехника'])
        
        # Дополнительные предпочтения по полу
        if gender == 'Ж':
            preferences.append('Умные часы')
        else:
            preferences.append('Фототехника')
        
        # Добавляем случайные предпочтения
        all_categories = list(self.categories.keys())
        additional = random.sample(all_categories, random.randint(1, 3))
        preferences.extend(additional)
        
        return list(set(preferences))  # Убираем дубликаты
    
    def generate_products(self, num_products: int = 500) -> pd.DataFrame:
        """Генерирует товары."""
        print(f"Генерация {num_products} товаров...")
        
        products_data = []
        product_id = 1
        
        for category, info in self.categories.items():
            # Количество товаров в категории пропорционально популярности
            category_count = max(1, int(num_products * info['popularity']))
            
            for _ in range(category_count):
                brand = random.choice(info['brands'])
                
                # Генерируем название товара
                name = self._generate_product_name(category, brand)
                
                # Цена в диапазоне категории
                min_price, max_price = info['price_range']
                price = round(random.uniform(min_price, max_price), 2)
                
                # Описание
                description = self._generate_product_description(category, brand, name)
                
                # Наличие на складе
                in_stock = random.random() < 0.85  # 85% товаров в наличии
                
                # Рейтинг товара (базовый)
                base_rating = random.uniform(3.5, 4.8)
                
                # Дата добавления
                days_ago = random.randint(1, 365)
                created_date = datetime.now() - timedelta(days=days_ago)
                
                products_data.append({
                    'product_id': product_id,
                    'name': name,
                    'category': category,
                    'brand': brand,
                    'price': price,
                    'description': description,
                    'in_stock': in_stock,
                    'base_rating': round(base_rating, 2),
                    'created_date': created_date.strftime('%Y-%m-%d')
                })
                
                product_id += 1
        
        return pd.DataFrame(products_data)
    
    def _generate_product_name(self, category: str, brand: str) -> str:
        """Генерирует название товара."""
        if category == 'Смартфоны':
            models = ['Pro', 'Max', 'Ultra', 'Plus', 'SE', 'Mini']
            model = random.choice(models)
            year = random.choice([2023, 2024])
            return f"{brand} {model} {year}"
        
        elif category == 'Ноутбуки':
            models = ['MacBook Pro', 'MacBook Air', 'ZenBook', 'ThinkPad', 'Pavilion', 'Inspiron']
            model = random.choice(models)
            size = random.choice(['13"', '14"', '15"', '16"'])
            return f"{brand} {model} {size}"
        
        elif category == 'Планшеты':
            models = ['iPad', 'Galaxy Tab', 'MatePad', 'Yoga Tab']
            model = random.choice(models)
            size = random.choice(['10"', '11"', '12"'])
            return f"{brand} {model} {size}"
        
        elif category == 'Наушники':
            models = ['AirPods', 'WH-1000XM', 'QC35', 'FreeBuds', 'Tune']
            model = random.choice(models)
            version = random.choice(['Pro', 'Max', '2', '3', '4'])
            return f"{brand} {model} {version}"
        
        elif category == 'Умные часы':
            models = ['Watch', 'Galaxy Watch', 'Watch GT', 'Amazfit']
            model = random.choice(models)
            series = random.choice(['Series', 'Pro', 'Active', 'Classic'])
            return f"{brand} {model} {series}"
        
        elif category == 'Фототехника':
            models = ['EOS', 'D', 'Alpha', 'X-T']
            model = random.choice(models)
            version = random.choice(['R5', 'R6', '850D', 'A7', 'A9', 'X-T4'])
            return f"{brand} {model} {version}"
        
        else:
            return f"{brand} {category}"
    
    def _generate_product_description(self, category: str, brand: str, name: str) -> str:
        """Генерирует описание товара."""
        descriptions = {
            'Смартфоны': [
                "Высокопроизводительный смартфон с отличной камерой и быстрой зарядкой",
                "Современный дизайн и передовые технологии в одном устройстве",
                "Мощный процессор и долгая работа от батареи"
            ],
            'Ноутбуки': [
                "Профессиональный ноутбук для работы и творчества",
                "Высокая производительность и портативность",
                "Отличное качество экрана и удобная клавиатура"
            ],
            'Планшеты': [
                "Универсальный планшет для работы и развлечений",
                "Большой яркий экран и быстрая работа",
                "Идеален для чтения, просмотра видео и игр"
            ],
            'Наушники': [
                "Беспроводные наушники с отличным звуком",
                "Активное шумоподавление и комфортная посадка",
                "Долгая работа от батареи и быстрая зарядка"
            ],
            'Умные часы': [
                "Умные часы с множеством функций для здоровья и фитнеса",
                "Отслеживание активности и уведомления",
                "Водонепроницаемость и стильный дизайн"
            ],
            'Фототехника': [
                "Профессиональная камера для качественной съемки",
                "Отличное качество изображения и надежность",
                "Подходит для любителей и профессионалов"
            ]
        }
        
        base_desc = random.choice(descriptions.get(category, ["Качественный товар от известного бренда"]))
        return f"{base_desc}. {brand} - это гарантия качества и надежности."
    
    def generate_ratings(self, users_df: pd.DataFrame, products_df: pd.DataFrame, 
                        avg_ratings_per_user: int = 20) -> pd.DataFrame:
        """Генерирует рейтинги."""
        print(f"Генерация рейтингов (в среднем {avg_ratings_per_user} на пользователя)...")
        
        ratings_data = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            user_preferences = user['preferred_categories'].split('|')
            user_age = user['age']
            user_gender = user['gender']
            
            # Количество рейтингов для пользователя
            num_ratings = max(5, int(np.random.poisson(avg_ratings_per_user)))
            num_ratings = min(num_ratings, len(products_df))
            
            # Выбираем товары с учетом предпочтений
            preferred_products = products_df[products_df['category'].isin(user_preferences)]
            
            if len(preferred_products) > 0:
                # 70% рейтингов из предпочитаемых категорий
                preferred_count = int(num_ratings * 0.7)
                preferred_sample = preferred_products.sample(min(preferred_count, len(preferred_products)))
                
                # 30% случайных товаров
                remaining_count = num_ratings - len(preferred_sample)
                other_products = products_df[~products_df['product_id'].isin(preferred_sample['product_id'])]
                other_sample = other_products.sample(min(remaining_count, len(other_products)))
                
                selected_products = pd.concat([preferred_sample, other_sample])
            else:
                selected_products = products_df.sample(num_ratings)
            
            # Генерируем рейтинги
            for _, product in selected_products.iterrows():
                rating = self._generate_realistic_rating(user, product)
                
                # Время оценки (последние 6 месяцев)
                days_ago = random.randint(1, 180)
                timestamp = datetime.now() - timedelta(days=days_ago)
                
                # Иногда добавляем отзыв
                review = None
                if random.random() < 0.4:  # 40% рейтингов с отзывами
                    review = self._generate_review(rating, product)
                
                ratings_data.append({
                    'user_id': user_id,
                    'product_id': product['product_id'],
                    'rating': rating,
                    'review': review,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return pd.DataFrame(ratings_data)
    
    def _generate_realistic_rating(self, user: pd.Series, product: pd.Series) -> float:
        """Генерирует реалистичный рейтинг."""
        base_rating = product['base_rating']
        
        # Корректировка на основе предпочтений пользователя
        user_preferences = user['preferred_categories'].split('|')
        if product['category'] in user_preferences:
            base_rating += random.uniform(0.2, 0.5)
        
        # Корректировка на основе возраста
        user_age = user['age']
        if user_age < 25 and product['category'] in ['Смартфоны', 'Наушники']:
            base_rating += 0.2
        elif user_age > 45 and product['category'] in ['Фототехника']:
            base_rating += 0.3
        
        # Случайная вариация
        noise = np.random.normal(0, 0.3)
        rating = base_rating + noise
        
        # Ограничиваем от 1 до 5
        rating = max(1.0, min(5.0, rating))
        
        # Округляем до 0.5
        return round(rating * 2) / 2
    
    def _generate_review(self, rating: float, product: pd.Series) -> str:
        """Генерирует текстовый отзыв."""
        positive_reviews = [
            "Отличный товар, рекомендую!",
            "Качество на высоте, доволен покупкой.",
            "Хорошее соотношение цены и качества.",
            "Быстрая доставка, товар соответствует описанию.",
            "Покупкой доволен, буду заказывать еще.",
            "Превзошел ожидания, отличное качество!",
            "Рекомендую всем, отличная покупка."
        ]
        
        neutral_reviews = [
            "Товар нормальный, без особых восторгов.",
            "Качество среднее, но за эти деньги сойдет.",
            "Ожидал большего, но в целом неплохо.",
            "Обычный товар, ничего особенного.",
            "Нормальное качество, соответствует цене."
        ]
        
        negative_reviews = [
            "Не рекомендую, качество плохое.",
            "Товар не соответствует описанию.",
            "За эти деньги можно найти лучше.",
            "Разочарован покупкой.",
            "Не стоит своих денег.",
            "Ожидал большего за такую цену."
        ]
        
        if rating >= 4.0:
            return random.choice(positive_reviews)
        elif rating >= 3.0:
            return random.choice(neutral_reviews)
        else:
            return random.choice(negative_reviews)
    
    def generate_all_data(self, num_users: int = 1000, num_products: int = 500, 
                         avg_ratings_per_user: int = 20, output_dir: str = "data"):
        """Генерирует все данные и сохраняет в CSV."""
        print("🚀 Начинаем генерацию данных для онлайн магазина...")
        
        # Создаем директорию если не существует
        os.makedirs(output_dir, exist_ok=True)
        
        # Генерируем данные
        users_df = self.generate_users(num_users)
        products_df = self.generate_products(num_products)
        ratings_df = self.generate_ratings(users_df, products_df, avg_ratings_per_user)
        
        # Сохраняем в CSV
        users_file = os.path.join(output_dir, "users.csv")
        products_file = os.path.join(output_dir, "products.csv")
        ratings_file = os.path.join(output_dir, "ratings.csv")
        
        users_df.to_csv(users_file, index=False, encoding='utf-8')
        products_df.to_csv(products_file, index=False, encoding='utf-8')
        ratings_df.to_csv(ratings_file, index=False, encoding='utf-8')
        
        print(f"\n✅ Данные сохранены:")
        print(f"  - Пользователи: {users_file} ({len(users_df)} записей)")
        print(f"  - Товары: {products_file} ({len(products_df)} записей)")
        print(f"  - Рейтинги: {ratings_file} ({len(ratings_df)} записей)")
        
        # Статистика
        print(f"\n📊 Статистика:")
        print(f"  - Средний рейтинг: {ratings_df['rating'].mean():.2f}")
        print(f"  - Плотность матрицы: {len(ratings_df) / (len(users_df) * len(products_df)):.4f}")
        print(f"  - Категории товаров: {products_df['category'].nunique()}")
        print(f"  - Бренды: {products_df['brand'].nunique()}")
        
        return users_df, products_df, ratings_df


def main():
    """Главная функция для генерации данных."""
    print("🛍️ ГЕНЕРАТОР ДАННЫХ ДЛЯ ОНЛАЙН МАГАЗИНА ЭЛЕКТРОНИКИ")
    print("="*60)
    
    # Создаем генератор
    generator = EcommerceDataGenerator(seed=42)
    
    # Генерируем данные
    users_df, products_df, ratings_df = generator.generate_all_data(
        num_users=1000,
        num_products=500,
        avg_ratings_per_user=20
    )
    
    print("\n🎉 Генерация данных завершена успешно!")
    print("Теперь можно использовать эти данные для обучения рекомендательной системы.")


if __name__ == '__main__':
    main()
