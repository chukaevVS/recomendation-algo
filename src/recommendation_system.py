"""
Основной класс рекомендательной системы для интернет-магазина.

Этот модуль объединяет все компоненты системы и предоставляет
единый интерфейс для работы с рекомендациями.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import pickle
import os
from datetime import datetime

try:
    # Относительные импорты для использования как пакета
    from .models.data_models import DataManager, User, Product, Rating
    from .algorithms.knn_recommender import KNNRecommender
    from .data.sample_data import create_sample_data
except ImportError:
    # Абсолютные импорты для прямого запуска
    from models.data_models import DataManager, User, Product, Rating
    from algorithms.knn_recommender import KNNRecommender
    from data.sample_data import create_sample_data


class RecommendationSystem:
    """
    Главный класс рекомендательной системы интернет-магазина.
    
    Интегрирует управление данными, алгоритмы рекомендаций и предоставляет
    высокоуровневый API для получения рекомендаций.
    """
    
    def __init__(self, 
                 approach: str = 'user_based',
                 n_neighbors: int = 10,
                 metric: str = 'cosine',
                 min_ratings: int = 5):
        """
        Инициализация рекомендательной системы.
        
        Args:
            approach: Подход к рекомендациям ('user_based' или 'item_based')
            n_neighbors: Количество ближайших соседей для k-NN
            metric: Метрика расстояния ('cosine', 'euclidean', 'manhattan')
            min_ratings: Минимальное количество рейтингов для учета
        """
        self.approach = approach
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.min_ratings = min_ratings
        
        # Компоненты системы
        self.data_manager = DataManager()
        self.recommender = KNNRecommender(
            n_neighbors=n_neighbors,
            metric=metric,
            approach=approach,
            min_ratings=min_ratings
        )
        
        # Флаги состояния
        self.is_data_loaded = False
        self.is_model_trained = False
        
        # Кэш для популярных товаров
        self._popular_items_cache = None
        self._cache_timestamp = None
        
    def load_data(self, users: List[User], products: List[Product], ratings: List[Rating]):
        """
        Загружает данные в систему.
        
        Args:
            users: Список пользователей
            products: Список товаров
            ratings: Список рейтингов
        """
        print("Загрузка данных в систему...")
        
        # Загружаем данные в менеджер
        self.data_manager.load_users(users)
        self.data_manager.load_products(products)
        self.data_manager.load_ratings(ratings)
        
        # Валидируем данные
        validation_results = self.data_manager.validate_data()
        if not all(validation_results.values()):
            print("Предупреждение: Обнаружены проблемы с данными:")
            for check, result in validation_results.items():
                if not result:
                    print(f"  - {check}: FAILED")
        
        self.is_data_loaded = True
        self.is_model_trained = False  # Нужно переобучить модель
        self._invalidate_cache()
        
        print(f"Данные успешно загружены:")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Товаров: {len(products)}")
        print(f"  - Рейтингов: {len(ratings)}")
    
    def load_sample_data(self, num_users: int = 50, num_products: int = 100, 
                        avg_ratings_per_user: int = 15, seed: int = 42):
        """
        Загружает тестовые данные.
        
        Args:
            num_users: Количество пользователей
            num_products: Количество товаров
            avg_ratings_per_user: Среднее количество рейтингов на пользователя
            seed: Семя для генератора случайных чисел
        """
        print("Генерация тестовых данных...")
        users, products, ratings = create_sample_data(
            num_users, num_products, avg_ratings_per_user, seed
        )
        self.load_data(users, products, ratings)
    
    def train_model(self):
        """Обучает модель рекомендаций."""
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены. Вызовите load_data() или load_sample_data() сначала.")
        
        print("Начинаем обучение модели...")
        
        # Получаем DataFrame с рейтингами
        ratings_df = self.data_manager.ratings_df.copy()
        
        # Обучаем рекомендательную модель
        self.recommender.fit(ratings_df)
        
        self.is_model_trained = True
        self._invalidate_cache()
        
        print("Модель успешно обучена!")
        
        # Выводим информацию о модели
        model_info = self.recommender.get_model_info()
        print("\nИнформация о модели:")
        for key, value in model_info.items():
            print(f"  - {key}: {value}")
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 10, 
                          include_metadata: bool = True) -> List[Dict]:
        """
        Получает рекомендации для пользователя.
        
        Args:
            user_id: ID пользователя
            n_recommendations: Количество рекомендаций
            include_metadata: Включить метаданные о товарах
            
        Returns:
            Список словарей с рекомендациями
        """
        if not self.is_model_trained:
            raise ValueError("Модель не обучена. Вызовите train_model() сначала.")
        
        # Получаем рекомендации от алгоритма
        recommendations = self.recommender.recommend_items(user_id, n_recommendations)
        
        # Формируем результат
        result = []
        for product_id, predicted_rating in recommendations:
            rec_dict = {
                'product_id': product_id,
                'predicted_rating': round(predicted_rating, 2)
            }
            
            if include_metadata:
                try:
                    product_info = self.data_manager.get_product_info(product_id)
                    rec_dict.update({
                        'name': product_info['name'],
                        'category': product_info['category'],
                        'price': product_info['price'],
                        'brand': product_info.get('brand', 'Unknown')
                    })
                except:
                    # Если не удалось получить информацию о товаре
                    rec_dict.update({
                        'name': f'Product {product_id}',
                        'category': 'Unknown',
                        'price': 0.0,
                        'brand': 'Unknown'
                    })
            
            result.append(rec_dict)
        
        return result
    
    def predict_rating(self, user_id: int, product_id: int) -> float:
        """
        Предсказывает рейтинг пользователя для товара.
        
        Args:
            user_id: ID пользователя
            product_id: ID товара
            
        Returns:
            Предсказанный рейтинг
        """
        if not self.is_model_trained:
            raise ValueError("Модель не обучена. Вызовите train_model() сначала.")
        
        return self.recommender.predict_rating(user_id, product_id)
    
    def get_similar_users(self, user_id: int, n_similar: int = 10) -> List[Dict]:
        """
        Находит похожих пользователей.
        
        Args:
            user_id: ID пользователя
            n_similar: Количество похожих пользователей
            
        Returns:
            Список словарей с информацией о похожих пользователях
        """
        if not self.is_model_trained or self.approach != 'user_based':
            raise ValueError("Модель должна быть обучена с approach='user_based'")
        
        similar_users = self.recommender.find_similar_users(user_id, n_similar)
        
        result = []
        for similar_user_id, similarity in similar_users:
            try:
                user_profile = self.data_manager.get_user_profile(similar_user_id)
                user_info = user_profile['user_info']
                
                result.append({
                    'user_id': similar_user_id,
                    'similarity': round(similarity, 3),
                    'name': user_info['name'],
                    'age': user_info.get('age'),
                    'ratings_count': len(user_profile['ratings'])
                })
            except:
                result.append({
                    'user_id': similar_user_id,
                    'similarity': round(similarity, 3),
                    'name': f'User {similar_user_id}',
                    'age': None,
                    'ratings_count': 0
                })
        
        return result
    
    def get_similar_items(self, product_id: int, n_similar: int = 10) -> List[Dict]:
        """
        Находит похожие товары.
        
        Args:
            product_id: ID товара
            n_similar: Количество похожих товаров
            
        Returns:
            Список словарей с информацией о похожих товарах
        """
        if not self.is_model_trained or self.approach != 'item_based':
            raise ValueError("Модель должна быть обучена с approach='item_based'")
        
        similar_items = self.recommender.find_similar_items(product_id, n_similar)
        
        result = []
        for similar_product_id, similarity in similar_items:
            try:
                product_info = self.data_manager.get_product_info(similar_product_id)
                
                result.append({
                    'product_id': similar_product_id,
                    'similarity': round(similarity, 3),
                    'name': product_info['name'],
                    'category': product_info['category'],
                    'price': product_info['price'],
                    'brand': product_info.get('brand', 'Unknown')
                })
            except:
                result.append({
                    'product_id': similar_product_id,
                    'similarity': round(similarity, 3),
                    'name': f'Product {similar_product_id}',
                    'category': 'Unknown',
                    'price': 0.0,
                    'brand': 'Unknown'
                })
        
        return result
    
    def get_popular_items(self, n_items: int = 10) -> List[Dict]:
        """
        Получает популярные товары.
        
        Args:
            n_items: Количество товаров
            
        Returns:
            Список словарей с популярными товарами
        """
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены.")
        
        # Проверяем кэш
        if (self._popular_items_cache is not None and 
            self._cache_timestamp is not None and 
            (datetime.now() - self._cache_timestamp).seconds < 3600):  # Кэш на 1 час
            return self._popular_items_cache[:n_items]
        
        # Получаем популярные товары
        popular_items = self.data_manager.get_popular_products(n_items)
        
        # Кэшируем результат
        self._popular_items_cache = popular_items
        self._cache_timestamp = datetime.now()
        
        return popular_items
    
    def get_user_profile(self, user_id: int) -> Dict:
        """
        Получает профиль пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с информацией о пользователе
        """
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены.")
        
        return self.data_manager.get_user_profile(user_id)
    
    def add_rating(self, user_id: int, product_id: int, rating: float, 
                   review: Optional[str] = None):
        """
        Добавляет новый рейтинг.
        
        Args:
            user_id: ID пользователя
            product_id: ID товара
            rating: Рейтинг (1-5)
            review: Текстовый отзыв (опционально)
        """
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены.")
        
        if not (1 <= rating <= 5):
            raise ValueError("Рейтинг должен быть от 1 до 5")
        
        # Создаем новый рейтинг
        new_rating = Rating(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            timestamp=datetime.now(),
            review=review
        )
        
        # Добавляем к существующим данным
        new_rating_df = pd.DataFrame([new_rating.to_dict()])
        self.data_manager.ratings_df = pd.concat([
            self.data_manager.ratings_df, 
            new_rating_df
        ], ignore_index=True)
        
        # Помечаем, что модель нужно переобучить
        self.is_model_trained = False
        self._invalidate_cache()
        
        print(f"Рейтинг добавлен: пользователь {user_id}, товар {product_id}, рейтинг {rating}")
    
    def get_system_stats(self) -> Dict:
        """
        Получает статистику системы.
        
        Returns:
            Словарь со статистикой
        """
        if not self.is_data_loaded:
            return {"status": "Данные не загружены"}
        
        stats = {
            "data_loaded": self.is_data_loaded,
            "model_trained": self.is_model_trained,
            "approach": self.approach,
            "n_neighbors": self.n_neighbors,
            "metric": self.metric,
            "users_count": len(self.data_manager.users_df) if self.data_manager.users_df is not None else 0,
            "products_count": len(self.data_manager.products_df) if self.data_manager.products_df is not None else 0,
            "ratings_count": len(self.data_manager.ratings_df) if self.data_manager.ratings_df is not None else 0
        }
        
        # Добавляем статистику пользователей
        if self.is_data_loaded:
            user_stats = self.data_manager.get_user_statistics()
            stats.update(user_stats)
        
        # Добавляем информацию о модели
        if self.is_model_trained:
            model_info = self.recommender.get_model_info()
            stats.update(model_info)
        
        return stats
    
    def save_model(self, filepath: str):
        """
        Сохраняет обученную модель.
        
        Args:
            filepath: Путь для сохранения модели
        """
        if not self.is_model_trained:
            raise ValueError("Модель не обучена.")
        
        model_data = {
            'recommender': self.recommender,
            'data_manager': self.data_manager,
            'approach': self.approach,
            'n_neighbors': self.n_neighbors,
            'metric': self.metric,
            'min_ratings': self.min_ratings,
            'is_data_loaded': self.is_data_loaded,
            'is_model_trained': self.is_model_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Модель сохранена в {filepath}")
    
    def load_model(self, filepath: str):
        """
        Загружает сохраненную модель.
        
        Args:
            filepath: Путь к файлу модели
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл модели не найден: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.recommender = model_data['recommender']
        self.data_manager = model_data['data_manager']
        self.approach = model_data['approach']
        self.n_neighbors = model_data['n_neighbors']
        self.metric = model_data['metric']
        self.min_ratings = model_data['min_ratings']
        self.is_data_loaded = model_data['is_data_loaded']
        self.is_model_trained = model_data['is_model_trained']
        
        self._invalidate_cache()
        
        print(f"Модель загружена из {filepath}")
    
    def _invalidate_cache(self):
        """Очищает кэш."""
        self._popular_items_cache = None
        self._cache_timestamp = None
    
    def __repr__(self):
        """Строковое представление системы."""
        status = "trained" if self.is_model_trained else "not trained"
        return (f"RecommendationSystem(approach='{self.approach}', "
                f"n_neighbors={self.n_neighbors}, metric='{self.metric}', "
                f"status='{status}')")


# Удобная функция для быстрого создания системы с тестовыми данными
def create_demo_system(approach: str = 'user_based', 
                      n_neighbors: int = 10,
                      num_users: int = 50, 
                      num_products: int = 100,
                      seed: int = 42) -> RecommendationSystem:
    """
    Создает демонстрационную рекомендательную систему с тестовыми данными.
    
    Args:
        approach: Подход к рекомендациям ('user_based' или 'item_based')
        n_neighbors: Количество ближайших соседей
        num_users: Количество пользователей
        num_products: Количество товаров
        seed: Семя для генератора случайных чисел
        
    Returns:
        Обученная рекомендательная система
    """
    print("Создание демонстрационной рекомендательной системы...")
    
    # Создаем систему
    system = RecommendationSystem(
        approach=approach,
        n_neighbors=n_neighbors
    )
    
    # Загружаем тестовые данные
    system.load_sample_data(
        num_users=num_users,
        num_products=num_products,
        seed=seed
    )
    
    # Обучаем модель
    system.train_model()
    
    print("Демонстрационная система готова к использованию!")
    return system
