"""
Flask API для рекомендательной системы интернет-магазина.

Этот модуль предоставляет RESTful API для получения рекомендаций,
управления рейтингами и получения информации о системе.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import traceback
import os
import sys

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from recommendation_system import RecommendationSystem, create_demo_system


class RecommendationAPI:
    """API класс для рекомендательной системы."""
    
    def __init__(self, recommendation_system: Optional[RecommendationSystem] = None):
        """
        Инициализация API.
        
        Args:
            recommendation_system: Экземпляр рекомендательной системы
        """
        self.app = Flask(__name__)
        CORS(self.app)  # Разрешаем CORS для всех доменов
        
        # Инициализируем рекомендательную систему
        if recommendation_system is None:
            print("Создание демонстрационной рекомендательной системы...")
            self.rec_system = create_demo_system()
        else:
            self.rec_system = recommendation_system
        
        # Регистрируем маршруты
        self._register_routes()
        
        # Настраиваем обработку ошибок
        self._register_error_handlers()
    
    def _register_routes(self):
        """Регистрирует все API маршруты."""
        
        @self.app.route('/', methods=['GET'])
        def index():
            """Главная страница API."""
            return jsonify({
                "message": "Рекомендательная система интернет-магазина",
                "version": "1.0.0",
                "endpoints": {
                    "GET /": "Информация об API",
                    "GET /health": "Проверка состояния системы",
                    "GET /stats": "Статистика системы",
                    "GET /users/<user_id>/recommendations": "Рекомендации для пользователя",
                    "GET /users/<user_id>/similar": "Похожие пользователи",
                    "GET /users/<user_id>/profile": "Профиль пользователя",
                    "GET /products/<product_id>/similar": "Похожие товары",
                    "GET /products/popular": "Популярные товары",
                    "POST /ratings": "Добавить рейтинг",
                    "POST /predict": "Предсказать рейтинг"
                }
            })
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Проверка состояния системы."""
            try:
                stats = self.rec_system.get_system_stats()
                return jsonify({
                    "status": "healthy",
                    "data_loaded": stats.get("data_loaded", False),
                    "model_trained": stats.get("model_trained", False),
                    "timestamp": stats.get("timestamp", None)
                })
            except Exception as e:
                return jsonify({
                    "status": "unhealthy",
                    "error": str(e)
                }), 500
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Получает статистику системы."""
            try:
                stats = self.rec_system.get_system_stats()
                return jsonify({
                    "success": True,
                    "data": stats
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/users/<int:user_id>/recommendations', methods=['GET'])
        def get_user_recommendations(user_id: int):
            """
            Получает рекомендации для пользователя.
            
            Query параметры:
            - n_recommendations (int): Количество рекомендаций (по умолчанию 10)
            - include_metadata (bool): Включить метаданные о товарах (по умолчанию true)
            """
            try:
                n_recommendations = request.args.get('n_recommendations', 10, type=int)
                include_metadata = request.args.get('include_metadata', 'true').lower() == 'true'
                
                # Валидация параметров
                if n_recommendations < 1 or n_recommendations > 100:
                    return jsonify({
                        "success": False,
                        "error": "n_recommendations должно быть от 1 до 100"
                    }), 400
                
                recommendations = self.rec_system.get_recommendations(
                    user_id=user_id,
                    n_recommendations=n_recommendations,
                    include_metadata=include_metadata
                )
                
                return jsonify({
                    "success": True,
                    "user_id": user_id,
                    "recommendations": recommendations,
                    "count": len(recommendations)
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/users/<int:user_id>/similar', methods=['GET'])
        def get_similar_users(user_id: int):
            """
            Находит похожих пользователей.
            
            Query параметры:
            - n_similar (int): Количество похожих пользователей (по умолчанию 10)
            """
            try:
                if self.rec_system.approach != 'user_based':
                    return jsonify({
                        "success": False,
                        "error": "Поиск похожих пользователей доступен только для user_based подхода"
                    }), 400
                
                n_similar = request.args.get('n_similar', 10, type=int)
                
                if n_similar < 1 or n_similar > 50:
                    return jsonify({
                        "success": False,
                        "error": "n_similar должно быть от 1 до 50"
                    }), 400
                
                similar_users = self.rec_system.get_similar_users(
                    user_id=user_id,
                    n_similar=n_similar
                )
                
                return jsonify({
                    "success": True,
                    "user_id": user_id,
                    "similar_users": similar_users,
                    "count": len(similar_users)
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/users/<int:user_id>/profile', methods=['GET'])
        def get_user_profile(user_id: int):
            """Получает профиль пользователя."""
            try:
                profile = self.rec_system.get_user_profile(user_id)
                return jsonify({
                    "success": True,
                    "user_id": user_id,
                    "profile": profile
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/products/<int:product_id>/similar', methods=['GET'])
        def get_similar_products(product_id: int):
            """
            Находит похожие товары.
            
            Query параметры:
            - n_similar (int): Количество похожих товаров (по умолчанию 10)
            """
            try:
                if self.rec_system.approach != 'item_based':
                    return jsonify({
                        "success": False,
                        "error": "Поиск похожих товаров доступен только для item_based подхода"
                    }), 400
                
                n_similar = request.args.get('n_similar', 10, type=int)
                
                if n_similar < 1 or n_similar > 50:
                    return jsonify({
                        "success": False,
                        "error": "n_similar должно быть от 1 до 50"
                    }), 400
                
                similar_products = self.rec_system.get_similar_items(
                    product_id=product_id,
                    n_similar=n_similar
                )
                
                return jsonify({
                    "success": True,
                    "product_id": product_id,
                    "similar_products": similar_products,
                    "count": len(similar_products)
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/products/popular', methods=['GET'])
        def get_popular_products():
            """
            Получает популярные товары.
            
            Query параметры:
            - n_items (int): Количество товаров (по умолчанию 10)
            """
            try:
                n_items = request.args.get('n_items', 10, type=int)
                
                if n_items < 1 or n_items > 100:
                    return jsonify({
                        "success": False,
                        "error": "n_items должно быть от 1 до 100"
                    }), 400
                
                popular_products = self.rec_system.get_popular_items(n_items)
                
                return jsonify({
                    "success": True,
                    "popular_products": popular_products,
                    "count": len(popular_products)
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/ratings', methods=['POST'])
        def add_rating():
            """
            Добавляет новый рейтинг.
            
            JSON параметры:
            - user_id (int): ID пользователя
            - product_id (int): ID товара
            - rating (float): Рейтинг (1-5)
            - review (str, optional): Текстовый отзыв
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Требуется JSON данные"
                    }), 400
                
                # Валидация обязательных полей
                required_fields = ['user_id', 'product_id', 'rating']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "success": False,
                            "error": f"Обязательное поле отсутствует: {field}"
                        }), 400
                
                user_id = data['user_id']
                product_id = data['product_id']
                rating = data['rating']
                review = data.get('review')
                
                # Валидация типов и значений
                if not isinstance(user_id, int) or user_id <= 0:
                    return jsonify({
                        "success": False,
                        "error": "user_id должно быть положительным целым числом"
                    }), 400
                
                if not isinstance(product_id, int) or product_id <= 0:
                    return jsonify({
                        "success": False,
                        "error": "product_id должно быть положительным целым числом"
                    }), 400
                
                if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                    return jsonify({
                        "success": False,
                        "error": "rating должно быть числом от 1 до 5"
                    }), 400
                
                self.rec_system.add_rating(
                    user_id=user_id,
                    product_id=product_id,
                    rating=float(rating),
                    review=review
                )
                
                return jsonify({
                    "success": True,
                    "message": "Рейтинг успешно добавлен",
                    "data": {
                        "user_id": user_id,
                        "product_id": product_id,
                        "rating": rating,
                        "review": review
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/predict', methods=['POST'])
        def predict_rating():
            """
            Предсказывает рейтинг пользователя для товара.
            
            JSON параметры:
            - user_id (int): ID пользователя
            - product_id (int): ID товара
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Требуется JSON данные"
                    }), 400
                
                # Валидация обязательных полей
                required_fields = ['user_id', 'product_id']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "success": False,
                            "error": f"Обязательное поле отсутствует: {field}"
                        }), 400
                
                user_id = data['user_id']
                product_id = data['product_id']
                
                # Валидация типов
                if not isinstance(user_id, int) or user_id <= 0:
                    return jsonify({
                        "success": False,
                        "error": "user_id должно быть положительным целым числом"
                    }), 400
                
                if not isinstance(product_id, int) or product_id <= 0:
                    return jsonify({
                        "success": False,
                        "error": "product_id должно быть положительным целым числом"
                    }), 400
                
                predicted_rating = self.rec_system.predict_rating(user_id, product_id)
                
                return jsonify({
                    "success": True,
                    "user_id": user_id,
                    "product_id": product_id,
                    "predicted_rating": round(predicted_rating, 2)
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
    
    def _register_error_handlers(self):
        """Регистрирует обработчики ошибок."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "success": False,
                "error": "Эндпоинт не найден",
                "code": 404
            }), 404
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({
                "success": False,
                "error": "Метод не разрешен",
                "code": 405
            }), 405
        
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                "success": False,
                "error": "Неверный запрос",
                "code": 400
            }), 400
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                "success": False,
                "error": "Внутренняя ошибка сервера",
                "code": 500
            }), 500
    
    def run(self, host: str = '0.0.0.0', port: int = 3001, debug: bool = False):
        """
        Запускает Flask сервер.
        
        Args:
            host: Хост для привязки
            port: Порт для привязки
            debug: Режим отладки
        """
        print(f"Запуск API сервера на {host}:{port}")
        print(f"Документация доступна по адресу: http://{host}:{port}/")
        self.app.run(host=host, port=port, debug=debug)


def create_api(recommendation_system: Optional[RecommendationSystem] = None) -> RecommendationAPI:
    """
    Создает экземпляр API.
    
    Args:
        recommendation_system: Экземпляр рекомендательной системы
        
    Returns:
        Экземпляр RecommendationAPI
    """
    return RecommendationAPI(recommendation_system)


# Пример использования
if __name__ == '__main__':
    # Создаем демонстрационную систему
    print("Создание демонстрационной рекомендательной системы...")
    demo_system = create_demo_system(
        approach='user_based',
        n_neighbors=10,
        num_users=50,
        num_products=100,
        seed=42
    )
    
    # Создаем API
    api = create_api(demo_system)
    
    # Запускаем сервер
    api.run(debug=True)
