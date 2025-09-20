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
from config import get_config, SystemConfig


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

  # Запуск в production режиме
  ENVIRONMENT=production python app.py

  # Показать текущую конфигурацию
  python app.py --show-config
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['api', 'demo', 'config'],
        default='api',
        help='Режим запуска: api (сервер), demo (демонстрация) или config (показать конфигурацию)'
    )
    
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default=None,
        help='Окружение для загрузки конфигурации (development, staging, production)'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        default=None,
        help='URL базы данных (переопределяет конфигурацию)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='Хост для API сервера (переопределяет конфигурацию)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Порт для API сервера (переопределяет конфигурацию)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Запуск в режиме отладки (переопределяет конфигурацию)'
    )
    
    parser.add_argument(
        '--no-auto-load',
        action='store_true',
        help='Не загружать данные и не обучать модель автоматически'
    )
    
    parser.add_argument(
        '--approach',
        choices=['user_based', 'item_based'],
        default=None,
        help='Подход к рекомендациям (переопределяет конфигурацию)'
    )
    
    parser.add_argument(
        '--neighbors',
        type=int,
        default=None,
        help='Количество ближайших соседей для k-NN (переопределяет конфигурацию)'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Показать текущую конфигурацию и выйти'
    )
    
    args = parser.parse_args()
    
    # Загружаем конфигурацию
    config = get_config(args.environment)
    
    # Переопределяем настройки из аргументов командной строки
    if args.database:
        config.database.url = args.database
    if args.host:
        config.api.host = args.host
    if args.port:
        config.api.port = args.port
    if args.debug:
        config.api.debug = True
    if args.approach:
        config.recommendation.approach = args.approach
    if args.neighbors:
        config.recommendation.n_neighbors = args.neighbors
    if args.no_auto_load:
        config.recommendation.auto_load = False
    
    # Валидируем конфигурацию
    config.validate()
    
    print("🚀 РЕКОМЕНДАТЕЛЬНАЯ СИСТЕМА")
    print("=" * 50)
    print(f"Режим: {args.mode}")
    print(f"Окружение: {config.environment}")
    print(f"База данных: {config.database.url}")
    print(f"API: {config.api.host}:{config.api.port}")
    print(f"Подход: {config.recommendation.approach}")
    print(f"Соседей: {config.recommendation.n_neighbors}")
    print(f"Автозагрузка: {config.recommendation.auto_load}")
    print("=" * 50)
    
    if args.show_config or args.mode == 'config':
        show_config(config)
        return
    
    if args.mode == 'api':
        run_api_server(config)
    elif args.mode == 'demo':
        run_demo(config)


def show_config(config: SystemConfig):
    """Показывает текущую конфигурацию."""
    print("🔧 ТЕКУЩАЯ КОНФИГУРАЦИЯ")
    print("=" * 50)
    
    import json
    config_dict = config.to_dict()
    print(json.dumps(config_dict, indent=2, ensure_ascii=False))


def run_api_server(config: SystemConfig):
    """Запускает API сервер."""
    try:
        print("🏗️ Создание рекомендательной системы...")
        
        # Создаем систему с автоматической загрузкой данных
        system = RecommendationSystemDB(
            database_url=config.database.url,
            approach=config.recommendation.approach,
            n_neighbors=config.recommendation.n_neighbors,
            metric=config.recommendation.metric,
            min_ratings=config.recommendation.min_ratings,
            auto_load=config.recommendation.auto_load
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
        
        print(f"\n🌐 Запуск API сервера на {config.api.host}:{config.api.port}")
        print(f"📖 Документация: http://{config.api.host}:{config.api.port}/")
        print(f"❤️  Health check: http://{config.api.host}:{config.api.port}/health")
        print(f"📊 Статистика: http://{config.api.host}:{config.api.port}/stats")
        
        # Запускаем сервер
        api.run(host=config.api.host, port=config.api.port, debug=config.api.debug)
        
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        if config.api.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_demo(config: SystemConfig):
    """Запускает демонстрацию системы."""
    try:
        print("🎯 ДЕМОНСТРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ")
        print("=" * 50)
        
        # Создаем систему
        system = RecommendationSystemDB(
            database_url=config.database.url,
            approach=config.recommendation.approach,
            n_neighbors=config.recommendation.n_neighbors,
            metric=config.recommendation.metric,
            min_ratings=config.recommendation.min_ratings,
            auto_load=config.recommendation.auto_load
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
        if config.api.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
