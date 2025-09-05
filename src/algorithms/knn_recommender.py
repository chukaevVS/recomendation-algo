"""
k-NN алгоритм для рекомендательной системы.

Этот модуль реализует алгоритм k ближайших соседей для создания рекомендаций
на основе коллаборативной фильтрации.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Union
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.sparse import csr_matrix
import warnings


class KNNRecommender:
    """
    k-NN рекомендательная система на основе коллаборативной фильтрации.
    
    Поддерживает два подхода:
    1. User-based: рекомендации на основе похожих пользователей
    2. Item-based: рекомендации на основе похожих товаров
    """
    
    def __init__(self, 
                 n_neighbors: int = 10, 
                 metric: str = 'cosine',
                 approach: str = 'user_based',
                 min_ratings: int = 5,
                 algorithm: str = 'auto'):
        """
        Инициализация k-NN рекомендательной системы.
        
        Args:
            n_neighbors: Количество ближайших соседей
            metric: Метрика расстояния ('cosine', 'euclidean', 'manhattan')
            approach: Подход к рекомендациям ('user_based' или 'item_based')
            min_ratings: Минимальное количество рейтингов для учета пользователя/товара
            algorithm: Алгоритм поиска соседей ('auto', 'ball_tree', 'kd_tree', 'brute')
        """
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.approach = approach
        self.min_ratings = min_ratings
        self.algorithm = algorithm
        
        # Инициализация модели NearestNeighbors
        self.model = None
        self.user_item_matrix = None
        self.item_user_matrix = None
        self.user_means = None
        self.item_means = None
        self.global_mean = None
        
        # Маппинги для индексов
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        
        self._validate_params()
    
    def _validate_params(self):
        """Валидация параметров."""
        if self.approach not in ['user_based', 'item_based']:
            raise ValueError("approach должен быть 'user_based' или 'item_based'")
        
        if self.metric not in ['cosine', 'euclidean', 'manhattan']:
            raise ValueError("metric должен быть 'cosine', 'euclidean' или 'manhattan'")
        
        if self.n_neighbors < 1:
            raise ValueError("n_neighbors должен быть >= 1")
    
    def fit(self, ratings_df: pd.DataFrame):
        """
        Обучение модели на данных рейтингов.
        
        Args:
            ratings_df: DataFrame с колонками ['user_id', 'product_id', 'rating']
        """
        print("Подготовка данных для обучения...")
        
        # Проверяем наличие необходимых колонок
        required_cols = ['user_id', 'product_id', 'rating']
        if not all(col in ratings_df.columns for col in required_cols):
            raise ValueError(f"DataFrame должен содержать колонки: {required_cols}")
        
        # Фильтруем пользователей и товары с минимальным количеством рейтингов
        user_counts = ratings_df['user_id'].value_counts()
        item_counts = ratings_df['product_id'].value_counts()
        
        valid_users = user_counts[user_counts >= self.min_ratings].index
        valid_items = item_counts[item_counts >= self.min_ratings].index
        
        filtered_ratings = ratings_df[
            (ratings_df['user_id'].isin(valid_users)) & 
            (ratings_df['product_id'].isin(valid_items))
        ].copy()
        
        print(f"Отфильтровано: {len(filtered_ratings)} рейтингов от {len(valid_users)} пользователей для {len(valid_items)} товаров")
        
        # Создаем матрицу пользователь-товар
        self.user_item_matrix = filtered_ratings.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='rating', 
            fill_value=0
        )
        
        # Создаем маппинги индексов
        self.user_to_idx = {user: idx for idx, user in enumerate(self.user_item_matrix.index)}
        self.idx_to_user = {idx: user for user, idx in self.user_to_idx.items()}
        self.item_to_idx = {item: idx for idx, item in enumerate(self.user_item_matrix.columns)}
        self.idx_to_item = {idx: item for item, idx in self.item_to_idx.items()}
        
        # Вычисляем средние значения
        self.user_means = self.user_item_matrix.mean(axis=1)
        self.item_means = self.user_item_matrix.mean(axis=0)
        self.global_mean = filtered_ratings['rating'].mean()
        
        # Подготавливаем данные в зависимости от подхода
        if self.approach == 'user_based':
            # Центрируем рейтинги пользователей (вычитаем средний рейтинг пользователя)
            centered_matrix = self.user_item_matrix.sub(self.user_means, axis=0).fillna(0)
            self.data_matrix = centered_matrix
        else:  # item_based
            # Транспонируем матрицу для item-based подхода
            self.item_user_matrix = self.user_item_matrix.T
            # Центрируем рейтинги товаров
            centered_matrix = self.item_user_matrix.sub(self.item_means, axis=0).fillna(0)
            self.data_matrix = centered_matrix
        
        # Обучаем модель k-NN
        print(f"Обучение {self.approach} модели с {self.n_neighbors} соседями...")
        
        # Выбираем метрику для sklearn
        sklearn_metric = self._get_sklearn_metric()
        
        self.model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors + 1, len(self.data_matrix)),  # +1 чтобы исключить сам объект
            metric=sklearn_metric,
            algorithm=self.algorithm
        )
        
        self.model.fit(self.data_matrix.values)
        
        print("Модель успешно обучена!")
    
    def _get_sklearn_metric(self) -> str:
        """Преобразует нашу метрику в формат sklearn."""
        metric_mapping = {
            'cosine': 'cosine',
            'euclidean': 'euclidean',
            'manhattan': 'manhattan'
        }
        return metric_mapping[self.metric]
    
    def predict_rating(self, user_id: int, product_id: int) -> float:
        """
        Предсказывает рейтинг пользователя для товара.
        
        Args:
            user_id: ID пользователя
            product_id: ID товара
            
        Returns:
            Предсказанный рейтинг
        """
        if self.model is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        if self.approach == 'user_based':
            return self._predict_user_based(user_id, product_id)
        else:
            return self._predict_item_based(user_id, product_id)
    
    def _predict_user_based(self, user_id: int, product_id: int) -> float:
        """Предсказание рейтинга на основе похожих пользователей."""
        if user_id not in self.user_to_idx or product_id not in self.item_to_idx:
            return self.global_mean
        
        user_idx = self.user_to_idx[user_id]
        item_idx = self.item_to_idx[product_id]
        
        # Находим похожих пользователей
        user_vector = self.data_matrix.iloc[user_idx:user_idx+1].values
        distances, neighbor_indices = self.model.kneighbors(user_vector)
        
        # Исключаем самого пользователя из соседей
        neighbor_indices = neighbor_indices[0][1:]
        distances = distances[0][1:]
        
        # Получаем рейтинги соседей для данного товара
        neighbor_ratings = []
        similarities = []
        
        for idx, neighbor_idx in enumerate(neighbor_indices):
            neighbor_user_id = self.idx_to_user[neighbor_idx]
            original_rating = self.user_item_matrix.iloc[neighbor_idx, item_idx]
            
            if original_rating > 0:  # У соседа есть рейтинг для этого товара
                neighbor_mean = self.user_means.iloc[neighbor_idx]
                centered_rating = original_rating - neighbor_mean
                neighbor_ratings.append(centered_rating)
                
                # Вычисляем схожесть (обратно пропорциональна расстоянию)
                if self.metric == 'cosine':
                    similarity = 1 - distances[idx]
                else:
                    similarity = 1 / (1 + distances[idx])
                
                similarities.append(similarity)
        
        if not neighbor_ratings:
            return self.global_mean
        
        # Вычисляем взвешенное среднее
        neighbor_ratings = np.array(neighbor_ratings)
        similarities = np.array(similarities)
        
        if np.sum(similarities) == 0:
            return self.global_mean
        
        weighted_rating = np.sum(neighbor_ratings * similarities) / np.sum(similarities)
        predicted_rating = self.user_means.iloc[user_idx] + weighted_rating
        
        # Ограничиваем рейтинг в диапазоне [1, 5]
        return np.clip(predicted_rating, 1.0, 5.0)
    
    def _predict_item_based(self, user_id: int, product_id: int) -> float:
        """Предсказание рейтинга на основе похожих товаров."""
        if user_id not in self.user_to_idx or product_id not in self.item_to_idx:
            return self.global_mean
        
        user_idx = self.user_to_idx[user_id]
        item_idx = self.item_to_idx[product_id]
        
        # Находим похожие товары
        item_vector = self.data_matrix.iloc[item_idx:item_idx+1].values
        distances, neighbor_indices = self.model.kneighbors(item_vector)
        
        # Исключаем сам товар из соседей
        neighbor_indices = neighbor_indices[0][1:]
        distances = distances[0][1:]
        
        # Получаем рейтинги пользователя для похожих товаров
        neighbor_ratings = []
        similarities = []
        
        for idx, neighbor_idx in enumerate(neighbor_indices):
            neighbor_item_id = self.idx_to_item[neighbor_idx]
            original_rating = self.user_item_matrix.iloc[user_idx, neighbor_idx]
            
            if original_rating > 0:  # У пользователя есть рейтинг для этого товара
                neighbor_mean = self.item_means.iloc[neighbor_idx]
                centered_rating = original_rating - neighbor_mean
                neighbor_ratings.append(centered_rating)
                
                # Вычисляем схожесть
                if self.metric == 'cosine':
                    similarity = 1 - distances[idx]
                else:
                    similarity = 1 / (1 + distances[idx])
                
                similarities.append(similarity)
        
        if not neighbor_ratings:
            return self.global_mean
        
        # Вычисляем взвешенное среднее
        neighbor_ratings = np.array(neighbor_ratings)
        similarities = np.array(similarities)
        
        if np.sum(similarities) == 0:
            return self.global_mean
        
        weighted_rating = np.sum(neighbor_ratings * similarities) / np.sum(similarities)
        predicted_rating = self.item_means.iloc[item_idx] + weighted_rating
        
        # Ограничиваем рейтинг в диапазоне [1, 5]
        return np.clip(predicted_rating, 1.0, 5.0)
    
    def recommend_items(self, user_id: int, n_recommendations: int = 10, 
                       exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Рекомендует товары для пользователя.
        
        Args:
            user_id: ID пользователя
            n_recommendations: Количество рекомендаций
            exclude_rated: Исключить уже оцененные товары
            
        Returns:
            Список кортежей (product_id, predicted_rating)
        """
        if self.model is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        if user_id not in self.user_to_idx:
            # Для нового пользователя рекомендуем популярные товары
            return self._recommend_popular_items(n_recommendations)
        
        recommendations = []
        user_rated_items = set()
        
        if exclude_rated:
            user_idx = self.user_to_idx[user_id]
            user_ratings = self.user_item_matrix.iloc[user_idx]
            user_rated_items = set(user_ratings[user_ratings > 0].index)
        
        # Предсказываем рейтинги для всех товаров
        for product_id in self.item_to_idx.keys():
            if exclude_rated and product_id in user_rated_items:
                continue
            
            predicted_rating = self.predict_rating(user_id, product_id)
            recommendations.append((product_id, predicted_rating))
        
        # Сортируем по убыванию предсказанного рейтинга
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:n_recommendations]
    
    def _recommend_popular_items(self, n_recommendations: int) -> List[Tuple[int, float]]:
        """Рекомендует популярные товары для новых пользователей."""
        if self.user_item_matrix is None:
            return []
        
        # Вычисляем популярность как средний рейтинг * количество оценок
        item_stats = []
        for product_id in self.item_to_idx.keys():
            item_idx = self.item_to_idx[product_id]
            ratings = self.user_item_matrix.iloc[:, item_idx]
            ratings = ratings[ratings > 0]
            
            if len(ratings) > 0:
                avg_rating = ratings.mean()
                rating_count = len(ratings)
                popularity = avg_rating * np.log(1 + rating_count)  # Взвешиваем по логарифму количества
                item_stats.append((product_id, popularity))
        
        # Сортируем по популярности
        item_stats.sort(key=lambda x: x[1], reverse=True)
        
        return item_stats[:n_recommendations]
    
    def find_similar_users(self, user_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """
        Находит похожих пользователей.
        
        Args:
            user_id: ID пользователя
            n_similar: Количество похожих пользователей
            
        Returns:
            Список кортежей (user_id, similarity_score)
        """
        if self.model is None or self.approach != 'user_based':
            raise ValueError("Модель должна быть обучена с approach='user_based'")
        
        if user_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[user_id]
        user_vector = self.data_matrix.iloc[user_idx:user_idx+1].values
        
        distances, neighbor_indices = self.model.kneighbors(user_vector)
        
        similar_users = []
        for idx, neighbor_idx in enumerate(neighbor_indices[0][1:]):  # Исключаем самого пользователя
            similar_user_id = self.idx_to_user[neighbor_idx]
            
            # Преобразуем расстояние в схожесть
            if self.metric == 'cosine':
                similarity = 1 - distances[0][idx + 1]
            else:
                similarity = 1 / (1 + distances[0][idx + 1])
            
            similar_users.append((similar_user_id, similarity))
        
        return similar_users[:n_similar]
    
    def find_similar_items(self, product_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """
        Находит похожие товары.
        
        Args:
            product_id: ID товара
            n_similar: Количество похожих товаров
            
        Returns:
            Список кортежей (product_id, similarity_score)
        """
        if self.model is None or self.approach != 'item_based':
            raise ValueError("Модель должна быть обучена с approach='item_based'")
        
        if product_id not in self.item_to_idx:
            return []
        
        item_idx = self.item_to_idx[product_id]
        item_vector = self.data_matrix.iloc[item_idx:item_idx+1].values
        
        distances, neighbor_indices = self.model.kneighbors(item_vector)
        
        similar_items = []
        for idx, neighbor_idx in enumerate(neighbor_indices[0][1:]):  # Исключаем сам товар
            similar_item_id = self.idx_to_item[neighbor_idx]
            
            # Преобразуем расстояние в схожесть
            if self.metric == 'cosine':
                similarity = 1 - distances[0][idx + 1]
            else:
                similarity = 1 / (1 + distances[0][idx + 1])
            
            similar_items.append((similar_item_id, similarity))
        
        return similar_items[:n_similar]
    
    def get_model_info(self) -> Dict:
        """
        Возвращает информацию о модели.
        
        Returns:
            Словарь с информацией о модели
        """
        if self.model is None:
            return {"status": "Модель не обучена"}
        
        return {
            "approach": self.approach,
            "n_neighbors": self.n_neighbors,
            "metric": self.metric,
            "algorithm": self.algorithm,
            "n_users": len(self.user_to_idx),
            "n_items": len(self.item_to_idx),
            "matrix_density": (self.user_item_matrix > 0).sum().sum() / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]),
            "global_mean_rating": self.global_mean
        }
