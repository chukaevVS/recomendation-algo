#!/usr/bin/env python3
"""
Конфигурационный файл для рекомендательной системы.

Содержит все настройки системы: подключения к БД, параметры API,
настройки алгоритма рекомендаций и другие конфигурационные параметры.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""
    
    # Основные настройки БД
    url: str = "sqlite:///data/recommendations.db"
    echo: bool = False  # Логирование SQL запросов
    
    # Настройки подключения
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # PostgreSQL специфичные настройки
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "recommendations"
    postgres_username: str = "rec_user"
    postgres_password: str = "rec_password"
    
    def get_postgres_url(self) -> str:
        """Возвращает URL для PostgreSQL."""
        return f"postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
    
    def get_sqlite_url(self) -> str:
        """Возвращает URL для SQLite."""
        return "sqlite:///data/recommendations.db"


@dataclass
class APIConfig:
    """Конфигурация API сервера."""
    
    # Основные настройки сервера
    host: str = "0.0.0.0"
    port: int = 3002
    debug: bool = False
    
    # CORS настройки
    cors_origins: list = field(default_factory=lambda: ["*"])
    cors_methods: list = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: list = field(default_factory=lambda: ["Content-Type", "Authorization"])
    
    # Лимиты запросов
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    request_timeout: int = 30
    
    # Безопасность
    secret_key: str = "your-secret-key-change-in-production"
    session_cookie_secure: bool = False
    session_cookie_httponly: bool = True


@dataclass
class RecommendationConfig:
    """Конфигурация алгоритма рекомендаций."""
    
    # Основные параметры алгоритма
    approach: str = "user_based"  # user_based или item_based
    n_neighbors: int = 15
    metric: str = "cosine"  # cosine, euclidean, manhattan
    min_ratings: int = 5
    
    # Настройки производительности
    auto_load: bool = True
    cache_popular_items: bool = True
    cache_ttl: int = 3600  # Время жизни кэша в секундах
    
    # Лимиты рекомендаций
    max_recommendations: int = 100
    default_recommendations: int = 10
    max_similar_items: int = 50
    max_similar_users: int = 50


@dataclass
class LoggingConfig:
    """Конфигурация логирования."""
    
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None  # Путь к файлу логов
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class DataConfig:
    """Конфигурация данных."""
    
    # Пути к файлам данных
    data_dir: str = "data"
    users_csv: str = "data/users.csv"
    products_csv: str = "data/products.csv"
    ratings_csv: str = "data/ratings.csv"
    
    # Настройки генерации данных
    default_users_count: int = 1000
    default_products_count: int = 500
    default_ratings_per_user: int = 20
    
    # Валидация данных
    min_rating: float = 1.0
    max_rating: float = 5.0
    require_unique_emails: bool = True


@dataclass
class SystemConfig:
    """Основная конфигурация системы."""
    
    # Компоненты конфигурации
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    recommendation: RecommendationConfig = field(default_factory=RecommendationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    
    # Общие настройки
    environment: str = "development"  # development, staging, production
    version: str = "2.0.0"
    name: str = "Recommendation System"
    
    @classmethod
    def load_from_env(cls) -> 'SystemConfig':
        """Загружает конфигурацию из переменных окружения."""
        config = cls()
        
        # Переопределяем настройки из переменных окружения
        config.database.url = os.getenv("DATABASE_URL", config.database.url)
        config.database.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        
        config.api.host = os.getenv("API_HOST", config.api.host)
        config.api.port = int(os.getenv("API_PORT", config.api.port))
        config.api.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        
        config.recommendation.approach = os.getenv("RECOMMENDATION_APPROACH", config.recommendation.approach)
        config.recommendation.n_neighbors = int(os.getenv("RECOMMENDATION_NEIGHBORS", config.recommendation.n_neighbors))
        config.recommendation.metric = os.getenv("RECOMMENDATION_METRIC", config.recommendation.metric)
        
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.environment = os.getenv("ENVIRONMENT", config.environment)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует конфигурацию в словарь."""
        return {
            "database": {
                "url": self.database.url,
                "echo": self.database.echo,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "pool_timeout": self.database.pool_timeout,
                "pool_recycle": self.database.pool_recycle,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
                "cors_origins": self.api.cors_origins,
                "cors_methods": self.api.cors_methods,
                "cors_headers": self.api.cors_headers,
                "max_content_length": self.api.max_content_length,
                "request_timeout": self.api.request_timeout,
            },
            "recommendation": {
                "approach": self.recommendation.approach,
                "n_neighbors": self.recommendation.n_neighbors,
                "metric": self.recommendation.metric,
                "min_ratings": self.recommendation.min_ratings,
                "auto_load": self.recommendation.auto_load,
                "cache_popular_items": self.recommendation.cache_popular_items,
                "cache_ttl": self.recommendation.cache_ttl,
                "max_recommendations": self.recommendation.max_recommendations,
                "default_recommendations": self.recommendation.default_recommendations,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count,
            },
            "data": {
                "data_dir": self.data.data_dir,
                "users_csv": self.data.users_csv,
                "products_csv": self.data.products_csv,
                "ratings_csv": self.data.ratings_csv,
                "default_users_count": self.data.default_users_count,
                "default_products_count": self.data.default_products_count,
                "default_ratings_per_user": self.data.default_ratings_per_user,
            },
            "system": {
                "environment": self.environment,
                "version": self.version,
                "name": self.name,
            }
        }
    
    def validate(self) -> None:
        """Валидирует конфигурацию."""
        # Валидация параметров API
        if not (1 <= self.api.port <= 65535):
            raise ValueError(f"API port must be between 1 and 65535, got {self.api.port}")
        
        # Валидация параметров рекомендаций
        if self.recommendation.approach not in ["user_based", "item_based"]:
            raise ValueError(f"Recommendation approach must be 'user_based' or 'item_based', got {self.recommendation.approach}")
        
        if self.recommendation.metric not in ["cosine", "euclidean", "manhattan"]:
            raise ValueError(f"Recommendation metric must be 'cosine', 'euclidean', or 'manhattan', got {self.recommendation.metric}")
        
        if self.recommendation.n_neighbors < 1:
            raise ValueError(f"Number of neighbors must be >= 1, got {self.recommendation.n_neighbors}")
        
        if not (self.data.min_rating <= self.data.max_rating):
            raise ValueError(f"Min rating ({self.data.min_rating}) must be <= max rating ({self.data.max_rating})")


