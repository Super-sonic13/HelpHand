from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.adoption import bp
from app.adoption.forms import AnimalForm, ReservationForm, AnimalFilterForm
from app.models import Animal, Adoption, AdoptionApplication
from app.decorators import admin_required, volunteer_required
from app.email import send_adoption_notification
from werkzeug.utils import secure_filename
import os

ANIMAL_DETAILS_ENDPOINT = 'adoption.animal_details'

@bp.route('/')
def list_animals():
    form = AnimalFilterForm(request.args)
    page = request.args.get('page', 1, type=int)
    query = Animal.query.filter_by(status='available')
    if form.species.data:
        query = query.filter(Animal.species == form.species.data)
    if form.age.data:
        if form.age.data == '0-1':
            query = query.filter(db.cast(Animal.age, db.Integer) >= 0, db.cast(Animal.age, db.Integer) <= 1)
        elif form.age.data == '1-5':
            query = query.filter(db.cast(Animal.age, db.Integer) >= 1, db.cast(Animal.age, db.Integer) <= 5)
        elif form.age.data == '5-8':
            query = query.filter(db.cast(Animal.age, db.Integer) >= 5, db.cast(Animal.age, db.Integer) <= 8)
        elif form.age.data == '8+':
            query = query.filter(db.cast(Animal.age, db.Integer) >= 8)
    if form.gender.data:
        query = query.filter(Animal.gender == form.gender.data)
    if form.size.data:
        query = query.filter(Animal.size == form.size.data)
    if form.breed.data:
        query = query.filter(Animal.breed.ilike(f"%{form.breed.data}%"))
    if form.good_with_children.data:
        query = query.filter(Animal.good_with_children == True)
    if form.good_with_other_animals.data:
        query = query.filter(Animal.good_with_other_animals == True)
    animals = query.paginate(page=page, per_page=9)
    return render_template('adoption/list.html', title='Доступні тварини', animals=animals.items, pagination=animals, form=form)

@bp.route('/adoption/<int:id>')
def animal_details(id):
    animal = Animal.query.get_or_404(id)
    form = ReservationForm()
    return render_template('adoption/details.html', title=animal.name, animal=animal, form=form)

@bp.route('/animal/<int:id>/adopt', methods=['GET', 'POST'])
@login_required
def adopt_animal(id):
    animal = Animal.query.get_or_404(id)
    if animal.status != 'available':
        flash('Ця тварина недоступна для усиновлення', 'error')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
    return render_template('adoption/adopt.html', title=f'Всиновити {animal.name}', animal=animal)

@bp.route('/applications')
@login_required
def my_applications():
    return redirect(url_for('main.dashboard'))

@bp.route('/applications/<int:id>')
@login_required
def view_application(id):
    application = AdoptionApplication.query.get_or_404(id)
    if application.user_id != current_user.id and not current_user.is_admin:
        flash('У вас немає прав для перегляду цієї заявки', 'error')
        return redirect(url_for('adoption.my_applications'))
    return render_template('adoption/application_detail.html', title='Деталі заявки', application=application)

@bp.route('/applications/<int:id>/update', methods=['POST'])
@login_required
@admin_required
def update_application(id):
    application = AdoptionApplication.query.get_or_404(id)
    status = request.form.get('status')
    if status in ['approved', 'rejected']:
        application.status = status
        db.session.commit()
        flash('Заявку оновлено', 'success')
        return redirect(url_for('adoption.view_application', id=id))
    flash('Невірний статус', 'error')
    return redirect(url_for('adoption.view_application', id=id))

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@volunteer_required
def add_animal():
    form = AnimalForm()
    if form.validate_on_submit():
        animal = Animal(
            name=form.name.data,
            species=form.species.data,
            breed=form.breed.data,
            age=form.age.data,
            gender=form.gender.data,
            size=form.size.data,
            description=form.description.data,
            good_with_children=form.good_with_children.data,
            good_with_other_animals=form.good_with_other_animals.data,
            user_id=current_user.id,
            status='available'
        )
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app', 'static', 'uploads', filename)
            form.image.data.save(filepath)
            animal.image_url = url_for('static', filename=f'uploads/{filename}')
        db.session.add(animal)
        db.session.commit()
        flash('Тварину успішно додано', 'success')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=animal.id))
    return render_template('adoption/form_animal.html', title='Додати тварину', form=form, is_edit=False, animal=None)

@bp.route('/test-adoption-flow')
@login_required
@admin_required
def test_adoption_flow():
    try:
        test_animal = Animal(
            name="Тестова тварина",
            species="Собака",
            breed="Тестова порода",
            age="Молода",
            gender="Самець",
            size="Середній",
            description="Тестова тварина для перевірки процесу усиновлення",
            status="available",
            user_id=current_user.id
        )
        db.session.add(test_animal)
        db.session.commit()
        adoption = Adoption(animal_id=test_animal.id, user_id=current_user.id)
        test_animal.status = 'pending'
        db.session.add(adoption)
        db.session.commit()
        contact_info = {
            'name': 'Тестовий контакт',
            'email': current_app.config['MAIL_USERNAME'],
            'phone': '123-456-7890'
        }
        send_adoption_notification(current_user, test_animal, contact_info)

        db.session.delete(adoption)
        db.session.delete(test_animal)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Тестовий процес усиновлення успішно завершено. Перевірте вашу електронну пошту.',
            'details': {
                'animal_id': test_animal.id,
                'user_id': current_user.id,
                'email_sent_to': current_user.email
            }
        })
    except Exception:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Тест не пройшов.'
        }), 500

