"""
Рекомендательная система с поддержкой базы данных.

Интегрирует базу данных с системой рекомендаций.
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
    from .database.db_loader import DatabaseLoader, HybridDataManager
except ImportError:
    # Абсолютные импорты для прямого запуска
    from models.data_models import DataManager, User, Product, Rating
    from algorithms.knn_recommender import KNNRecommender
    from database.db_loader import DatabaseLoader, HybridDataManager


class RecommendationSystemDB:
    """
    Рекомендательная система с поддержкой базы данных.
    
    Интегрирует управление данными, алгоритмы рекомендаций и базу данных.
    """
    
    def __init__(self, 
                 database_url: Optional[str] = None,
                 approach: str = 'user_based',
                 n_neighbors: int = 10,
                 metric: str = 'cosine',
                 min_ratings: int = 5,
                 auto_load: bool = True):
        """
        Инициализация рекомендательной системы с БД.
        
        Args:
            database_url: URL базы данных (если None, используется SQLite)
            approach: Подход к рекомендациям ('user_based' или 'item_based')
            n_neighbors: Количество ближайших соседей для k-NN
            metric: Метрика расстояния ('cosine', 'euclidean', 'manhattan')
            min_ratings: Минимальное количество рейтингов для учета
            auto_load: Автоматически загружать данные и обучать модель при инициализации
        """
        self.approach = approach
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.min_ratings = min_ratings
        
        # Компоненты системы
        self.data_manager = HybridDataManager(database_url)
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
        
        # Автоматическая загрузка и обучение при инициализации
        if auto_load:
            self.load_data_from_db()
            self.train_model()
        
    def load_data_from_db(self):
        """Загружает данные из базы данных."""
        print("🗄️ Загрузка данных из базы данных...")
        
        # Загружаем данные из БД в память
        users, products, ratings = self.data_manager.load_initial_data()
        
        # Создаем традиционный DataManager для совместимости
        self.data_manager_legacy = DataManager()
        
        # Конвертируем данные в формат для DataManager
        users_data = [user.to_dict() for user in users]
        products_data = [product.to_dict() for product in products]
        ratings_data = [rating.to_dict() for rating in ratings]
        
        # Загружаем в DataManager
        self.data_manager_legacy.load_users(users)
        self.data_manager_legacy.load_products(products)
        self.data_manager_legacy.load_ratings(ratings)
        
        # Валидируем данные
        validation_results = self.data_manager_legacy.validate_data()
        if not all(validation_results.values()):
            print("Предупреждение: Обнаружены проблемы с данными:")
            for check, result in validation_results.items():
                if not result:
                    print(f"  - {check}: FAILED")
        
        self.is_data_loaded = True
        self.is_model_trained = False
        self._invalidate_cache()
        
        print(f"✅ Данные загружены из БД:")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Товаров: {len(products)}")
        print(f"  - Рейтингов: {len(ratings)}")
    
    def train_model(self):
        """Обучает модель рекомендаций."""
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены. Вызовите load_data_from_db() сначала.")
        
        print("🎯 Начинаем обучение модели...")
        
        # Получаем DataFrame с рейтингами
        ratings_df = self.data_manager_legacy.ratings_df.copy()
        
        # Обучаем рекомендательную модель
        self.recommender.fit(ratings_df)
        
        self.is_model_trained = True
        self._invalidate_cache()
        
        print("✅ Модель успешно обучена!")
        
        # Выводим информацию о модели
        model_info = self.recommender.get_model_info()
        print("\n📊 Информация о модели:")
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
                    # Получаем информацию из БД
                    product_info = self.data_manager.get_product_from_cache(product_id)
                    if product_info:
                        rec_dict.update({
                            'name': product_info.name,
                            'category': product_info.category,
                            'price': product_info.price,
                            'brand': product_info.brand
                        })
                    else:
                        # Fallback на legacy DataManager
                        product_info = self.data_manager_legacy.get_product_info(product_id)
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
                # Получаем информацию из БД
                user_info = self.data_manager.get_user_from_cache(similar_user_id)
                if user_info:
                    result.append({
                        'user_id': similar_user_id,
                        'similarity': round(similarity, 3),
                        'name': user_info.name,
                        'age': user_info.age,
                        'ratings_count': len(self.data_manager.get_user_ratings(similar_user_id))
                    })
                else:
                    result.append({
                        'user_id': similar_user_id,
                        'similarity': round(similarity, 3),
                        'name': f'User {similar_user_id}',
                        'age': None,
                        'ratings_count': 0
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
                # Получаем информацию из БД
                product_info = self.data_manager.get_product_from_cache(similar_product_id)
                if product_info:
                    result.append({
                        'product_id': similar_product_id,
                        'similarity': round(similarity, 3),
                        'name': product_info.name,
                        'category': product_info.category,
                        'price': product_info.price,
                        'brand': product_info.brand
                    })
                else:
                    result.append({
                        'product_id': similar_product_id,
                        'similarity': round(similarity, 3),
                        'name': f'Product {similar_product_id}',
                        'category': 'Unknown',
                        'price': 0.0,
                        'brand': 'Unknown'
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
        popular_items = self.data_manager_legacy.get_popular_products(n_items)
        
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
        
        return self.data_manager_legacy.get_user_profile(user_id)
    
    def add_rating(self, user_id: int, product_id: int, rating: float, 
                   review: Optional[str] = None):
        """
        Добавляет новый рейтинг в БД и обновляет кэш.
        
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
        
        # Добавляем в БД и кэш
        rating_id = self.data_manager.add_rating(new_rating)
        
        # Обновляем legacy DataManager
        new_rating_df = pd.DataFrame([new_rating.to_dict()])
        self.data_manager_legacy.ratings_df = pd.concat([
            self.data_manager_legacy.ratings_df, 
            new_rating_df
        ], ignore_index=True)
        
        # Помечаем, что модель нужно переобучить
        self.is_model_trained = False
        self._invalidate_cache()
        
        print(f"✅ Рейтинг добавлен в БД: пользователь {user_id}, товар {product_id}, рейтинг {rating}")
        return rating_id
    
    def add_product(self, product: Product):
        """
        Добавляет новый товар в БД и обновляет кэш.
        
        Args:
            product: Объект товара
        """
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены.")
        
        # Добавляем в БД и кэш
        product_id = self.data_manager.add_product(product)
        
        # Обновляем legacy DataManager
        new_product_df = pd.DataFrame([product.to_dict()])
        self.data_manager_legacy.products_df = pd.concat([
            self.data_manager_legacy.products_df, 
            new_product_df
        ], ignore_index=True)
        
        # Помечаем, что модель нужно переобучить
        self.is_model_trained = False
        self._invalidate_cache()
        
        print(f"✅ Товар добавлен в БД: {product.name} (ID: {product.product_id})")
        return product_id
    
    def add_user(self, user: User):
        """
        Добавляет нового пользователя в БД и обновляет кэш.
        
        Args:
            user: Объект пользователя
        """
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены.")
        
        # Добавляем в БД и кэш
        user_id = self.data_manager.add_user(user)
        
        # Обновляем legacy DataManager
        new_user_df = pd.DataFrame([user.to_dict()])
        self.data_manager_legacy.users_df = pd.concat([
            self.data_manager_legacy.users_df, 
            new_user_df
        ], ignore_index=True)
        
        # Помечаем, что модель нужно переобучить
        self.is_model_trained = False
        self._invalidate_cache()
        
        print(f"✅ Пользователь добавлен в БД: {user.name} (ID: {user.user_id})")
        return user_id
    
    def retrain_model(self):
        """
        Переобучает модель с учетом новых данных.
        
        Returns:
            bool: True если переобучение прошло успешно
        """
        if not self.is_data_loaded:
            raise ValueError("Данные не загружены.")
        
        try:
            print("🔄 Начинаем переобучение модели...")
            
            # Обновляем кэш из БД
            self.data_manager.refresh_cache()
            
            # Загружаем обновленные данные
            users, products, ratings = self.data_manager.load_initial_data()
            
            # Обновляем legacy DataManager
            self.data_manager_legacy.load_users(users)
            self.data_manager_legacy.load_products(products)
            self.data_manager_legacy.load_ratings(ratings)
            
            # Переобучаем модель
            ratings_df = self.data_manager_legacy.ratings_df.copy()
            self.recommender.fit(ratings_df)
            
            self.is_model_trained = True
            self._invalidate_cache()
            
            print("✅ Модель успешно переобучена!")
            
            # Выводим информацию о модели
            model_info = self.recommender.get_model_info()
            print("\n📊 Информация о переобученной модели:")
            for key, value in model_info.items():
                print(f"  - {key}: {value}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при переобучении модели: {e}")
            self.is_model_trained = False
            return False
    
    def get_system_stats(self) -> Dict:
        """
        Получает статистику системы.
        
        Returns:
            Словарь со статистикой
        """
        if not self.is_data_loaded:
            return {"status": "Данные не загружены"}
        
        # Получаем статистику из БД
        db_stats = self.data_manager.get_stats()
        
        stats = {
            "data_loaded": self.is_data_loaded,
            "model_trained": self.is_model_trained,
            "approach": self.approach,
            "n_neighbors": self.n_neighbors,
            "metric": self.metric,
            **db_stats
        }
        
        # Добавляем статистику пользователей
        if self.is_data_loaded:
            user_stats = self.data_manager_legacy.get_user_statistics()
            stats.update(user_stats)
        
        # Добавляем информацию о модели
        if self.is_model_trained:
            model_info = self.recommender.get_model_info()
            stats.update(model_info)
        
        return stats
    
    def _invalidate_cache(self):
        """Очищает кэш."""
        self._popular_items_cache = None
        self._cache_timestamp = None
    
    def __repr__(self):
        """Строковое представление системы."""
        status = "trained" if self.is_model_trained else "not trained"
        return (f"RecommendationSystemDB(approach='{self.approach}', "
                f"n_neighbors={self.n_neighbors}, metric='{self.metric}', "
                f"status='{status}')")


