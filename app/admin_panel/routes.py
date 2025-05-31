from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models import User, Animal, LostFoundReport, AdoptionApplication, UserRole, Adoption
from app.admin_panel import bp

@bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin_panel/index.html', title='Admin Panel')

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    return render_template('admin_panel/users.html', users=users)

@bp.route('/animals')
@login_required
@admin_required
def animals():
    page = request.args.get('page', 1, type=int)
    animals = Animal.query.paginate(page=page, per_page=20)
    return render_template('admin_panel/animals.html', animals=animals)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    page = request.args.get('page', 1, type=int)
    reports = LostFoundReport.query.paginate(page=page, per_page=20)
    return render_template('admin_panel/reports.html', reports=reports)

@bp.route('/applications')
@login_required
@admin_required
def applications():
    page = request.args.get('page', 1, type=int)
    applications = AdoptionApplication.query.paginate(page=page, per_page=20)
    return render_template('admin_panel/applications.html', applications=applications)

@bp.route('/user/<int:id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(id):
    user = User.query.get_or_404(id)
    role = request.form.get('role')
    
    if role not in [r.value for r in UserRole]:
        return jsonify({'error': 'Invalid role'}), 400
        
    user.role = role
    db.session.commit()
    return jsonify({'message': 'Role updated successfully'})

@bp.route('/application/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_application_status(id):
    application = AdoptionApplication.query.get_or_404(id)
    status = request.form.get('status')
    
    if status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
        
    application.status = status
    if status == 'approved':
        application.animal.status = 'adopted'
    elif status == 'rejected':
        application.animal.status = 'available'
        
    db.session.commit()
    return jsonify({'message': 'Application status updated successfully'})

@bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.role == UserRole.ADMIN.value:
        flash('Неможливо видалити адміністратора!', 'danger')
        return redirect(url_for('admin_panel.users'))
    # Видалити всі заявки та адопції користувача
    AdoptionApplication.query.filter_by(user_id=user.id).delete()
    Adoption.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('Користувача успішно видалено.', 'success')
    return redirect(url_for('admin_panel.users'))

@bp.route('/user/<int:id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Ви не можете деактивувати себе!'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active}) 