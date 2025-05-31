from flask import request, jsonify, render_template
from .ai_handler import get_gemini_response
from app.chatbot import bp


@bp.route('/')
def chat():
    return render_template('chatbot/chat.html', title='Чат з ботом')

@bp.route('/send', methods=['POST'])
def chatbot_send():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'response': 'Повідомлення порожнє'}), 400

    response = get_gemini_response(user_message)
    return jsonify({'response': response})