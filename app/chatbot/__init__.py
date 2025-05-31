from flask import Blueprint

bp = Blueprint('chatbot', __name__)

from app.chatbot import routes
from dotenv import load_dotenv
load_dotenv()