from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, URL
from app.models import Animal
from flask_wtf.file import FileField, FileAllowed

class AdoptionApplicationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    state = StringField('State/Province', validators=[DataRequired(), Length(min=2, max=100)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=3, max=20)])
    
    housing_type = SelectField('Housing Type', choices=[
        ('own', 'Own Home'),
        ('rent', 'Rent'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    landlord_permission = BooleanField('I have permission from my landlord to have pets')
    yard = BooleanField('I have a fenced yard')
    
    previous_pets = TextAreaField('Previous Pet Experience', validators=[Optional()])
    current_pets = TextAreaField('Current Pets', validators=[Optional()])
    vet_reference = StringField('Veterinarian Reference', validators=[Optional()])
    
    adoption_reason = TextAreaField('Why do you want to adopt this animal?',
                                  validators=[DataRequired(), Length(min=10, max=500)])
    care_plan = TextAreaField('How will you care for this animal?', 
                            validators=[DataRequired(), Length(min=10, max=500)])
    
    submit = SubmitField('Submit Application')

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
    image = FileField('Фото', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    good_with_children = BooleanField('Добре з дітьми')
    good_with_other_animals = BooleanField('Добре з іншими тваринами')
    submit = SubmitField('Зберегти')

class ReservationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    housing_type = SelectField('Housing Type', 
                             choices=[('house', 'House'), 
                                    ('apartment', 'Apartment'),
                                    ('other', 'Other')],
                             validators=[DataRequired()])
    previous_pets = TextAreaField('Previous Pet Experience')
    current_pets = TextAreaField('Current Pets')
    vet_reference = StringField('Veterinarian Reference')
    adoption_reason = TextAreaField('Why do you want to adopt this pet?', validators=[DataRequired()])
    care_plan = TextAreaField('How will you care for this pet?', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Submit Reservation') 