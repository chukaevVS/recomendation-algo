"""
Загрузчик данных из базы данных для рекомендательной системы.

Интегрирует базу данных с системой рекомендаций.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from ..models.data_models import User, Product, Rating
    from .db_models import DatabaseManager
except ImportError:
    from models.data_models import User, Product, Rating
    from database.db_models import DatabaseManager


class DatabaseLoader:
    """Загрузчик данных из базы данных."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Инициализация загрузчика.
        
        Args:
            database_url: URL базы данных (если None, используется SQLite по умолчанию)
        """
        self.db_manager = DatabaseManager(database_url)
    
    def load_users(self) -> List[User]:
        """Загружает пользователей из базы данных."""
        print("Загрузка пользователей из базы данных...")
        
        users_data = self.db_manager.get_all_users()
        users = []
        
        for user_data in users_data:
            # Преобразуем строку предпочтений в список
            preferred_categories = []
            if user_data.get('preferred_categories'):
                preferred_categories = user_data['preferred_categories'].split('|')
            
            user = User(
                user_id=user_data['user_id'],
                name=user_data['name'],
                email=user_data['email'],
                age=user_data.get('age', 25),
                gender=user_data.get('gender', 'М'),
                registration_date=user_data.get('registration_date', datetime.now())
            )
            users.append(user)
        
        print(f"Загружено {len(users)} пользователей")
        return users
    
    def load_products(self) -> List[Product]:
        """Загружает товары из базы данных."""
        print("Загрузка товаров из базы данных...")
        
        products_data = self.db_manager.get_all_products()
        products = []
        
        for product_data in products_data:
            product = Product(
                product_id=product_data['product_id'],
                name=product_data['name'],
                category=product_data['category'],
                price=product_data['price'],
                description=product_data.get('description', ''),
                brand=product_data.get('brand', 'Unknown'),
                in_stock=product_data.get('in_stock', True)
            )
            products.append(product)
        
        print(f"Загружено {len(products)} товаров")
        return products
    
    def load_ratings(self) -> List[Rating]:
        """Загружает рейтинги из базы данных."""
        print("Загрузка рейтингов из базы данных...")
        
        ratings_data = self.db_manager.get_all_ratings()
        ratings = []
        
        for rating_data in ratings_data:
            rating = Rating(
                user_id=rating_data['user_id'],
                product_id=rating_data['product_id'],
                rating=rating_data['rating'],
                timestamp=rating_data.get('timestamp', datetime.now()),
                review=rating_data.get('review')
            )
            ratings.append(rating)
        
        print(f"Загружено {len(ratings)} рейтингов")
        return ratings
    
    def load_all_data(self) -> tuple[List[User], List[Product], List[Rating]]:
        """Загружает все данные из базы данных."""
        print("🗄️ Загрузка данных из базы данных...")
        
        users = self.load_users()
        products = self.load_products()
        ratings = self.load_ratings()
        
        return users, products, ratings
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает пользователя по ID."""
        return self.db_manager.get_user_by_id(user_id)
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Получает товар по ID."""
        return self.db_manager.get_product_by_id(product_id)
    
    def get_user_ratings(self, user_id: int) -> List[Dict[str, Any]]:
        """Получает рейтинги пользователя."""
        return self.db_manager.get_user_ratings(user_id)
    
    def get_product_ratings(self, product_id: int) -> List[Dict[str, Any]]:
        """Получает рейтинги товара."""
        return self.db_manager.get_product_ratings(product_id)
    
    def add_user_to_db(self, user: User) -> int:
        """Добавляет пользователя в базу данных."""
        user_data = {
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'age': user.age,
            'gender': user.gender,
            'city': getattr(user, 'city', 'Unknown'),
            'registration_date': user.registration_date,
            'preferred_categories': '|'.join(getattr(user, 'preferred_categories', []))
        }
        return self.db_manager.add_user(user_data)
    
    def add_product_to_db(self, product: Product) -> int:
        """Добавляет товар в базу данных."""
        product_data = {
            'product_id': product.product_id,
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'price': product.price,
            'description': product.description,
            'in_stock': product.in_stock,
            'base_rating': getattr(product, 'base_rating', 4.0),
            'created_date': getattr(product, 'created_date', datetime.now())
        }
        return self.db_manager.add_product(product_data)
    
    def add_rating_to_db(self, rating: Rating) -> int:
        """Добавляет рейтинг в базу данных."""
        rating_data = {
            'user_id': rating.user_id,
            'product_id': rating.product_id,
            'rating': rating.rating,
            'review': rating.review,
            'timestamp': rating.timestamp
        }
        return self.db_manager.add_rating(rating_data)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Получает статистику базы данных."""
        return self.db_manager.get_database_stats()
    
    def sync_user_changes(self, user_id: int, changes: Dict[str, Any]):
        """Синхронизирует изменения пользователя с базой данных."""
        # Здесь можно добавить логику синхронизации
        # Например, обновление предпочтений пользователя
        pass
    
    def sync_product_changes(self, product_id: int, changes: Dict[str, Any]):
        """Синхронизирует изменения товара с базой данных."""
        # Здесь можно добавить логику синхронизации
        # Например, обновление цены или наличия товара
        pass


