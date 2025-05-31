import pytest
from app.models import Animal, User
from app import db

def test_main_index(client):
    resp = client.get('/')
    assert resp.status_code == 200

def test_adoption_list(client, app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        animal = Animal(name='Doggy', species='Dog', user_id=user.id)
        db.session.add(animal)
        db.session.commit()
    resp = client.get('/adoption/', follow_redirects=True)
    assert resp.status_code == 200

def test_lost_found_list(client, app):
    with app.app_context():
        user = User(username='finder', email='finder@example.com')
        db.session.add(user)
        db.session.commit()
        animal = Animal(name='LostPet', species='Cat', user_id=user.id, status='lost')
        db.session.add(animal)
        db.session.commit()
    resp = client.get('/lost-found/', follow_redirects=True)
    assert resp.status_code == 200

def test_auth_login_page(client):
    resp = client.get('/auth/login', follow_redirects=True)
    assert resp.status_code == 200

def test_auth_register_page(client):
    resp = client.get('/auth/register', follow_redirects=True)
    assert resp.status_code == 200


def test_auth_login_functionality(client, app):
    user = User(username='loginuser', email='login@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    resp = client.post('/auth/login', data=dict(
        email='login@example.com',
        password='password123'
    ), follow_redirects=True)
    assert resp.status_code == 200

def test_auth_logout_functionality(client, app):
    with app.app_context():
        user = User(username='logoutuser', email='logout@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    client.post('/auth/login', data=dict(
        email='logout@example.com',
        password='password123'
    ), follow_redirects=True)
    resp_logout = client.get('/auth/logout', follow_redirects=True)
    assert resp_logout.status_code == 200
