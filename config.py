import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Базова конфігурація Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Конфігурація сесії
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    SESSION_PERMANENT = True
    
    # База даних
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Налаштування завантаження
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Налаштування пошти
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Обліковий запис адміністратора
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin'
    
    # Конфігурація OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-3.5-turbo"  # або "gpt-4" якщо є доступ
    
    # Конфігурація чат-бота
    CHATBOT_FALLBACK_MESSAGE = "Вибачте, я не можу відповісти на це питання. Будь ласка, зверніться до адміністратора."
    CHATBOT_MAX_TOKENS = 150
    CHATBOT_TEMPERATURE = 0.7
    CHATBOT_SYSTEM_MESSAGE = """Ти - асистент притулку для тварин. 
    Твоя роль - допомагати відвідувачам з питаннями про усиновлення тварин, 
    загублених тваринах та загальному догляді за тваринами. 
    Відповідай українською мовою."""
    
    # Створення необхідних директорій
    @staticmethod
    def init_app(app):
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'uploads'), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session'), exist_ok=True)
    
    # Пагінація
    ITEMS_PER_PAGE = 12 