from flask import Blueprint

bp = Blueprint('adoption', __name__)

from app.adoption import routes