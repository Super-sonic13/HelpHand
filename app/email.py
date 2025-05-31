from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail

NOT_PROVIDED = 'Not provided'

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_notification_email(to, subject, template):
    """
    Допоміжна функція для надсилання сповіщень через email з використанням шаблонів
    """
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[to],
        text_body=template,
        html_body=None
    )

def send_adoption_notification(user, animal, contact_info):
    """
    Надсилає підтвердження заявки на усиновлення користувачу.
    
    Аргументи:
        user: Екземпляр моделі User заявника
        animal: Екземпляр моделі Animal, якого усиновлюють
        contact_info: словник з контактними даними (ім'я, email, телефон)
    """
    subject = f"Вашу заявку на усиновлення {animal.name} отримано"
    
    text_body = render_template(
        'email/adoption_confirmation.txt',
        user=user,
        animal=animal,
        contact_name=contact_info.get('name', NOT_PROVIDED),
        contact_email=contact_info.get('email', NOT_PROVIDED),
        contact_phone=contact_info.get('phone')
    )
    
    html_body = render_template(
        'email/adoption_confirmation.html',
        user=user,
        animal=animal,
        contact_name=contact_info.get('name', NOT_PROVIDED),
        contact_email=contact_info.get('email', NOT_PROVIDED),
        contact_phone=contact_info.get('phone')
    )
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    ) 