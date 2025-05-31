from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User, UserRole

class LoginForm(FlaskForm):
    username = StringField("Ім'я користувача", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запам\'ятати мене')
    submit = SubmitField('Увійти')

class RegistrationForm(FlaskForm):
    username = StringField("Ім'я користувача", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Повторіть пароль", validators=[DataRequired(), EqualTo('password', message='Паролі повинні співпадати.')])
    role = SelectField(
        "Оберіть вашу роль",
        choices=[
            (UserRole.USER.value, "Звичайний користувач — хочу всиновити тварину або повідомити про загублену/знайдену"),
            (UserRole.VOLUNTEER.value, "Волонтер — хочу допомагати тваринам та керувати усиновленнями")
        ],
        validators=[DataRequired()],
        default=UserRole.USER.value
    )
    submit = SubmitField("Зареєструватися")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Користувач з таким ім'ям вже існує. Виберіть інше ім'я.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Користувач з такою електронною поштою вже існує. Виберіть іншу пошту.") 