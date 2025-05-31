from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from datetime import datetime, timezone

MAIN_INDEX_ENDPOINT = 'main.index'
AUTH_LOGIN_ENDPOINT = 'auth.login'

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for(AUTH_LOGIN_ENDPOINT))
        if not user.is_active:
            flash('Ваш акаунт заблоковано. Зверніться до адміністратора.', 'error')
            return redirect(url_for(AUTH_LOGIN_ENDPOINT))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for(MAIN_INDEX_ENDPOINT)
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for(MAIN_INDEX_ENDPOINT))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Користувач з такою електронною поштою вже існує.', 'error')
            return redirect(url_for(AUTH_LOGIN_ENDPOINT))
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for(AUTH_LOGIN_ENDPOINT))
    return render_template('auth/register.html', title='Register', form=form) 

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