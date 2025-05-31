from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Animal, LostFoundReport, ChatbotFeedback, AdoptionApplication
from datetime import datetime, timezone
from app.email import send_email
from flask import current_app

MAIN_DASHBOARD_ENDPOINT = 'main.dashboard'

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html', title='Home')

@bp.route('/about')
def about():
    return render_template('main/about.html', title='About Us')

@bp.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact Us')

@bp.route('/dashboard')
@login_required
def dashboard():
    user_animals = current_user.animals.all()
    # Заявки, які користувач подав на адопцію
    adoption_applications = AdoptionApplication.query.filter_by(user_id=current_user.id).all()
    lost_found_reports = current_user.lost_found_reports.order_by(LostFoundReport.created_at.desc()).all()
    # Заявки на тварин волонтера
    my_applications = []
    if current_user.is_volunteer:
        my_applications = AdoptionApplication.query.join(Animal).filter(Animal.user_id == current_user.id).all()
    return render_template(
        'main/dashboard.html',
                         title='Dashboard',
                         user_animals=user_animals,
        adoption_applications=adoption_applications,
        lost_found_reports=lost_found_reports,
        my_applications=my_applications
    )

@bp.route('/dismiss-notification', methods=['POST'])
@login_required
def dismiss_notification():
    current_user.last_notification_dismissed = datetime.now(timezone.utc)
    db.session.commit()
    return '', 204  # Відповідь без вмісту

@bp.route('/mark-responses-read', methods=['POST'])
@login_required
def mark_responses_read():
    current_user.last_response_read_time = datetime.now(timezone.utc)
    db.session.commit()
    return '', 204  # Відповідь без вмісту

@bp.route('/adoption/application/<int:id>/approve', methods=['POST'])
@login_required
def approve_application(id):
    application = AdoptionApplication.query.get_or_404(id)
    animal = application.animal
    if not (current_user.is_volunteer and animal.user_id == current_user.id):
        flash('Ви не маєте прав для цієї дії', 'danger')
        return redirect(url_for(MAIN_DASHBOARD_ENDPOINT))
    application.status = 'approved'
    animal.status = 'adopted'
    db.session.commit()
    # Відправка email заявнику
    subject = f"Ваша заявка на {animal.name} схвалена!"
    text_body = f"Вітаємо! Ваша заявка на адопцію тварини {animal.name} була схвалена волонтером. З вами зв'яжуться для подальших дій."
    send_email(subject, current_app.config['MAIL_USERNAME'], [application.email], text_body)
    flash('Заявку схвалено, заявнику надіслано лист.', 'success')
    return redirect(url_for(MAIN_DASHBOARD_ENDPOINT))

@bp.route('/adoption/application/<int:id>/reject', methods=['POST'])
@login_required
def reject_application(id):
    application = AdoptionApplication.query.get_or_404(id)
    animal = application.animal
    if not (current_user.is_volunteer and animal.user_id == current_user.id):
        flash('Ви не маєте прав для цієї дії', 'danger')
        return redirect(url_for(MAIN_DASHBOARD_ENDPOINT))
    application.status = 'rejected'
    animal.status = 'available'
    db.session.commit()
    # Відправка email заявнику
    subject = f"Ваша заявка на {animal.name} відхилена"
    text_body = f"На жаль, ваша заявка на адопцію тварини {animal.name} була відхилена волонтером. Ви можете спробувати подати заявку на іншу тварину."
    send_email(subject, current_app.config['MAIL_USERNAME'], [application.email], text_body)
    flash('Заявку відхилено, заявнику надіслано лист.', 'info')
    return redirect(url_for(MAIN_DASHBOARD_ENDPOINT)) 