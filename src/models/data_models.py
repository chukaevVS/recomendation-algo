"""
Модели данных для рекомендательной системы интернет-магазина.

Этот модуль содержит классы для представления пользователей, товаров и рейтингов.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Модель пользователя интернет-магазина."""
    
    user_id: int
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    registration_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Преобразует объект пользователя в словарь."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'registration_date': self.registration_date
        }


@dataclass
class Product:
    """Модель товара интернет-магазина."""
    
    product_id: int
    name: str
    category: str
    price: float
    description: Optional[str] = None
    brand: Optional[str] = None
    in_stock: bool = True
    
    def to_dict(self) -> Dict:
        """Преобразует объект товара в словарь."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'description': self.description,
            'brand': self.brand,
            'in_stock': self.in_stock
        }


@dataclass
class Rating:
    """Модель рейтинга товара пользователем."""
    
    user_id: int
    product_id: int
    rating: float
    timestamp: Optional[datetime] = None
    review: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Преобразует объект рейтинга в словарь."""
        return {
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'timestamp': self.timestamp,
            'review': self.review
        }


class DataManager:
    """Класс для управления данными рекомендательной системы."""
    
    def __init__(self):
        """Инициализация менеджера данных."""
        self.users_df: Optional[pd.DataFrame] = None
        self.products_df: Optional[pd.DataFrame] = None
        self.ratings_df: Optional[pd.DataFrame] = None
    
    def load_users(self, users: List[User]) -> None:
        """
        Загружает пользователей в DataFrame.
        
        Args:
            users: Список объектов User
        """
        users_data = [user.to_dict() for user in users]
        self.users_df = pd.DataFrame(users_data)
        self.users_df.set_index('user_id', inplace=True)
    
    def load_products(self, products: List[Product]) -> None:
        """
        Загружает товары в DataFrame.
        
        Args:
            products: Список объектов Product
        """
        products_data = [product.to_dict() for product in products]
        self.products_df = pd.DataFrame(products_data)
        self.products_df.set_index('product_id', inplace=True)
    
    def load_ratings(self, ratings: List[Rating]) -> None:
        """
        Загружает рейтинги в DataFrame.
        
        Args:
            ratings: Список объектов Rating
        """
        ratings_data = [rating.to_dict() for rating in ratings]
        self.ratings_df = pd.DataFrame(ratings_data)
    
    def get_user_item_matrix(self) -> pd.DataFrame:
        """
        Создает матрицу пользователь-товар из рейтингов.
        
        Returns:
            DataFrame с пользователями по строкам и товарами по столбцам
        """
        if self.ratings_df is None:
            raise ValueError("Рейтинги не загружены")
        
        # Создаем pivot table для матрицы пользователь-товар
        user_item_matrix = self.ratings_df.pivot_table(
            index='user_id',
            columns='product_id',
            values='rating',
            fill_value=0
        )
        
        return user_item_matrix
    
    def get_user_profile(self, user_id: int) -> Dict:
        """
        Получает профиль пользователя с его рейтингами.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с информацией о пользователе и его рейтингами
        """
        if self.users_df is None or self.ratings_df is None:
            raise ValueError("Данные не загружены")
        
        user_info = self.users_df.loc[user_id].to_dict()
        user_ratings = self.ratings_df[
            self.ratings_df['user_id'] == user_id
        ].to_dict('records')
        
        return {
            'user_info': user_info,
            'ratings': user_ratings
        }
    
    def get_product_info(self, product_id: int) -> Dict:
        """
        Получает информацию о товаре.
        
        Args:
            product_id: ID товара
            
        Returns:
            Словарь с информацией о товаре
        """
        if self.products_df is None:
            raise ValueError("Данные о товарах не загружены")
        
        return self.products_df.loc[product_id].to_dict()
    
    def get_popular_products(self, top_n: int = 10) -> List[Dict]:
        """
        Получает самые популярные товары по среднему рейтингу.
        
        Args:
            top_n: Количество товаров для возврата
            
        Returns:
            Список словарей с информацией о популярных товарах
        """
        if self.ratings_df is None or self.products_df is None:
            raise ValueError("Данные не загружены")
        
        # Вычисляем средний рейтинг и количество оценок для каждого товара
        product_stats = self.ratings_df.groupby('product_id').agg({
            'rating': ['mean', 'count']
        }).round(2)
        
        product_stats.columns = ['avg_rating', 'rating_count']
        
        # Фильтруем товары с минимальным количеством оценок (например, >= 2)
        popular_products = product_stats[
            product_stats['rating_count'] >= 2
        ].sort_values('avg_rating', ascending=False).head(top_n)
        
        # Добавляем информацию о товарах
        result = []
        for product_id in popular_products.index:
            product_info = self.products_df.loc[product_id].to_dict()
            product_info.update({
                'avg_rating': popular_products.loc[product_id, 'avg_rating'],
                'rating_count': popular_products.loc[product_id, 'rating_count']
            })
            result.append(product_info)
        
        return result
    
    def get_user_statistics(self) -> Dict:
        """
        Получает статистику по пользователям.
        
        Returns:
            Словарь со статистикой
        """
        if self.ratings_df is None:
            return {}
        
        user_stats = self.ratings_df.groupby('user_id').agg({
            'rating': ['count', 'mean', 'std']
        }).round(2)
        
        user_stats.columns = ['ratings_count', 'avg_rating', 'rating_std']
        
        return {
            'total_users': len(user_stats),
            'avg_ratings_per_user': user_stats['ratings_count'].mean(),
            'most_active_user': user_stats['ratings_count'].idxmax(),
            'most_ratings': user_stats['ratings_count'].max()
        }
    
    def validate_data(self) -> Dict[str, bool]:
        """
        Проверяет целостность загруженных данных.
        
        Returns:
            Словарь с результатами проверок
        """
        results = {}
        
        # Проверка наличия данных
        results['users_loaded'] = self.users_df is not None
        results['products_loaded'] = self.products_df is not None
        results['ratings_loaded'] = self.ratings_df is not None
        
        if not all([results['users_loaded'], results['products_loaded'], results['ratings_loaded']]):
            return results
        
        # Проверка целостности рейтингов
        valid_users = set(self.ratings_df['user_id']).issubset(set(self.users_df.index))
        valid_products = set(self.ratings_df['product_id']).issubset(set(self.products_df.index))
        
        results['valid_user_ids'] = valid_users
        results['valid_product_ids'] = valid_products
        
        # Проверка диапазона рейтингов
        rating_range = (self.ratings_df['rating'] >= 1) & (self.ratings_df['rating'] <= 5)
        results['valid_rating_range'] = rating_range.all()
        
        return results
