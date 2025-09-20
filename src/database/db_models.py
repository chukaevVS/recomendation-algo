"""
Модели базы данных для рекомендательной системы.

Поддерживает SQLite и PostgreSQL.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, Dict, Any
import os


Base = declarative_base()


class User(Base):
    """Модель пользователя."""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(String(1))
    city = Column(String(50))
    registration_date = Column(DateTime, default=datetime.utcnow)
    preferred_categories = Column(Text)  # JSON строка с предпочтениями
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'city': self.city,
            'registration_date': self.registration_date,
            'preferred_categories': self.preferred_categories
        }


class Product(Base):
    """Модель товара."""
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    brand = Column(String(50))
    price = Column(Float, nullable=False)
    description = Column(Text)
    in_stock = Column(Boolean, default=True)
    base_rating = Column(Float, default=4.0)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'price': self.price,
            'description': self.description,
            'in_stock': self.in_stock,
            'base_rating': self.base_rating,
            'created_date': self.created_date
        }


class Rating(Base):
    """Модель рейтинга."""
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    review = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'review': self.review,
            'timestamp': self.timestamp
        }


class DatabaseManager:
    """Менеджер базы данных."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Инициализация менеджера базы данных.
        
        Args:
            database_url: URL базы данных (если None, используется SQLite)
        """
        if database_url is None:
            # Используем SQLite по умолчанию
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recommendations.db')
            database_url = f"sqlite:///{db_path}"
        
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        print(f"Подключение к базе данных: {database_url}")
    
    def create_tables(self):
        """Создает все таблицы в базе данных."""
        Base.metadata.create_all(bind=self.engine)
        print("Таблицы базы данных созданы")
    
    def get_session(self):
        """Возвращает сессию базы данных."""
        return self.SessionLocal()
    
    def load_users_from_csv(self, csv_file: str):
        """Загружает пользователей из CSV файла."""
        import pandas as pd
        
        print(f"Загрузка пользователей из {csv_file}...")
        
        # Читаем CSV
        df = pd.read_csv(csv_file)
        
        session = self.get_session()
        try:
            # Очищаем таблицу
            session.query(User).delete()
            
            # Загружаем данные
            for _, row in df.iterrows():
                user = User(
                    user_id=int(row['user_id']),
                    name=row['name'],
                    email=row['email'],
                    age=int(row['age']) if pd.notna(row['age']) else None,
                    gender=row['gender'],
                    city=row['city'],
                    registration_date=datetime.strptime(row['registration_date'], '%Y-%m-%d'),
                    preferred_categories=row['preferred_categories']
                )
                session.add(user)
            
            session.commit()
            print(f"Загружено {len(df)} пользователей")
            
        except Exception as e:
            session.rollback()
            print(f"Ошибка при загрузке пользователей: {e}")
            raise
        finally:
            session.close()
    
    def load_products_from_csv(self, csv_file: str):
        """Загружает товары из CSV файла."""
        import pandas as pd
        
        print(f"Загрузка товаров из {csv_file}...")
        
        # Читаем CSV
        df = pd.read_csv(csv_file)
        
        session = self.get_session()
        try:
            # Очищаем таблицу
            session.query(Product).delete()
            
            # Загружаем данные
            for _, row in df.iterrows():
                product = Product(
                    product_id=int(row['product_id']),
                    name=row['name'],
                    category=row['category'],
                    brand=row['brand'],
                    price=float(row['price']),
                    description=row['description'],
                    in_stock=bool(row['in_stock']),
                    base_rating=float(row['base_rating']),
                    created_date=datetime.strptime(row['created_date'], '%Y-%m-%d')
                )
                session.add(product)
            
            session.commit()
            print(f"Загружено {len(df)} товаров")
            
        except Exception as e:
            session.rollback()
            print(f"Ошибка при загрузке товаров: {e}")
            raise
        finally:
            session.close()
    
    def load_ratings_from_csv(self, csv_file: str):
        """Загружает рейтинги из CSV файла."""
        import pandas as pd
        
        print(f"Загрузка рейтингов из {csv_file}...")
        
        # Читаем CSV
        df = pd.read_csv(csv_file)
        
        session = self.get_session()
        try:
            # Очищаем таблицу
            session.query(Rating).delete()
            
            # Загружаем данные
            for _, row in df.iterrows():
                rating = Rating(
                    user_id=int(row['user_id']),
                    product_id=int(row['product_id']),
                    rating=float(row['rating']),
                    review=row['review'] if pd.notna(row['review']) else None,
                    timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                )
                session.add(rating)
            
            session.commit()
            print(f"Загружено {len(df)} рейтингов")
            
        except Exception as e:
            session.rollback()
            print(f"Ошибка при загрузке рейтингов: {e}")
            raise
        finally:
            session.close()
    
    def get_all_users(self):
        """Получает всех пользователей."""
        session = self.get_session()
        try:
            users = session.query(User).all()
            return [user.to_dict() for user in users]
        finally:
            session.close()
    
    def get_all_products(self):
        """Получает все товары."""
        session = self.get_session()
        try:
            products = session.query(Product).all()
            return [product.to_dict() for product in products]
        finally:
            session.close()
    
    def get_all_ratings(self):
        """Получает все рейтинги."""
        session = self.get_session()
        try:
            ratings = session.query(Rating).all()
            return [rating.to_dict() for rating in ratings]
        finally:
            session.close()
    
    def add_user(self, user_data: Dict[str, Any]):
        """Добавляет нового пользователя."""
        session = self.get_session()
        try:
            user = User(**user_data)
            session.add(user)
            session.commit()
            return user.user_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_product(self, product_data: Dict[str, Any]):
        """Добавляет новый товар."""
        session = self.get_session()
        try:
            product = Product(**product_data)
            session.add(product)
            session.commit()
            return product.product_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_rating(self, rating_data: Dict[str, Any]):
        """Добавляет новый рейтинг."""
        session = self.get_session()
        try:
            rating = Rating(**rating_data)
            session.add(rating)
            session.commit()
            return rating.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_by_id(self, user_id: int):
        """Получает пользователя по ID."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user.to_dict() if user else None
        finally:
            session.close()
    
    def get_product_by_id(self, product_id: int):
        """Получает товар по ID."""
        session = self.get_session()
        try:
            product = session.query(Product).filter(Product.product_id == product_id).first()
            return product.to_dict() if product else None
        finally:
            session.close()
    
    def get_user_ratings(self, user_id: int):
        """Получает рейтинги пользователя."""
        session = self.get_session()
        try:
            ratings = session.query(Rating).filter(Rating.user_id == user_id).all()
            return [rating.to_dict() for rating in ratings]
        finally:
            session.close()
    
    def get_product_ratings(self, product_id: int):
        """Получает рейтинги товара."""
        session = self.get_session()
        try:
            ratings = session.query(Rating).filter(Rating.product_id == product_id).all()
            return [rating.to_dict() for rating in ratings]
        finally:
            session.close()
    
    def get_database_stats(self):
        """Получает статистику базы данных."""
        session = self.get_session()
        try:
            users_count = session.query(User).count()
            products_count = session.query(Product).count()
            ratings_count = session.query(Rating).count()
            
            return {
                'users_count': users_count,
                'products_count': products_count,
                'ratings_count': ratings_count,
                'database_url': self.database_url
            }
        finally:
            session.close()