class HybridDataManager:
    """Гибридный менеджер данных - работает с БД и памятью."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Инициализация гибридного менеджера."""
        self.db_loader = DatabaseLoader(database_url)
        self.memory_cache = {}  # Кэш для часто используемых данных
    
    def load_initial_data(self):
        """Загружает начальные данные из БД в память."""
        print("📊 Загрузка начальных данных из базы данных...")
        users, products, ratings = self.db_loader.load_all_data()
        
        # Кэшируем данные в памяти
        self.memory_cache = {
            'users': {user.user_id: user for user in users},
            'products': {product.product_id: product for product in products},
            'ratings': ratings
        }
        
        print(f"Кэшировано в памяти:")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Товаров: {len(products)}")
        print(f"  - Рейтингов: {len(ratings)}")
        
        return users, products, ratings
    
    def add_user(self, user: User):
        """Добавляет пользователя в БД и кэш."""
        user_id = self.db_loader.add_user_to_db(user)
        self.memory_cache['users'][user.user_id] = user
        return user_id
    
    def add_product(self, product: Product):
        """Добавляет товар в БД и кэш."""
        product_id = self.db_loader.add_product_to_db(product)
        self.memory_cache['products'][product.product_id] = product
        return product_id
    
    def add_rating(self, rating: Rating):
        """Добавляет рейтинг в БД и кэш."""
        rating_id = self.db_loader.add_rating_to_db(rating)
        self.memory_cache['ratings'].append(rating)
        return rating_id
    
    def get_user_from_cache(self, user_id: int) -> Optional[User]:
        """Получает пользователя из кэша."""
        return self.memory_cache.get('users', {}).get(user_id)
    
    def get_product_from_cache(self, product_id: int) -> Optional[Product]:
        """Получает товар из кэша."""
        return self.memory_cache.get('products', {}).get(product_id)
    
    def refresh_cache(self):
        """Обновляет кэш из базы данных."""
        print("🔄 Обновление кэша из базы данных...")
        self.load_initial_data()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику."""
        db_stats = self.db_loader.get_database_stats()
        cache_stats = {
            'cached_users': len(self.memory_cache.get('users', {})),
            'cached_products': len(self.memory_cache.get('products', {})),
            'cached_ratings': len(self.memory_cache.get('ratings', []))
        }
        
        return {**db_stats, **cache_stats}


def create_database_system(database_url: Optional[str] = None):
    """
    Создает систему с базой данных.
    
    Args:
        database_url: URL базы данных
        
    Returns:
        HybridDataManager: Гибридный менеджер данных
    """
    print("🏗️ Создание системы с базой данных...")
    
    # Создаем гибридный менеджер
    data_manager = HybridDataManager(database_url)
    
    # Загружаем данные
    data_manager.load_initial_data()
    
    print("✅ Система с базой данных готова!")
    return data_manager


if __name__ == '__main__':
    # Пример использования
    import os
    
    # Создаем систему с базой данных
    data_manager = create_database_system()
    
    # Выводим статистику
    stats = data_manager.get_stats()
    print(f"\n📊 Статистика системы:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")