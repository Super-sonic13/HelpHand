from app import create_app, db
from app.models import User
from config import Config

app = create_app()

with app.app_context():
    # Перевірка чи адмін вже існує
    admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=Config.ADMIN_EMAIL,
            is_admin=True
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print('Адміністратора створено')
    else:
        print('Адміністратор вже існує')

if __name__ == '__main__':
    create_admin() 