# Предустановленные конфигурации для разных окружений
DEVELOPMENT_CONFIG = SystemConfig(
    database=DatabaseConfig(
        url="sqlite:///data/recommendations.db",
        echo=True
    ),
    api=APIConfig(
        debug=True,
        port=3002
    ),
    recommendation=RecommendationConfig(
        n_neighbors=10,
        auto_load=True
    ),
    logging=LoggingConfig(
        level="DEBUG"
    ),
    environment="development"
)

STAGING_CONFIG = SystemConfig(
    database=DatabaseConfig(
        url="postgresql://rec_user:rec_password@localhost:5432/recommendations_staging",
        echo=False,
        pool_size=5,
        max_overflow=10
    ),
    api=APIConfig(
        debug=False,
        port=3002,
        cors_origins=["https://staging.example.com"]
    ),
    recommendation=RecommendationConfig(
        n_neighbors=15,
        auto_load=True,
        cache_ttl=1800
    ),
    logging=LoggingConfig(
        level="INFO",
        file="logs/recommendation_staging.log"
    ),
    environment="staging"
)

PRODUCTION_CONFIG = SystemConfig(
    database=DatabaseConfig(
        url="postgresql://rec_user:rec_password@db.example.com:5432/recommendations",
        echo=False,
        pool_size=20,
        max_overflow=30,
        pool_recycle=1800
    ),
    api=APIConfig(
        debug=False,
        port=80,
        cors_origins=["https://example.com", "https://www.example.com"],
        secret_key="your-very-secure-secret-key-here",
        session_cookie_secure=True
    ),
    recommendation=RecommendationConfig(
        n_neighbors=20,
        auto_load=True,
        cache_ttl=3600,
        max_recommendations=50
    ),
    logging=LoggingConfig(
        level="WARNING",
        file="logs/recommendation_production.log",
        max_file_size=50 * 1024 * 1024,  # 50MB
        backup_count=10
    ),
    environment="production"
)


def get_config(environment: Optional[str] = None) -> SystemConfig:
    """
    Возвращает конфигурацию для указанного окружения.
    
    Args:
        environment: Окружение (development, staging, production) или None для автовыбора
        
    Returns:
        Конфигурация системы
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    # Загружаем базовую конфигурацию для окружения
    if environment == "development":
        config = DEVELOPMENT_CONFIG
    elif environment == "staging":
        config = STAGING_CONFIG
    elif environment == "production":
        config = PRODUCTION_CONFIG
    else:
        raise ValueError(f"Unknown environment: {environment}")
    
    # Переопределяем настройки из переменных окружения
    config = SystemConfig.load_from_env()
    
    # Валидируем конфигурацию
    config.validate()
    
    return config


# Глобальная конфигурация (загружается при импорте)
config = get_config()


if __name__ == "__main__":
    # Демонстрация использования конфигурации
    print("🔧 КОНФИГУРАЦИЯ РЕКОМЕНДАТЕЛЬНОЙ СИСТЕМЫ")
    print("=" * 50)
    
    # Загружаем конфигурацию
    cfg = get_config()
    
    print(f"Окружение: {cfg.environment}")
    print(f"Версия: {cfg.version}")
    print(f"База данных: {cfg.database.url}")
    print(f"API: {cfg.api.host}:{cfg.api.port}")
    print(f"Режим отладки: {cfg.api.debug}")
    print(f"Алгоритм: {cfg.recommendation.approach}")
    print(f"Количество соседей: {cfg.recommendation.n_neighbors}")
    print(f"Метрика: {cfg.recommendation.metric}")
    print(f"Автозагрузка: {cfg.recommendation.auto_load}")
    
    print("\n📊 Полная конфигурация:")
    import json
    print(json.dumps(cfg.to_dict(), indent=2, ensure_ascii=False))