def create_db_system(database_url: Optional[str] = None,
                     approach: str = 'user_based', 
                     n_neighbors: int = 10) -> RecommendationSystemDB:
    """
    Создает рекомендательную систему с базой данных.
    
    Args:
        database_url: URL базы данных (если None, используется SQLite)
        approach: Подход к рекомендациям ('user_based' или 'item_based')
        n_neighbors: Количество ближайших соседей
        
    Returns:
        Обученная рекомендательная система с БД
    """
    print("🏗️ Создание рекомендательной системы с базой данных...")
    
    # Создаем систему
    system = RecommendationSystemDB(
        database_url=database_url,
        approach=approach,
        n_neighbors=n_neighbors
    )
    
    # Загружаем данные из БД
    system.load_data_from_db()
    
    # Обучаем модель
    system.train_model()
    
    print("✅ Система с базой данных готова к использованию!")
    return system


if __name__ == '__main__':
    # Пример использования
    print("🚀 ДЕМОНСТРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ С БАЗОЙ ДАННЫХ")
    print("="*60)
    
    # Создаем систему
    system = create_db_system()
    
    # Выводим статистику
    stats = system.get_system_stats()
    print(f"\n📊 Статистика системы:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # Получаем рекомендации
    print(f"\n🎯 Рекомендации для пользователя 1:")
    recommendations = system.get_recommendations(user_id=1, n_recommendations=5)
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['name']} ({rec['category']}) - рейтинг: {rec['predicted_rating']}")
    
    print("\n🎉 Демонстрация завершена!")
