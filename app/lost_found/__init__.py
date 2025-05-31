from flask import Blueprint

bp = Blueprint('lost_found', __name__)

from app.lost_found import routes 