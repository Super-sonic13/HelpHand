import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_session import Session
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
mail = Mail()
session = Session()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Встановлення власного інтерфейсу сесії
    app.config['SESSION_TYPE'] = 'filesystem'
    session.init_app(app)
    
    # Забезпечення існування директорії instance
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ініціалізація розширень
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Ініціалізація налаштувань конфігурації
    config_class.init_app(app)

    # Налаштування менеджера входу
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'

    with app.app_context():
        # Реєстрація блюпринтів
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)
        
        from app.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        
        from app.adoption import bp as adoption_bp
        app.register_blueprint(adoption_bp, url_prefix='/adoption')
        
        from app.lost_found import bp as lost_found_bp
        app.register_blueprint(lost_found_bp, url_prefix='/lost-found')
        
        from app.chatbot import bp as chatbot_bp
        app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
        
        from app.admin_panel import bp as admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # Реєстрація CLI команд
        from app.cli import register_commands
        register_commands(app)
        
        # Ініціалізація бази даних
        from app import models
        db.create_all()

    return app 