@bp.route('/animal/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@volunteer_required
def edit_animal(id):
    animal = Animal.query.get_or_404(id)
    if animal.user_id != current_user.id and not current_user.is_admin:
        flash('У вас немає прав для редагування цієї тварини', 'error')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
    form = AnimalForm()
    if form.validate_on_submit():
        animal.name = form.name.data
        animal.species = form.species.data
        animal.breed = form.breed.data
        animal.age = form.age.data
        animal.gender = form.gender.data
        animal.size = form.size.data
        animal.description = form.description.data
        animal.good_with_children = form.good_with_children.data
        animal.good_with_other_animals = form.good_with_other_animals.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app', 'static', 'uploads', filename)
            form.image.data.save(filepath)
            animal.image_url = url_for('static', filename=f'uploads/{filename}')
        db.session.commit()
        flash('Тварину успішно оновлено', 'success')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=animal.id))
    elif request.method == 'GET':
        form.name.data = animal.name
        form.species.data = animal.species
        form.breed.data = animal.breed
        form.age.data = animal.age
        form.gender.data = animal.gender
        form.size.data = animal.size
        form.description.data = animal.description
        form.good_with_children.data = animal.good_with_children
        form.good_with_other_animals.data = animal.good_with_other_animals
    return render_template('adoption/form_animal.html', title='Edit Animal', form=form, is_edit=True, animal=animal)

@bp.route('/animal/<int:id>/delete', methods=['POST'])
@login_required
@volunteer_required
def delete_animal(id):
    animal = Animal.query.get_or_404(id)
    # Дозволяємо адміну видаляти будь-яку тварину
    if not current_user.is_admin:
        if animal.user_id != current_user.id:
            flash('У вас немає прав для видалення цієї тварини', 'error')
            return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
        # Для волонтера залишаємо перевірку статусу
    if animal.status not in ['available', 'reserved']:
        flash('Не можна видалити тварину, яка вже усиновлена або в процесі усиновлення', 'error')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
    try:
        # Видалити всі заявки та адопції, пов'язані з твариною
        AdoptionApplication.query.filter_by(animal_id=animal.id).delete()
        Adoption.query.filter_by(animal_id=animal.id).delete()
        db.session.delete(animal)
        db.session.commit()
        flash('Тварину успішно видалено', 'success')
        return redirect(url_for('adoption.list_animals'))
    except Exception:
        db.session.rollback()
        flash('Помилка при видаленні тварини', 'error')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))

def notify_applicant(current_user, animal, contact_info):
    try:
        send_adoption_notification(current_user, animal, contact_info)
    except Exception as email_error:
        current_app.logger.error(f"Failed to send adoption notification email: {str(email_error)}")

def notify_volunteer(animal, application):
    try:
        if animal.owner and animal.owner.email:
            from app.email import send_email
            subject = f"Нова заявка на адопцію для {animal.name}"
            text_body = (
                f"Ваша тварина: {animal.name}\n\n"
                f"Заявник: {getattr(current_user, 'full_name', current_user.username)}\n"
                f"Email: {current_user.email}\n"
                f"Телефон: {getattr(current_user, 'phone', '-')}\n\n"
                f"Причина адопції: {application.adoption_reason}\n\n"
                "Перейдіть у кабінет для підтвердження або відмови."
            )
            send_email(subject, current_app.config['MAIL_USERNAME'], [animal.owner.email], text_body)
    except Exception as email_error:
        current_app.logger.error(f"Failed to send volunteer notification email: {str(email_error)}")

@bp.route('/adoption/<int:id>/reserve', methods=['GET', 'POST'])
@login_required
def reserve_animal(id):
    animal = Animal.query.get_or_404(id)
    if animal.status != 'available':
        flash('Ця тварина недоступна для резервування.', 'error')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
    
    existing_application = AdoptionApplication.query.filter_by(
        user_id=current_user.id,
        animal_id=animal.id,
        status='pending'
    ).first()
    
    if existing_application:
        flash('У вас вже є заявка на цю тварину.', 'warning')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
    
    form = ReservationForm()
    
    if request.method == 'GET':
        form.full_name.data = getattr(current_user, 'full_name', '')
        form.email.data = current_user.email
        form.phone.data = getattr(current_user, 'phone', '')
    
    if form.validate_on_submit():
        application = AdoptionApplication(
            user_id=current_user.id,
            animal_id=animal.id,
            status='pending',
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            housing_type=form.housing_type.data,
            previous_pets=form.previous_pets.data,
            current_pets=form.current_pets.data,
            vet_reference=form.vet_reference.data,
            adoption_reason=form.adoption_reason.data,
            care_plan=form.care_plan.data,
            notes=form.notes.data
        )
        
        animal.status = 'reserved'
        db.session.add(application)
        db.session.commit()
        contact_info = {
            'name': animal.owner.username if animal.owner else 'Shelter Staff',
            'email': animal.owner.email if animal.owner else current_app.config['MAIL_USERNAME'],
            'phone': animal.owner.phone if animal.owner and hasattr(animal.owner, 'phone') else 'Not available'
        }
        notify_applicant(current_user, animal, contact_info)
        notify_volunteer(animal, application)
        flash('Ваша заявка на усиновлення успішно подана!', 'success')
        return redirect(url_for(ANIMAL_DETAILS_ENDPOINT, id=id))
    return render_template('adoption/reserve.html', animal=animal, form=form) 