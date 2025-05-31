import click
from flask.cli import with_appcontext
from app import db
from app.models import User, UserRole

def register_commands(app):
    @app.cli.command("create_admin")
    @with_appcontext
    def create_admin():
        """Створює адміністратора, якщо він не існує."""
        try:
            if not User.query.filter_by(role=UserRole.ADMIN.value).first():
                admin = User(
                    username=app.config['ADMIN_USERNAME'],
                    email=app.config['ADMIN_EMAIL'],
                    role=UserRole.ADMIN.value
                )
                admin.set_password(app.config['ADMIN_PASSWORD'])
                db.session.add(admin)
                db.session.commit()
                click.echo('Адміністратора успішно створено.')
            else:
                click.echo('Адміністратор вже існує.')
        except Exception as e:
            click.echo(f"Помилка створення адміністратора: {e}") 