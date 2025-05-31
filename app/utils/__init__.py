from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email asynchronously."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_found_notification(report, responder):
    """Send notification email to report author when someone responds."""
    author = report.author
    if not author.email:
        return False

    try:
        send_email(
            subject='New Response to Your Report',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[author.email],
            text_body=render_template('lost_found/email/response_notification.txt',
                                    author=author, responder=responder, report=report),
            html_body=render_template('lost_found/email/response_notification.html',
                                    author=author, responder=responder, report=report)
        )
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send response notification: {str(e)}')
        return False 