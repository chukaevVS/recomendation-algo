"""
Тестовый скрипт для API с базой данных.

Демонстрирует работу API с рекомендательной системой, использующей базу данных.
"""

import requests
import json
import time
from typing import Dict, Any


class DatabaseAPIClient:
    """Клиент для работы с API рекомендательной системы с базой данных."""
    
    def __init__(self, base_url: str = "http://localhost:3002"):
        """
        Инициализация клиента.
        
        Args:
            base_url: Базовый URL API сервера
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_health(self) -> Dict[str, Any]:
        """Проверяет состояние системы."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику системы."""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()
    
    def get_db_stats(self) -> Dict[str, Any]:
        """Получает статистику базы данных."""
        response = self.session.get(f"{self.base_url}/db-stats")
        response.raise_for_status()
        return response.json()
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 5) -> Dict[str, Any]:
        """Получает рекомендации для пользователя."""
        response = self.session.get(
            f"{self.base_url}/users/{user_id}/recommendations",
            params={"n_recommendations": n_recommendations}
        )
        response.raise_for_status()
        return response.json()
    
    def add_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет новый товар в базу данных."""
        response = self.session.post(
            f"{self.base_url}/products",
            json=product_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def add_rating(self, rating_data: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет новый рейтинг в базу данных."""
        response = self.session.post(
            f"{self.base_url}/ratings",
            json=rating_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def batch_add_ratings(self, ratings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет несколько рейтингов в базу данных."""
        response = self.session.post(
            f"{self.base_url}/ratings/batch",
            json=ratings_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def retrain_model(self, force: bool = False, async_mode: bool = False) -> Dict[str, Any]:
        """Переобучает модель."""
        params = {"force": force}
        if async_mode:
            params["async"] = True
            
        response = self.session.post(
            f"{self.base_url}/retrain",
            params=params
        )
        response.raise_for_status()
        return response.json()


def print_section(title: str):
    """Печатает заголовок раздела."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_subsection(title: str):
    """Печатает заголовок подраздела."""
    print(f"\n--- {title} ---")


def demo_system_status(client: DatabaseAPIClient):
    """Демонстрирует состояние системы."""
    print_section("ПРОВЕРКА СОСТОЯНИЯ СИСТЕМЫ")
    
    try:
        # Проверяем здоровье системы
        health = client.get_health()
        print("Состояние системы:")
        print(f"  - Статус: {health['status']}")
        print(f"  - Данные загружены: {health['data_loaded']}")
        print(f"  - Модель обучена: {health['model_trained']}")
        print(f"  - База данных подключена: {health['database_connected']}")
        
        # Получаем статистику
        stats = client.get_stats()
        if stats['success']:
            data = stats['data']
            print(f"\nСтатистика системы:")
            print(f"  - Пользователей: {data['users_count']}")
            print(f"  - Товаров: {data['products_count']}")
            print(f"  - Рейтингов: {data['ratings_count']}")
            print(f"  - Модель обучена: {data['model_trained']}")
            print(f"  - База данных: {data['database_url']}")
        
        # Получаем статистику БД
        db_stats = client.get_db_stats()
        if db_stats['success']:
            db_data = db_stats['data']
            print(f"\nСтатистика базы данных:")
            print(f"  - Пользователей в БД: {db_data['users_count']}")
            print(f"  - Товаров в БД: {db_data['products_count']}")
            print(f"  - Рейтингов в БД: {db_data['ratings_count']}")
            print(f"  - URL БД: {db_data['database_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке состояния: {e}")
        return False


def demo_recommendations(client: DatabaseAPIClient):
    """Демонстрирует получение рекомендаций."""
    print_section("РЕКОМЕНДАЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ")
    
    test_users = [1, 5, 10]
    
    for user_id in test_users:
        print_subsection(f"Рекомендации для пользователя {user_id}")
        
        try:
            recommendations = client.get_recommendations(user_id, n_recommendations=5)
            
            if recommendations['success']:
                print(f"Топ-5 рекомендаций:")
                for i, rec in enumerate(recommendations['recommendations'], 1):
                    print(f"  {i}. {rec['name']} ({rec['category']})")
                    print(f"     Предсказанный рейтинг: {rec['predicted_rating']}")
                    print(f"     Цена: {rec['price']:.2f} руб.")
                    print(f"     Бренд: {rec['brand']}")
            else:
                print(f"❌ Ошибка: {recommendations['error']}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении рекомендаций: {e}")


def demo_add_new_product(client: DatabaseAPIClient):
    """Демонстрирует добавление нового товара."""
    print_section("ДОБАВЛЕНИЕ НОВОГО ТОВАРА В БД")
    
    new_product = {
        "product_id": 502,
        "name": "Samsung Galaxy S24 Ultra",
        "category": "Смартфоны",
        "price": 99999.99,
        "description": "Флагманский смартфон Samsung с S Pen",
        "brand": "Samsung",
        "in_stock": True
    }
    
    try:
        result = client.add_product(new_product)
        
        if result['success']:
            print(f"✅ Товар добавлен в БД:")
            print(f"   Название: {result['data']['name']}")
            print(f"   ID: {result['data']['product_id']}")
            print(f"   Цена: {result['data']['price']} руб.")
            print(f"   Категория: {result['data']['category']}")
        else:
            print(f"❌ Ошибка: {result['error']}")
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении товара: {e}")


def demo_add_ratings(client: DatabaseAPIClient):
    """Демонстрирует добавление рейтингов."""
    print_section("ДОБАВЛЕНИЕ РЕЙТИНГОВ В БД")
    
    new_ratings = {
        "ratings": [
            {
                "user_id": 1,
                "product_id": 502,
                "rating": 4.8,
                "review": "Отличный телефон, очень мощный!"
            },
            {
                "user_id": 2,
                "product_id": 502,
                "rating": 4.5,
                "review": "Хорошее качество, но дорого"
            },
            {
                "user_id": 3,
                "product_id": 502,
                "rating": 5.0,
                "review": "Лучший телефон на рынке!"
            }
        ]
    }
    
    try:
        result = client.batch_add_ratings(new_ratings)
        
        if result['success']:
            print(f"✅ {result['count']} рейтингов добавлено в БД")
        else:
            print(f"❌ Ошибка: {result['error']}")
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении рейтингов: {e}")


def demo_retrain_model(client: DatabaseAPIClient):
    """Демонстрирует переобучение модели."""
    print_section("ПЕРЕОБУЧЕНИЕ МОДЕЛИ")
    
    print("Запускаем асинхронное переобучение модели...")
    
    try:
        # Запускаем асинхронное переобучение
        result = client.retrain_model(force=True, async_mode=True)
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   Статус: {result['status']}")
            
            # Ждем завершения переобучения
            print("   Ждем завершения переобучения...")
            time.sleep(10)
            
            # Проверяем статус
            stats = client.get_stats()
            if stats['success']:
                print(f"   Модель обучена: {stats['data']['model_trained']}")
                
                # Показываем обновленную статистику
                print(f"   Обновленная статистика:")
                print(f"     - Пользователей: {stats['data']['users_count']}")
                print(f"     - Товаров: {stats['data']['products_count']}")
                print(f"     - Рейтингов: {stats['data']['ratings_count']}")
        else:
            print(f"❌ Ошибка: {result['error']}")
            
    except Exception as e:
        print(f"❌ Ошибка при переобучении модели: {e}")


def demo_updated_recommendations(client: DatabaseAPIClient):
    """Демонстрирует обновленные рекомендации."""
    print_section("ОБНОВЛЕННЫЕ РЕКОМЕНДАЦИИ ПОСЛЕ ДООБУЧЕНИЯ")
    
    test_user_id = 1
    
    print_subsection(f"Новые рекомендации для пользователя {test_user_id}")
    
    try:
        recommendations = client.get_recommendations(test_user_id, n_recommendations=5)
        
        if recommendations['success']:
            print("Топ-5 рекомендаций после дообучения:")
            for i, rec in enumerate(recommendations['recommendations'], 1):
                new_marker = "🆕" if rec['product_id'] in [501, 502] else ""
                print(f"  {i}. {rec['name']} ({rec['category']}) {new_marker}")
                print(f"     Предсказанный рейтинг: {rec['predicted_rating']}")
                print(f"     Цена: {rec['price']:.2f} руб.")
                print(f"     Бренд: {rec['brand']}")
        else:
            print(f"❌ Ошибка: {recommendations['error']}")
            
    except Exception as e:
        print(f"❌ Ошибка при получении обновленных рекомендаций: {e}")


def main():
    """Главная функция тестирования."""
    print("🗄️ ТЕСТИРОВАНИЕ API С БАЗОЙ ДАННЫХ")
    print("Демонстрирует работу API с рекомендательной системой на основе БД")
    
    # Создаем клиент API
    client = DatabaseAPIClient()
    
    try:
        # Проверяем доступность API
        print("\nПроверяем доступность API...")
        client.get_health()
        print("✅ API доступен!")
        
        # Демонстрация
        if not demo_system_status(client):
            return
        
        demo_recommendations(client)
        demo_add_new_product(client)
        demo_add_ratings(client)
        demo_retrain_model(client)
        demo_updated_recommendations(client)
        
        print_section("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("✅ Все тесты API с базой данных прошли успешно!")
        print("\nКлючевые особенности API:")
        print("• Полная интеграция с базой данных")
        print("• Асинхронное переобучение модели")
        print("• Автоматическое обновление рекомендаций")
        print("• Сохранение данных в БД")
        print("• RESTful API с JSON ответами")
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к API серверу!")
        print("Убедитесь, что сервер запущен на http://localhost:3002")
        print("Запустите сервер командой: python3 src/api/flask_api_db.py")
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