def create_database_from_csv(users_csv: str, products_csv: str, ratings_csv: str, 
                           database_url: Optional[str] = None):
    """
    Создает базу данных и загружает данные из CSV файлов.
    
    Args:
        users_csv: Путь к CSV файлу с пользователями
        products_csv: Путь к CSV файлу с товарами
        ratings_csv: Путь к CSV файлу с рейтингами
        database_url: URL базы данных (опционально)
    """
    print("🗄️ Создание базы данных из CSV файлов...")
    
    # Создаем менеджер базы данных
    db_manager = DatabaseManager(database_url)
    
    # Создаем таблицы
    db_manager.create_tables()
    
    # Загружаем данные
    db_manager.load_users_from_csv(users_csv)
    db_manager.load_products_from_csv(products_csv)
    db_manager.load_ratings_from_csv(ratings_csv)
    
    # Выводим статистику
    stats = db_manager.get_database_stats()
    print(f"\n✅ База данных создана:")
    print(f"  - Пользователей: {stats['users_count']}")
    print(f"  - Товаров: {stats['products_count']}")
    print(f"  - Рейтингов: {stats['ratings_count']}")
    print(f"  - База данных: {stats['database_url']}")
    
    return db_manager


if __name__ == '__main__':
    # Пример использования
    import os
    
    # Пути к CSV файлам
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    users_csv = os.path.join(data_dir, 'users.csv')
    products_csv = os.path.join(data_dir, 'products.csv')
    ratings_csv = os.path.join(data_dir, 'ratings.csv')
    
    # Проверяем существование файлов
    if all(os.path.exists(f) for f in [users_csv, products_csv, ratings_csv]):
        # Создаем базу данных
        db_manager = create_database_from_csv(users_csv, products_csv, ratings_csv)
        print("🎉 База данных готова к использованию!")
    else:
        print("❌ CSV файлы не найдены. Сначала запустите генератор данных.")
