import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # Основные настройки MySQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    IMGS = os.getenv('IMGS', 'imgs')
    
    TELEGRAM_URL = os.getenv('TELEGRAM_URL', '')
    TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY', '')

    #Секретный ключ для авторизации
    SECRET_KEY = os.urandom(24)
    REMEMBER_COOKIE_SECURE = True
    
    # Формируем URI для подключения
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )
    
    # Настройки пула соединений
    SQLALCHEMY_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
    SQLALCHEMY_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Дополнительные настройки для продакшена
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': SQLALCHEMY_POOL_RECYCLE,
        'pool_size': SQLALCHEMY_POOL_SIZE
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Можно переопределить любые настройки для продакшена
    SQLALCHEMY_POOL_SIZE = 10