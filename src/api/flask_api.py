"""
Flask API для рекомендательной системы с базой данных.

Этот модуль предоставляет RESTful API для получения рекомендаций,
управления рейтингами и работы с базой данных.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import traceback
import os
import sys
from datetime import datetime

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from recommendation_system import RecommendationSystemDB, create_db_system


class RecommendationAPIDB:
    """API класс для рекомендательной системы с базой данных."""
    
    def __init__(self, recommendation_system: Optional[RecommendationSystemDB] = None,
                 database_url: Optional[str] = None):
        """
        Инициализация API.
        
        Args:
            recommendation_system: Экземпляр рекомендательной системы
            database_url: URL базы данных
        """
        self.app = Flask(__name__)
        CORS(self.app)  # Разрешаем CORS для всех доменов
        
        # Инициализируем рекомендательную систему
        if recommendation_system is None:
            print("Создание рекомендательной системы с базой данных...")
            self.rec_system = create_db_system(database_url)
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
                "message": "Рекомендательная система с базой данных",
                "version": "2.0.0",
                "database": "SQLite/PostgreSQL",
                "endpoints": {
                    "GET /": "Информация об API",
                    "GET /health": "Проверка состояния системы",
                    "GET /stats": "Статистика системы",
                    "GET /db-stats": "Статистика базы данных",
                    "GET /users/<user_id>/recommendations": "Рекомендации для пользователя",
                    "GET /users/<user_id>/similar": "Похожие пользователи",
                    "GET /users/<user_id>/profile": "Профиль пользователя",
                    "GET /products/<product_id>/similar": "Похожие товары",
                    "GET /products/popular": "Популярные товары",
                    "POST /ratings": "Добавить рейтинг",
                    "POST /products": "Добавить товар",
                    "POST /users": "Добавить пользователя",
                    "POST /retrain": "Переобучить модель",
                    "POST /ratings/batch": "Добавить несколько рейтингов",
                    "POST /products/batch": "Добавить несколько товаров"
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
                    "database_connected": True,
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
                
                # Конвертируем numpy типы в Python типы для JSON сериализации
                def convert_numpy_types(obj):
                    if hasattr(obj, 'item'):  # numpy scalar
                        return obj.item()
                    elif hasattr(obj, 'tolist'):  # numpy array
                        return obj.tolist()
                    elif isinstance(obj, dict):
                        return {k: convert_numpy_types(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_numpy_types(v) for v in obj]
                    else:
                        return obj
                
                stats = convert_numpy_types(stats)
                
                return jsonify({
                    "success": True,
                    "data": stats
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/db-stats', methods=['GET'])
        def get_db_stats():
            """Получает статистику базы данных."""
            try:
                db_stats = self.rec_system.data_manager.get_database_stats()
                return jsonify({
                    "success": True,
                    "data": db_stats
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
            Добавляет новый рейтинг в базу данных.
            
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
                
                # Добавляем рейтинг в БД
                rating_id = self.rec_system.add_rating(
                    user_id=user_id,
                    product_id=product_id,
                    rating=float(rating),
                    review=review
                )
                
                return jsonify({
                    "success": True,
                    "message": "Рейтинг успешно добавлен в базу данных",
                    "rating_id": rating_id,
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
        
        @self.app.route('/products', methods=['POST'])
        def add_product():
            """
            Добавляет новый товар в базу данных.
            
            JSON параметры:
            - product_id (int): ID товара
            - name (str): Название товара
            - category (str): Категория товара
            - price (float): Цена товара
            - description (str, optional): Описание товара
            - brand (str, optional): Бренд товара
            - in_stock (bool, optional): Наличие на складе (по умолчанию true)
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Требуется JSON данные"
                    }), 400
                
                # Валидация обязательных полей
                required_fields = ['product_id', 'name', 'category', 'price']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "success": False,
                            "error": f"Обязательное поле отсутствует: {field}"
                        }), 400
                
                # Импортируем Product здесь, чтобы избежать циклических импортов
                from models.data_models import Product
                
                # Создаем новый товар
                new_product = Product(
                    product_id=data['product_id'],
                    name=data['name'],
                    category=data['category'],
                    price=float(data['price']),
                    description=data.get('description', ''),
                    brand=data.get('brand', 'Unknown'),
                    in_stock=data.get('in_stock', True)
                )
                
                # Добавляем товар в БД
                product_id = self.rec_system.add_product(new_product)
                
                return jsonify({
                    "success": True,
                    "message": "Товар успешно добавлен в базу данных",
                    "product_id": product_id,
                    "data": {
                        "product_id": new_product.product_id,
                        "name": new_product.name,
                        "category": new_product.category,
                        "price": new_product.price
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/users', methods=['POST'])
        def add_user():
            """
            Добавляет нового пользователя в базу данных.
            
            JSON параметры:
            - user_id (int): ID пользователя
            - name (str): Имя пользователя
            - email (str): Email пользователя
            - age (int, optional): Возраст пользователя
            - gender (str, optional): Пол пользователя
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Требуется JSON данные"
                    }), 400
                
                # Валидация обязательных полей
                required_fields = ['user_id', 'name', 'email']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "success": False,
                            "error": f"Обязательное поле отсутствует: {field}"
                        }), 400
                
                # Импортируем User здесь, чтобы избежать циклических импортов
                from models.data_models import User
                
                # Создаем нового пользователя
                new_user = User(
                    user_id=data['user_id'],
                    name=data['name'],
                    email=data['email'],
                    age=data.get('age', 25),
                    gender=data.get('gender', 'М'),
                    registration_date=datetime.now()
                )
                
                # Добавляем пользователя в БД
                user_id = self.rec_system.add_user(new_user)
                
                return jsonify({
                    "success": True,
                    "message": "Пользователь успешно добавлен в базу данных",
                    "user_id": user_id,
                    "data": {
                        "user_id": new_user.user_id,
                        "name": new_user.name,
                        "email": new_user.email,
                        "age": new_user.age
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/retrain', methods=['POST'])
        def retrain_model():
            """
            Переобучает модель с учетом новых данных из БД.
            
            Query параметры:
            - force (bool): Принудительное переобучение даже если модель уже обучена
            - async (bool): Асинхронное переобучение (возвращает статус без ожидания)
            """
            try:
                force = request.args.get('force', 'false').lower() == 'true'
                async_mode = request.args.get('async', 'false').lower() == 'true'
                
                # Проверяем, нужно ли переобучение
                if not force and self.rec_system.is_model_trained:
                    return jsonify({
                        "success": True,
                        "message": "Модель уже обучена. Используйте force=true для принудительного переобучения.",
                        "model_trained": True
                    })
                
                if async_mode:
                    # Асинхронное переобучение - запускаем в фоне и возвращаем статус
                    import threading
                    
                    def retrain_background():
                        try:
                            self.rec_system.retrain_model()
                        except Exception as e:
                            print(f"Ошибка при асинхронном переобучении: {e}")
                    
                    thread = threading.Thread(target=retrain_background)
                    thread.daemon = True
                    thread.start()
                    
                    return jsonify({
                        "success": True,
                        "message": "Переобучение запущено в фоновом режиме",
                        "status": "retraining_in_progress",
                        "model_trained": False
                    })
                else:
                    # Синхронное переобучение
                    print("Начинаем синхронное переобучение модели...")
                    success = self.rec_system.retrain_model()
                    
                    if success:
                        stats = self.rec_system.get_system_stats()
                        
                        # Конвертируем numpy типы в Python типы для JSON сериализации
                        def convert_numpy_types(obj):
                            if hasattr(obj, 'item'):  # numpy scalar
                                return obj.item()
                            elif hasattr(obj, 'tolist'):  # numpy array
                                return obj.tolist()
                            elif isinstance(obj, dict):
                                return {k: convert_numpy_types(v) for k, v in obj.items()}
                            elif isinstance(obj, list):
                                return [convert_numpy_types(v) for v in obj]
                            else:
                                return obj
                        
                        stats = convert_numpy_types(stats)
                        
                        return jsonify({
                            "success": True,
                            "message": "Модель успешно переобучена с данными из БД",
                            "model_trained": True,
                            "stats": stats
                        })
                    else:
                        return jsonify({
                            "success": False,
                            "error": "Ошибка при переобучении модели"
                        }), 500
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/ratings/batch', methods=['POST'])
        def batch_add_ratings():
            """
            Добавляет несколько рейтингов одновременно в базу данных.
            
            JSON параметры:
            - ratings (array): Массив объектов рейтингов
            """
            try:
                data = request.get_json()
                
                if not data or 'ratings' not in data:
                    return jsonify({
                        "success": False,
                        "error": "Требуется массив ratings в JSON данных"
                    }), 400
                
                ratings_data = data['ratings']
                if not isinstance(ratings_data, list):
                    return jsonify({
                        "success": False,
                        "error": "ratings должен быть массивом"
                    }), 400
                
                # Валидируем и добавляем рейтинги
                added_count = 0
                for i, rating_data in enumerate(ratings_data):
                    required_fields = ['user_id', 'product_id', 'rating']
                    for field in required_fields:
                        if field not in rating_data:
                            return jsonify({
                                "success": False,
                                "error": f"Обязательное поле {field} отсутствует в рейтинге {i}"
                            }), 400
                    
                    try:
                        self.rec_system.add_rating(
                            user_id=rating_data['user_id'],
                            product_id=rating_data['product_id'],
                            rating=float(rating_data['rating']),
                            review=rating_data.get('review')
                        )
                        added_count += 1
                    except Exception as e:
                        return jsonify({
                            "success": False,
                            "error": f"Ошибка при добавлении рейтинга {i}: {e}"
                        }), 500
                
                return jsonify({
                    "success": True,
                    "message": f"Добавлено {added_count} рейтингов в базу данных",
                    "count": added_count
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
    
    def run(self, host: str = '0.0.0.0', port: int = 3002, debug: bool = False):
        """
        Запускает Flask сервер.
        
        Args:
            host: Хост для привязки
            port: Порт для привязки
            debug: Режим отладки
        """
        print(f"Запуск API сервера с базой данных на {host}:{port}")
        print(f"Документация доступна по адресу: http://{host}:{port}/")
        self.app.run(host=host, port=port, debug=debug)


def create_api_db(database_url: Optional[str] = None) -> RecommendationAPIDB:
    """
    Создает экземпляр API с базой данных.
    
    Args:
        database_url: URL базы данных
        
    Returns:
        Экземпляр RecommendationAPIDB
    """
    return RecommendationAPIDB(database_url=database_url)


# Пример использования
if __name__ == '__main__':
    # Создаем API с базой данных
    api = create_api_db()
    
    # Запускаем сервер
    api.run(debug=True)
