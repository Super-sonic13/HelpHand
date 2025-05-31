from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, URL
from app.models import Animal
from flask_wtf.file import FileField, FileAllowed

class AdoptionApplicationForm(FlaskForm):
    full_name = StringField('Повне ім\'я', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Адреса', validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField('Місто', validators=[DataRequired(), Length(min=2, max=100)])
    state = StringField('Область', validators=[DataRequired(), Length(min=2, max=100)])
    postal_code = StringField('Поштовий індекс', validators=[DataRequired(), Length(min=3, max=20)])
    
    housing_type = SelectField('Тип житла', choices=[
        ('own', 'Власне житло'),
        ('rent', 'Оренда'),
        ('other', 'Інше')
    ], validators=[DataRequired()])
    landlord_permission = BooleanField('У мене є дозвіл від власника житла на утримання тварин')
    yard = BooleanField('У мене є огороджений двір')
    
    previous_pets = TextAreaField('Досвід утримання тварин', validators=[Optional()])
    current_pets = TextAreaField('Поточні тварини', validators=[Optional()])
    vet_reference = StringField('Контакт ветеринара', validators=[Optional()])
    
    adoption_reason = TextAreaField('Чому ви хочете всиновити цю тварину?',
                                  validators=[DataRequired(), Length(min=10, max=500)])
    care_plan = TextAreaField('Як ви будете доглядати за цією твариною?', 
                            validators=[DataRequired(), Length(min=10, max=500)])
    
    submit = SubmitField('Подати заявку')

class AnimalFilterForm(FlaskForm):
    species = SelectField('Вид', choices=[
        ('', 'Всі види'),
        ('dog', 'Собака'),
        ('cat', 'Кіт'),
        ('other', 'Інше')
    ], validators=[Optional()])
    
    breed = StringField('Порода', validators=[Optional()])
    
    age = SelectField('Вік', choices=[
        ('', 'Будь-який вік'),
        ('0-1', '0-1 рік'),
        ('1-5', '1-5 років'),
        ('5-8', '5-8 років'),
        ('8+', '8+ років')
    ], validators=[Optional()])
    
    gender = SelectField('Стать', choices=[
        ('', 'Будь-яка стать'),
        ('male', 'Самець'),
        ('female', 'Самиця')
    ], validators=[Optional()])
    
    size = SelectField('Розмір', choices=[
        ('', 'Будь-який розмір'),
        ('small', 'Малий'),
        ('medium', 'Середній'),
        ('large', 'Великий')
    ], validators=[Optional()])
    
    good_with_children = BooleanField('Добре з дітьми', validators=[Optional()])
    good_with_other_animals = BooleanField('Добре з іншими тваринами', validators=[Optional()])
    
    submit = SubmitField('Застосувати фільтри')

class AnimalForm(FlaskForm):
    name = StringField('Кличка', validators=[DataRequired(), Length(max=100)])
    species = SelectField('Вид', choices=[('dog', 'Собака'), ('cat', 'Кіт'), ('other', 'Інше')], validators=[DataRequired()])
    breed = StringField('Порода', validators=[Optional(), Length(max=100)])
    age = SelectField('Вік', choices=[
        ('0-1', '0-1 рік'),
        ('1-3', '1-3 роки'),
        ('3-5', '3-5 років'),
        ('5-8', '5-8 років'),
        ('8+', '8+ років')
    ], validators=[DataRequired()])
    gender = SelectField('Стать', choices=[('male', 'Самець'), ('female', 'Самиця')], validators=[DataRequired()])
    size = SelectField('Розмір', choices=[('small', 'Малий'), ('medium', 'Середній'), ('large', 'Великий')], validators=[DataRequired()])
    description = TextAreaField('Опис', validators=[DataRequired()])
    image = FileField('Фото', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Тільки зображення!')])
    image_url = StringField('URL зображення', validators=[Optional(), URL()])
    good_with_children = BooleanField('Добре з дітьми')
    good_with_other_animals = BooleanField('Добре з іншими тваринами')
    submit = SubmitField('Зберегти')

class ReservationForm(FlaskForm):
    full_name = StringField('Повне ім\'я', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Номер телефону', validators=[DataRequired()])
    address = StringField('Адреса', validators=[DataRequired()])
    city = StringField('Місто', validators=[DataRequired()])
    state = StringField('Область', validators=[DataRequired()])
    postal_code = StringField('Поштовий індекс', validators=[DataRequired()])
    housing_type = SelectField('Тип житла', 
                             choices=[('house', 'Будинок'), 
                                    ('apartment', 'Квартира'),
                                    ('other', 'Інше')],
                             validators=[DataRequired()])
    previous_pets = TextAreaField('Досвід утримання тварин')
    current_pets = TextAreaField('Поточні тварини')
    vet_reference = StringField('Контакт ветеринара')
    adoption_reason = TextAreaField('Чому ви хочете всиновити цю тварину?', validators=[DataRequired()])
    care_plan = TextAreaField('Як ви будете доглядати за цією твариною?', validators=[DataRequired()])
    notes = TextAreaField('Додаткові примітки')
    submit = SubmitField('Подати заявку') 