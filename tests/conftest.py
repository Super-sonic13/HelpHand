import pytest
from app import create_app, db
from flask import template_rendered
from contextlib import contextmanager

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def setup_db(app):
    db.create_all()
    yield
    db.session.remove()
    db.drop_all() 