from flask import Flask
from dotenv import load_dotenv
from .extensions import db, migrate, login_manager
from .config import DevelopmentConfig  # или ProductionConfig
from .models import User
from flask_login import login_user, login_required, logout_user, current_user

# Загрузка .env должна происходить до создания приложения
load_dotenv()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    #Настройка менеджера входа
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Пожалуйста, войдите в систему, чтобы получить доступ к этой странице'
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
   

    # Регистрация маршрутки
    from . import routes
    routes.init_routes(app)

    
    
    return app