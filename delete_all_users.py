from app import create_app, db
from app.models import User
from config import Config

app = create_app(Config)
 
with app.app_context():
    num_deleted = User.query.delete()
    db.session.commit()
    print(f"Видалено {num_deleted} користувачів.") 