from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Надсилає email асинхронно."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_found_notification(report, responder):
    """Надсилає email-сповіщення автору звіту, коли хтось відповідає."""
    author = report.author
    current_app.logger.info(f'Trying to send response notification to: {getattr(author, "email", None)}')
    if not author.email:
        current_app.logger.warning('No email found for report author.')
        return False

    try:
        send_email(
            subject='Нова відповідь на ваше оголошення',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[author.email],
            text_body=render_template('lost_found/email/response_notification.txt',
                                    author=author, responder=responder, report=report),
            html_body=render_template('lost_found/email/response_notification.html',
                                    author=author, responder=responder, report=report)
        )
        current_app.logger.info('Response notification email sent successfully.')
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send response notification: {str(e)}')
        return False 