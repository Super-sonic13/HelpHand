from app import db
from app.models import User, Animal

def test_create_user(app):
    user = User(username='testuser', email='test@example.com')
    db.session.add(user)
    db.session.commit()
    assert User.query.filter_by(username='testuser').first() is not None

def test_create_animal(app):
    user = User(username='owner', email='owner@example.com')
    db.session.add(user)
    db.session.commit()
    animal = Animal(name='Doggy', species='Dog', user_id=user.id)
    db.session.add(animal)
    db.session.commit()
    assert Animal.query.filter_by(name='Doggy').first() is not None 