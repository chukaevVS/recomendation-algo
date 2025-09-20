"""
Демонстрационный скрипт для рекомендательной системы с базой данных.

Этот скрипт показывает:
- Создание базы данных из CSV файлов
- Загрузку данных в рекомендательную систему
- Обучение модели на данных из БД
- Получение рекомендаций
- Добавление новых данных в БД
- Переобучение модели
"""

import sys
import os
import pandas as pd

# Добавляем путь к проекту в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommendation_system import create_db_system
from src.database.db_models import create_database_from_csv
from src.models.data_models import User, Product, Rating
from datetime import datetime


def print_section(title: str):
    """Печатает заголовок раздела."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_subsection(title: str):
    """Печатает заголовок подраздела."""
    print(f"\n--- {title} ---")


def demo_database_creation():
    """Демонстрирует создание базы данных."""
    print_section("СОЗДАНИЕ БАЗЫ ДАННЫХ ИЗ CSV ФАЙЛОВ")
    
    # Пути к CSV файлам
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    users_csv = os.path.join(data_dir, 'users.csv')
    products_csv = os.path.join(data_dir, 'products.csv')
    ratings_csv = os.path.join(data_dir, 'ratings.csv')
    
    # Проверяем существование файлов
    if not all(os.path.exists(f) for f in [users_csv, products_csv, ratings_csv]):
        print("❌ CSV файлы не найдены. Сначала запустите генератор данных.")
        return None
    
    print("CSV файлы найдены:")
    print(f"  - Пользователи: {users_csv}")
    print(f"  - Товары: {products_csv}")
    print(f"  - Рейтинги: {ratings_csv}")
    
    # Создаем базу данных
    print("\nСоздание базы данных...")
    db_manager = create_database_from_csv(users_csv, products_csv, ratings_csv)
    
    return db_manager


def demo_system_creation():
    """Демонстрирует создание системы с базой данных."""
    print_section("СОЗДАНИЕ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ С БД")
    
    print("Создание системы с параметрами:")
    print("  - Подход: user_based")
    print("  - Количество соседей: 15")
    print("  - Метрика: cosine")
    
    # Создаем систему
    system = create_db_system(
        approach='user_based',
        n_neighbors=15
    )
    
    # Получаем статистику системы
    print_subsection("Статистика системы")
    stats = system.get_system_stats()
    print(f"Пользователей: {stats['users_count']}")
    print(f"Товаров: {stats['products_count']}")
    print(f"Рейтингов: {stats['ratings_count']}")
    print(f"Модель обучена: {stats['model_trained']}")
    print(f"База данных: {stats['database_url']}")
    
    return system


def demo_recommendations(system):
    """Демонстрирует получение рекомендаций."""
    print_section("РЕКОМЕНДАЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ")
    
    # Тестируем рекомендации для нескольких пользователей
    test_users = [1, 5, 10, 25, 50]
    
    for user_id in test_users:
        print_subsection(f"Рекомендации для пользователя {user_id}")
        
        try:
            # Получаем профиль пользователя
            profile = system.get_user_profile(user_id)
            user_info = profile['user_info']
            user_ratings = profile['ratings']
            
            print(f"Пользователь: {user_info['name']} ({user_info['age']} лет)")
            print(f"Email: {user_info['email']}")
            print(f"Количество оценок: {len(user_ratings)}")
            
            if len(user_ratings) > 0:
                avg_rating = sum(r['rating'] for r in user_ratings) / len(user_ratings)
                print(f"Средний рейтинг пользователя: {avg_rating:.2f}")
                
                # Показываем несколько последних оценок
                print("Последние оценки:")
                for rating in sorted(user_ratings, key=lambda x: x['timestamp'], reverse=True)[:3]:
                    print(f"  - Товар {rating['product_id']}: {rating['rating']}")
            
            # Получаем рекомендации
            recommendations = system.get_recommendations(user_id, n_recommendations=5)
            
            print("\nТоп-5 рекомендаций:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec['name']} ({rec['category']})")
                print(f"     Предсказанный рейтинг: {rec['predicted_rating']}")
                print(f"     Цена: {rec['price']:.2f} руб.")
                print(f"     Бренд: {rec['brand']}")
                
        except Exception as e:
            print(f"Ошибка при получении рекомендаций для пользователя {user_id}: {e}")


def demo_similar_users(system):
    """Демонстрирует поиск похожих пользователей."""
    print_section("ПОИСК ПОХОЖИХ ПОЛЬЗОВАТЕЛЕЙ")
    
    test_user_id = 1
    print_subsection(f"Похожие пользователи для пользователя {test_user_id}")
    
    try:
        # Получаем информацию о целевом пользователе
        profile = system.get_user_profile(test_user_id)
        user_info = profile['user_info']
        print(f"Целевой пользователь: {user_info['name']} ({user_info['age']} лет)")
        print(f"Email: {user_info['email']}")
        
        # Находим похожих пользователей
        similar_users = system.get_similar_users(test_user_id, n_similar=5)
        
        print("\nТоп-5 похожих пользователей:")
        for i, similar in enumerate(similar_users, 1):
            print(f"  {i}. {similar['name']} ({similar['age']} лет)")
            print(f"     Схожесть: {similar['similarity']:.3f}")
            print(f"     Количество оценок: {similar['ratings_count']}")
            
    except Exception as e:
        print(f"Ошибка при поиске похожих пользователей: {e}")


def demo_rating_prediction(system):
    """Демонстрирует предсказание рейтингов."""
    print_section("ПРЕДСКАЗАНИЕ РЕЙТИНГОВ")
    
    test_user_id = 1
    test_products = [10, 25, 50, 75, 100]
    
    print_subsection(f"Предсказания для пользователя {test_user_id}")
    
    try:
        profile = system.get_user_profile(test_user_id)
        user_info = profile['user_info']
        print(f"Пользователь: {user_info['name']}")
        
        print("\nПредсказанные рейтинги:")
        for product_id in test_products:
            try:
                predicted_rating = system.predict_rating(test_user_id, product_id)
                
                # Получаем информацию о товаре
                product_info = system.data_manager.get_product_from_cache(product_id)
                if product_info:
                    print(f"  Товар {product_id}: {product_info.name}")
                    print(f"    Категория: {product_info.category}")
                    print(f"    Предсказанный рейтинг: {predicted_rating:.2f}")
                    print(f"    Цена: {product_info.price:.2f} руб.")
                    print(f"    Бренд: {product_info.brand}")
                
            except Exception as e:
                print(f"  Товар {product_id}: Ошибка - {e}")
                
    except Exception as e:
        print(f"Ошибка при предсказании рейтингов: {e}")


def demo_add_new_data(system):
    """Демонстрирует добавление новых данных."""
    print_section("ДОБАВЛЕНИЕ НОВЫХ ДАННЫХ В БД")
    
    print_subsection("Добавление нового товара")
    
    # Создаем новый товар
    new_product = Product(
        product_id=501,
        name="iPhone 15 Pro Max",
        category="Смартфоны",
        price=119999.99,
        description="Новый флагманский смартфон от Apple с улучшенной камерой",
        brand="Apple",
        in_stock=True
    )
    
    try:
        product_id = system.add_product(new_product)
        print(f"✅ Товар добавлен в БД: {new_product.name} (ID: {product_id})")
    except Exception as e:
        print(f"❌ Ошибка при добавлении товара: {e}")
    
    print_subsection("Добавление новых рейтингов")
    
    # Добавляем несколько рейтингов для нового товара
    new_ratings = [
        {
            'user_id': 1,
            'product_id': 501,
            'rating': 5.0,
            'review': 'Отличный телефон, очень доволен!'
        },
        {
            'user_id': 2,
            'product_id': 501,
            'rating': 4.8,
            'review': 'Качество на высоте, но дорого'
        },
        {
            'user_id': 3,
            'product_id': 501,
            'rating': 4.5,
            'review': 'Хороший телефон, рекомендую'
        }
    ]
    
    for rating_data in new_ratings:
        try:
            rating_id = system.add_rating(
                user_id=rating_data['user_id'],
                product_id=rating_data['product_id'],
                rating=rating_data['rating'],
                review=rating_data['review']
            )
            print(f"✅ Рейтинг добавлен в БД: пользователь {rating_data['user_id']}, товар {rating_data['product_id']}, рейтинг {rating_data['rating']}")
        except Exception as e:
            print(f"❌ Ошибка при добавлении рейтинга: {e}")


def demo_retrain_model(system):
    """Демонстрирует переобучение модели."""
    print_section("ПЕРЕОБУЧЕНИЕ МОДЕЛИ")
    
    print("Начинаем переобучение модели с новыми данными...")
    
    try:
        success = system.retrain_model()
        
        if success:
            print("✅ Модель успешно переобучена!")
            
            # Показываем обновленную статистику
            stats = system.get_system_stats()
            print(f"\nОбновленная статистика:")
            print(f"  - Пользователей: {stats['users_count']}")
            print(f"  - Товаров: {stats['products_count']}")
            print(f"  - Рейтингов: {stats['ratings_count']}")
            print(f"  - Модель обучена: {stats['model_trained']}")
        else:
            print("❌ Ошибка при переобучении модели")
            
    except Exception as e:
        print(f"❌ Ошибка при переобучении модели: {e}")


def demo_updated_recommendations(system):
    """Демонстрирует обновленные рекомендации."""
    print_section("ОБНОВЛЕННЫЕ РЕКОМЕНДАЦИИ ПОСЛЕ ДООБУЧЕНИЯ")
    
    test_user_id = 1
    
    print_subsection(f"Новые рекомендации для пользователя {test_user_id}")
    
    try:
        # Получаем обновленные рекомендации
        recommendations = system.get_recommendations(test_user_id, n_recommendations=5)
        
        print("Топ-5 рекомендаций после дообучения:")
        for i, rec in enumerate(recommendations, 1):
            new_marker = "🆕" if rec['product_id'] == 501 else ""
            print(f"  {i}. {rec['name']} ({rec['category']}) {new_marker}")
            print(f"     Предсказанный рейтинг: {rec['predicted_rating']}")
            print(f"     Цена: {rec['price']:.2f} руб.")
            print(f"     Бренд: {rec['brand']}")
            
    except Exception as e:
        print(f"Ошибка при получении обновленных рекомендаций: {e}")


def main():
    """Главная функция демонстрации."""
    print("🗄️ ДЕМОНСТРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ С БАЗОЙ ДАННЫХ")
    print("Показывает полный цикл работы с БД: создание, обучение, рекомендации, дообучение")
    
    try:
        # 1. Создание базы данных
        db_manager = demo_database_creation()
        if db_manager is None:
            return
        
        # 2. Создание системы
        system = demo_system_creation()
        
        # 3. Получение рекомендаций
        demo_recommendations(system)
        
        # 4. Поиск похожих пользователей
        demo_similar_users(system)
        
        # 5. Предсказание рейтингов
        demo_rating_prediction(system)
        
        # 6. Добавление новых данных
        demo_add_new_data(system)
        
        # 7. Переобучение модели
        demo_retrain_model(system)
        
        # 8. Обновленные рекомендации
        demo_updated_recommendations(system)
        
        print_section("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("✅ Все этапы работы с базой данных успешно продемонстрированы!")
        print("\nКлючевые особенности системы:")
        print("• Полная интеграция с базой данных SQLite")
        print("• Автоматическая загрузка данных из БД")
        print("• Сохранение новых данных в БД")
        print("• Переобучение модели с новыми данными")
        print("• Обновление рекомендаций в реальном времени")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
