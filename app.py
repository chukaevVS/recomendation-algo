#!/usr/bin/env python3
"""
Единая точка входа в рекомендательную систему.

Этот файл предоставляет простой способ запуска рекомендательной системы
с автоматическим подключением к базе данных и обучением модели.
"""

import os
import sys
import argparse
from typing import Optional

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.recommendation_system import RecommendationSystemDB, create_db_system
from src.api.flask_api import RecommendationAPIDB


def main():
    """Главная функция приложения."""
    parser = argparse.ArgumentParser(
        description='Рекомендательная система с базой данных',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Запуск API сервера (по умолчанию)
  python app.py

  # Запуск API сервера на другом порту
  python app.py --port 8080

  # Запуск с PostgreSQL
  python app.py --database postgresql://user:pass@localhost/recommendations

  # Запуск без автоматического обучения модели
  python app.py --no-auto-load

  # Запуск в режиме отладки
  python app.py --debug
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['api', 'demo'],
        default='api',
        help='Режим запуска: api (сервер) или demo (демонстрация)'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        default=None,
        help='URL базы данных (по умолчанию: SQLite в data/recommendations.db)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Хост для API сервера (по умолчанию: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=3002,
        help='Порт для API сервера (по умолчанию: 3002)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Запуск в режиме отладки'
    )
    
    parser.add_argument(
        '--no-auto-load',
        action='store_true',
        help='Не загружать данные и не обучать модель автоматически'
    )
    
    parser.add_argument(
        '--approach',
        choices=['user_based', 'item_based'],
        default='user_based',
        help='Подход к рекомендациям (по умолчанию: user_based)'
    )
    
    parser.add_argument(
        '--neighbors',
        type=int,
        default=15,
        help='Количество ближайших соседей для k-NN (по умолчанию: 15)'
    )
    
    args = parser.parse_args()
    
    print("🚀 РЕКОМЕНДАТЕЛЬНАЯ СИСТЕМА")
    print("=" * 50)
    print(f"Режим: {args.mode}")
    print(f"База данных: {args.database or 'SQLite (data/recommendations.db)'}")
    print(f"Подход: {args.approach}")
    print(f"Соседей: {args.neighbors}")
    print("=" * 50)
    
    if args.mode == 'api':
        run_api_server(args)
    elif args.mode == 'demo':
        run_demo(args)


def run_api_server(args):
    """Запускает API сервер."""
    try:
        print("🏗️ Создание рекомендательной системы...")
        
        # Создаем систему с автоматической загрузкой данных
        auto_load = not args.no_auto_load
        system = RecommendationSystemDB(
            database_url=args.database,
            approach=args.approach,
            n_neighbors=args.neighbors,
            auto_load=auto_load
        )
        
        print("🌐 Создание API сервера...")
        
        # Создаем API с системой
        api = RecommendationAPIDB(recommendation_system=system)
        
        print(f"✅ Система готова!")
        print(f"📊 Статистика:")
        stats = system.get_system_stats()
        print(f"  - Пользователей: {stats.get('n_users', 0)}")
        print(f"  - Товаров: {stats.get('n_items', 0)}")
        print(f"  - Рейтингов: {stats.get('n_ratings', 0)}")
        print(f"  - Модель обучена: {stats.get('model_trained', False)}")
        
        print(f"\n🌐 Запуск API сервера на {args.host}:{args.port}")
        print(f"📖 Документация: http://{args.host}:{args.port}/")
        print(f"❤️  Health check: http://{args.host}:{args.port}/health")
        print(f"📊 Статистика: http://{args.host}:{args.port}/stats")
        
        # Запускаем сервер
        api.run(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_demo(args):
    """Запускает демонстрацию системы."""
    try:
        print("🎯 ДЕМОНСТРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ")
        print("=" * 50)
        
        # Создаем систему
        auto_load = not args.no_auto_load
        system = RecommendationSystemDB(
            database_url=args.database,
            approach=args.approach,
            n_neighbors=args.neighbors,
            auto_load=auto_load
        )
        
        # Выводим статистику
        stats = system.get_system_stats()
        print(f"\n📊 Статистика системы:")
        print(f"  - Пользователей: {stats.get('n_users', 0)}")
        print(f"  - Товаров: {stats.get('n_items', 0)}")
        print(f"  - Рейтингов: {stats.get('n_ratings', 0)}")
        print(f"  - Модель обучена: {stats.get('model_trained', False)}")
        
        if stats.get('model_trained', False):
            # Получаем рекомендации для нескольких пользователей
            test_users = [1, 5, 10, 25, 50]
            
            for user_id in test_users:
                try:
                    print(f"\n🎯 Рекомендации для пользователя {user_id}:")
                    recommendations = system.get_recommendations(
                        user_id=user_id, 
                        n_recommendations=3
                    )
                    
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec['name']} ({rec['category']})")
                        print(f"     Рейтинг: {rec['predicted_rating']}, Цена: {rec['price']:.2f} руб.")
                        
                except Exception as e:
                    print(f"  ❌ Ошибка для пользователя {user_id}: {e}")
            
            # Показываем популярные товары
            print(f"\n🔥 Популярные товары:")
            popular = system.get_popular_items(5)
            for i, item in enumerate(popular, 1):
                print(f"  {i}. {item['name']} ({item['category']}) - {item['rating_count']} оценок")
        
        print(f"\n✅ Демонстрация завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка при демонстрации: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
