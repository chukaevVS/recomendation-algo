"""
Демонстрационный скрипт для рекомендательной системы интернет-магазина.

Этот скрипт показывает основные возможности системы:
- Создание и загрузка данных
- Обучение модели
- Получение рекомендаций
- Поиск похожих пользователей/товаров
- Предсказание рейтингов
"""

import sys
import os
import pandas as pd

# Добавляем путь к проекту в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommendation_system import create_demo_system, RecommendationSystem
from src.models.data_models import User, Product, Rating
from src.data.sample_data import create_sample_data


def print_section(title: str):
    """Печатает заголовок раздела."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_subsection(title: str):
    """Печатает заголовок подраздела."""
    print(f"\n--- {title} ---")


def demo_basic_functionality():
    """Демонстрация основного функционала системы."""
    print_section("ДЕМОНСТРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ")
    
    print("Создание демонстрационной рекомендательной системы...")
    print("Параметры:")
    print("  - Подход: user_based (на основе похожих пользователей)")
    print("  - Количество соседей: 10")
    print("  - Метрика: cosine")
    print("  - Пользователей: 50")
    print("  - Товаров: 100")
    
    # Создаем демонстрационную систему
    system = create_demo_system(
        approach='user_based',
        n_neighbors=10,
        num_users=50,
        num_products=100,
        seed=42
    )
    
    # Получаем статистику системы
    print_subsection("Статистика системы")
    stats = system.get_system_stats()
    print(f"Пользователей: {stats['users_count']}")
    print(f"Товаров: {stats['products_count']}")
    print(f"Рейтингов: {stats['ratings_count']}")
    print(f"Средний рейтинг: {stats['global_mean_rating']:.2f}")
    print(f"Плотность матрицы: {stats['matrix_density']:.3f}")
    
    return system


def demo_recommendations(system: RecommendationSystem):
    """Демонстрация получения рекомендаций."""
    print_section("РЕКОМЕНДАЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ")
    
    # Тестируем рекомендации для нескольких пользователей
    test_users = [1, 5, 10, 25]
    
    for user_id in test_users:
        print_subsection(f"Рекомендации для пользователя {user_id}")
        
        try:
            # Получаем профиль пользователя
            profile = system.get_user_profile(user_id)
            user_info = profile['user_info']
            user_ratings = profile['ratings']
            
            print(f"Пользователь: {user_info['name']} ({user_info['age']} лет)")
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
                
        except Exception as e:
            print(f"Ошибка при получении рекомендаций для пользователя {user_id}: {e}")


def demo_similar_users(system: RecommendationSystem):
    """Демонстрация поиска похожих пользователей."""
    if system.approach != 'user_based':
        print("Поиск похожих пользователей доступен только для user_based подхода")
        return
    
    print_section("ПОИСК ПОХОЖИХ ПОЛЬЗОВАТЕЛЕЙ")
    
    test_user_id = 1
    print_subsection(f"Похожие пользователи для пользователя {test_user_id}")
    
    try:
        # Получаем информацию о целевом пользователе
        profile = system.get_user_profile(test_user_id)
        user_info = profile['user_info']
        print(f"Целевой пользователь: {user_info['name']} ({user_info['age']} лет)")
        
        # Находим похожих пользователей
        similar_users = system.get_similar_users(test_user_id, n_similar=5)
        
        print("\nТоп-5 похожих пользователей:")
        for i, similar in enumerate(similar_users, 1):
            print(f"  {i}. {similar['name']} ({similar['age']} лет)")
            print(f"     Схожесть: {similar['similarity']:.3f}")
            print(f"     Количество оценок: {similar['ratings_count']}")
            
    except Exception as e:
        print(f"Ошибка при поиске похожих пользователей: {e}")


def demo_rating_prediction(system: RecommendationSystem):
    """Демонстрация предсказания рейтингов."""
    print_section("ПРЕДСКАЗАНИЕ РЕЙТИНГОВ")
    
    test_user_id = 1
    test_products = [10, 25, 50, 75, 90]
    
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
                product_info = system.data_manager.get_product_info(product_id)
                
                print(f"  Товар {product_id}: {product_info['name']}")
                print(f"    Категория: {product_info['category']}")
                print(f"    Предсказанный рейтинг: {predicted_rating:.2f}")
                print(f"    Цена: {product_info['price']:.2f} руб.")
                
            except Exception as e:
                print(f"  Товар {product_id}: Ошибка - {e}")
                
    except Exception as e:
        print(f"Ошибка при предсказании рейтингов: {e}")


def demo_popular_products(system: RecommendationSystem):
    """Демонстрация получения популярных товаров."""
    print_section("ПОПУЛЯРНЫЕ ТОВАРЫ")
    
    try:
        popular_products = system.get_popular_items(n_items=10)
        
        print("Топ-10 популярных товаров:")
        for i, product in enumerate(popular_products, 1):
            print(f"  {i}. {product['name']} ({product['category']})")
            print(f"     Средний рейтинг: {product['avg_rating']:.2f}")
            print(f"     Количество оценок: {product['rating_count']}")
            print(f"     Цена: {product['price']:.2f} руб.")
            
    except Exception as e:
        print(f"Ошибка при получении популярных товаров: {e}")


def demo_add_rating(system: RecommendationSystem):
    """Демонстрация добавления нового рейтинга."""
    print_section("ДОБАВЛЕНИЕ НОВОГО РЕЙТИНГА")
    
    print("Добавляем новый рейтинг от пользователя 1 для товара 999...")
    
    try:
        # Добавляем новый рейтинг
        system.add_rating(
            user_id=1,
            product_id=999,  # Несуществующий товар
            rating=4.5,
            review="Отличный товар, рекомендую!"
        )
        
        print("Рейтинг успешно добавлен!")
        print("Примечание: Для применения изменений модель нужно переобучить.")
        
        # Показываем, что модель помечена как не обученная
        stats = system.get_system_stats()
        print(f"Статус модели: {'обучена' if stats['model_trained'] else 'требует переобучения'}")
        
    except Exception as e:
        print(f"Ошибка при добавлении рейтинга: {e}")


def demo_comparison_approaches():
    """Сравнение user_based и item_based подходов."""
    print_section("СРАВНЕНИЕ ПОДХОДОВ")
    
    print("Создаем две системы с разными подходами...")
    
    # User-based система
    print_subsection("User-based подход")
    user_system = create_demo_system(
        approach='user_based',
        n_neighbors=10,
        num_users=30,
        num_products=50,
        seed=42
    )
    
    # Item-based система
    print_subsection("Item-based подход")
    item_system = create_demo_system(
        approach='item_based',
        n_neighbors=10,
        num_users=30,
        num_products=50,
        seed=42
    )
    
    # Сравниваем рекомендации для одного пользователя
    test_user_id = 1
    print_subsection(f"Рекомендации для пользователя {test_user_id}")
    
    try:
        user_recs = user_system.get_recommendations(test_user_id, n_recommendations=5)
        item_recs = item_system.get_recommendations(test_user_id, n_recommendations=5)
        
        print("User-based рекомендации:")
        for i, rec in enumerate(user_recs, 1):
            print(f"  {i}. {rec['name']} (рейтинг: {rec['predicted_rating']:.2f})")
        
        print("\nItem-based рекомендации:")
        for i, rec in enumerate(item_recs, 1):
            print(f"  {i}. {rec['name']} (рейтинг: {rec['predicted_rating']:.2f})")
        
        # Проверяем пересечение рекомендаций
        user_products = set(rec['product_id'] for rec in user_recs)
        item_products = set(rec['product_id'] for rec in item_recs)
        intersection = user_products.intersection(item_products)
        
        print(f"\nПересечение рекомендаций: {len(intersection)} из 5 товаров")
        
    except Exception as e:
        print(f"Ошибка при сравнении подходов: {e}")


def demo_data_analysis(system: RecommendationSystem):
    """Демонстрация анализа данных."""
    print_section("АНАЛИЗ ДАННЫХ")
    
    try:
        # Анализ рейтингов
        ratings_df = system.data_manager.ratings_df
        
        print_subsection("Статистика рейтингов")
        print(f"Общее количество рейтингов: {len(ratings_df)}")
        print(f"Уникальных пользователей: {ratings_df['user_id'].nunique()}")
        print(f"Уникальных товаров: {ratings_df['product_id'].nunique()}")
        print(f"Средний рейтинг: {ratings_df['rating'].mean():.2f}")
        print(f"Медианный рейтинг: {ratings_df['rating'].median():.2f}")
        print(f"Стандартное отклонение: {ratings_df['rating'].std():.2f}")
        
        # Распределение рейтингов
        print_subsection("Распределение рейтингов")
        rating_counts = ratings_df['rating'].value_counts().sort_index()
        for rating, count in rating_counts.items():
            percentage = count / len(ratings_df) * 100
            print(f"  {rating}: {count} ({percentage:.1f}%)")
        
        # Анализ категорий товаров
        products_df = system.data_manager.products_df
        print_subsection("Распределение по категориям")
        category_counts = products_df['category'].value_counts()
        for category, count in category_counts.head(5).items():
            percentage = count / len(products_df) * 100
            print(f"  {category}: {count} товаров ({percentage:.1f}%)")
        
        # Самые активные пользователи
        print_subsection("Самые активные пользователи")
        user_activity = ratings_df['user_id'].value_counts().head(5)
        for user_id, count in user_activity.items():
            try:
                profile = system.get_user_profile(user_id)
                user_name = profile['user_info']['name']
                print(f"  {user_name} (ID: {user_id}): {count} оценок")
            except:
                print(f"  Пользователь {user_id}: {count} оценок")
        
    except Exception as e:
        print(f"Ошибка при анализе данных: {e}")


def main():
    """Главная функция демонстрации."""
    print("🛍️ ДЕМОНСТРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ ДЛЯ ИНТЕРНЕТ-МАГАЗИНА")
    print("Использует k-NN алгоритм для коллаборативной фильтрации")
    
    try:
        # Основная демонстрация
        system = demo_basic_functionality()
        
        # Демонстрация различных возможностей
        demo_recommendations(system)
        demo_similar_users(system)
        demo_rating_prediction(system)
        demo_popular_products(system)
        demo_add_rating(system)
        
        # Анализ данных
        demo_data_analysis(system)
        
        # Сравнение подходов
        demo_comparison_approaches()
        
        print_section("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("✅ Все основные функции системы продемонстрированы!")
        print("\nДля запуска API сервера используйте:")
        print("  python src/api/flask_api.py")
        print("\nДля получения дополнительной информации см. README.md")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
