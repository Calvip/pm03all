from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True,  nullable=False)
    telegram_id = db.Column(db.String(60), nullable=True)

    def get_id(self):
        return str(self.id)  # Flask-Login ожидает строку
    
    def __repr__(self):
        return f'<User {self.username}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    patronymic = db.Column(db.String(64), nullable=False)
    account_number = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Client {self.username}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f'<Client {self.username}>'