from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Email, URL
from app.models import Animal

class LostFoundForm(FlaskForm):
    report_type = SelectField('Тип звіту', choices=[
        ('lost', 'Загублена тварина'),
        ('found', 'Знайдена тварина')
    ], validators=[DataRequired(message='Будь ласка, виберіть тип звіту')])
    
    animal_type = SelectField('Вид тварини', choices=[
        ('dog', 'Собака'),
        ('cat', 'Кіт'),
        ('other', 'Інша тварина')
    ], validators=[DataRequired(message='Будь ласка, виберіть вид тварини')])
    
    name = StringField("Кличка тварини (якщо відома)", validators=[Optional(), Length(max=100)])
    breed = StringField('Порода (якщо відома)', validators=[Optional(), Length(max=100)])
    color = StringField('Колір', validators=[DataRequired(message='Будь ласка, вкажіть колір тварини'), Length(max=100)])
    size = SelectField('Розмір', choices=[
        ('small', 'Маленький'),
        ('medium', 'Середній'),
        ('large', 'Великий')
    ], validators=[DataRequired(message='Будь ласка, виберіть розмір тварини')])
    
    gender = SelectField('Стать', choices=[
        ('male', 'Самець'),
        ('female', 'Самиця'),
        ('unknown', 'Невідомо')
    ], validators=[Optional()])
    
    last_seen_date = DateField('Дата останньої зустрічі', validators=[DataRequired(message='Будь ласка, вкажіть дату')])
    location = StringField('Місце', validators=[DataRequired(message='Будь ласка, вкажіть місце'), Length(max=200)])
    description = TextAreaField('Опис', validators=[DataRequired(message='Будь ласка, додайте опис')])
    
    contact_name = StringField("Ім'я контактної особи", validators=[DataRequired(message="Будь ласка, вкажіть ім'я"), Length(max=100)])
    contact_email = StringField('Email', validators=[DataRequired(message='Будь ласка, вкажіть email'), Email(message='Невірний формат email'), Length(max=120)])
    contact_phone = StringField('Телефон', validators=[DataRequired(message='Будь ласка, вкажіть номер телефону'), Length(max=20)])
    
    has_collar = BooleanField('Має нашийник')
    is_microchipped = BooleanField('Має мікрочіп')
    special_needs = TextAreaField('Особливі потреби або додаткова інформація', validators=[Optional()])
    
    image = FileField('Фото', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Дозволені тільки зображення!')
    ])
    
    submit = SubmitField('Відправити звіт')

class LostFoundSearchForm(FlaskForm):
    report_type = SelectField('Тип звіту', choices=[
        ('', 'Всі звіти'),
        ('lost', 'Загублені тварини'),
        ('found', 'Знайдені тварини')
    ], validators=[Optional()])
    
    animal_type = SelectField('Вид тварини', choices=[
        ('', 'Всі види'),
        ('dog', 'Собака'),
        ('cat', 'Кіт'),
        ('other', 'Інша тварина')
    ], validators=[Optional()])
    
    breed = StringField('Порода', validators=[Optional()])
    color = StringField('Колір', validators=[Optional()])
    size = SelectField('Розмір', choices=[
        ('', 'Будь-який розмір'),
        ('small', 'Маленький'),
        ('medium', 'Середній'),
        ('large', 'Великий')
    ], validators=[Optional()])
    
    location = StringField('Місце', validators=[Optional()])
    date_from = DateField('Дата від', validators=[Optional()])
    date_to = DateField('Дата до', validators=[Optional()])
    
    submit = SubmitField('Пошук') 

class ReportResponseForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Response') 