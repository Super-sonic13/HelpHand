from flask import render_template, redirect, url_for, flash, request, current_app, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.lost_found import bp
from .forms import LostFoundForm, LostFoundSearchForm, ReportResponseForm
from app.models import LostFoundReport, User, ReportResponse
from app.decorators import admin_required
from app.utils import send_email, send_found_notification
from datetime import datetime, timezone

LOST_FOUND_VIEW_REPORT = 'lost_found.view_report'

@bp.route('/')
def index():
    reports = LostFoundReport.query.filter_by(is_active=True).all()
    return render_template('lost_found/index.html', title='Загублені та знайдені', reports=reports)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_report():
    if not current_user.is_active:
        abort(403)
    form = LostFoundForm()
    if form.validate_on_submit():
        report = LostFoundReport(
            report_type=form.report_type.data,
            animal_type=form.animal_type.data,
            name=form.name.data,
            breed=form.breed.data,
            color=form.color.data,
            size=form.size.data,
            last_seen_date=form.last_seen_date.data,
            location=form.location.data,
            description=form.description.data,
            contact_name=form.contact_name.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            has_collar=form.has_collar.data,
            is_microchipped=form.is_microchipped.data,
            special_needs=form.special_needs.data,
            user_id=current_user.id
        )

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app', 'static', 'uploads', filename)
            form.image.data.save(filepath)
            report.image_url = url_for('static', filename=f'uploads/{filename}')

        db.session.add(report)
        db.session.commit()
        flash('Оголошення успішно додано', 'success')
        return redirect(url_for(LOST_FOUND_VIEW_REPORT, id=report.id))
    return render_template('lost_found/create.html', title='Додати оголошення', form=form, is_edit=False, report=None)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_report(id):
    if not current_user.is_active:
        abort(403)
    report = LostFoundReport.query.get_or_404(id)
    
    # Перевірка чи користувач є автором оголошення
    if report.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    form = LostFoundForm()
    if form.validate_on_submit():
        # Оновлення полів оголошення
        report.report_type = form.report_type.data
        report.animal_type = form.animal_type.data
        report.name = form.name.data
        report.breed = form.breed.data
        report.color = form.color.data
        report.size = form.size.data
        report.last_seen_date = form.last_seen_date.data
        report.location = form.location.data
        report.description = form.description.data
        report.contact_name = form.contact_name.data
        report.contact_email = form.contact_email.data
        report.contact_phone = form.contact_phone.data
        report.has_collar = form.has_collar.data
        report.is_microchipped = form.is_microchipped.data
        report.special_needs = form.special_needs.data

        if form.image.data:
            # Видалення старого фото якщо воно є
            if report.image_url:
                old_filepath = os.path.join('app', 'static', report.image_url.lstrip('/'))
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            # Збереження нового фото
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app', 'static', 'uploads', filename)
            form.image.data.save(filepath)
            report.image_url = url_for('static', filename=f'uploads/{filename}')

        db.session.commit()
        flash('Оголошення успішно оновлено', 'success')
        return redirect(url_for(LOST_FOUND_VIEW_REPORT, id=report.id))
    elif request.method == 'GET':
        # Заповнення форми поточними даними
        form.report_type.data = report.report_type
        form.animal_type.data = report.animal_type
        form.name.data = report.name
        form.breed.data = report.breed
        form.color.data = report.color
        form.size.data = report.size
        form.last_seen_date.data = report.last_seen_date
        form.location.data = report.location
        form.description.data = report.description
        form.contact_name.data = report.contact_name
        form.contact_email.data = report.contact_email
        form.contact_phone.data = report.contact_phone
        form.has_collar.data = report.has_collar
        form.is_microchipped.data = report.is_microchipped
        form.special_needs.data = report.special_needs
        
    return render_template('lost_found/edit.html', title='Редагувати оголошення', form=form, report=report)

@bp.route('/reports')
@login_required
def list_reports():
    if not current_user.is_active:
        abort(403)
    current_user.last_response_read_time = datetime.now(timezone.utc)
    db.session.commit()
    
    page = request.args.get('page', 1, type=int)
    query = LostFoundReport.query.filter_by(is_active=True)
    
    report_type = request.args.get('type')
    if report_type:
        query = query.filter(LostFoundReport.report_type == report_type)
    animal_type = request.args.get('species')
    if animal_type:
        query = query.filter(LostFoundReport.animal_type == animal_type)
    location = request.args.get('location')
    if location:
        query = query.filter(LostFoundReport.location.ilike(f'%{location}%'))
    
    reports = query.order_by(LostFoundReport.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('lost_found/list.html', title='Загублені та знайдені тварини', reports=reports, pagination=reports)


@bp.route('/reports/<int:id>')
def view_report(id):
    report = LostFoundReport.query.get_or_404(id)
    return render_template('lost_found/view.html', title=f'Оголошення #{report.id}',
                         report=report)


@bp.route('/reports/<int:id>/delete', methods=['POST'])
@login_required
def delete_report(id):
    report = LostFoundReport.query.get_or_404(id)
    if report.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if report.image_url:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'],
                              report.image_url.lstrip('/'))
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(report)
    db.session.commit()
    flash('Оголошення успішно видалено!')
    return redirect(url_for('lost_found.list_reports'))

@bp.route('/reports/<int:id>/resolve', methods=['POST'])
@login_required
def resolve_report(id):
    report = LostFoundReport.query.get_or_404(id)
    if report.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    report.is_active = False
    db.session.commit()
    flash('Оголошення позначено як вирішене!')
    return redirect(url_for(LOST_FOUND_VIEW_REPORT, id=report.id))

@bp.route('/report/<int:id>/respond', methods=['GET', 'POST'])
@login_required
def respond_to_report(id):
    if not current_user.is_active:
        abort(403)
    report = LostFoundReport.query.get_or_404(id)
    
    if report.user_id == current_user.id:
        flash('Ви не можете відповідати на своє оголошення.')
        return redirect(url_for(LOST_FOUND_VIEW_REPORT, id=id))
    
    if not report.is_active:
        flash('Це оголошення вже вирішене.')
        return redirect(url_for(LOST_FOUND_VIEW_REPORT, id=id))
    
    form = ReportResponseForm()
    if form.validate_on_submit():
        response = ReportResponse(
            report_id=report.id,
            responder_id=current_user.id,
            message=form.message.data
        )
        db.session.add(response)
        db.session.commit()
        
        if send_found_notification(report, current_user):
            flash('The report author has been notified about your response.')
        else:
            flash('Failed to send notification email, but your response was recorded.')
        
        return redirect(url_for(LOST_FOUND_VIEW_REPORT, id=id))
    
    return render_template('lost_found/respond_form.html', report=report, form=form)

@bp.route('/my-responses')
@login_required
def my_responses():
    # Всі відповіді на оголошення користувача
    if not current_user.is_active:
        abort(403)
    reports = LostFoundReport.query.filter_by(user_id=current_user.id).all()
    responses = []
    new_responses = []
    for report in reports:
        for response in report.responses:
            responses.append(response)
            if response.timestamp > (current_user.last_response_read_time or datetime.min) and response.responder_id != current_user.id:
                new_responses.append(response)
    # Оновити last_response_read_time
    current_user.last_response_read_time = datetime.now(timezone.utc)
    db.session.commit()
    return render_template('lost_found/my_responses.html', responses=responses, new_responses=new_responses)