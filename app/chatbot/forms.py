from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ChatMessageForm(FlaskForm):
    message = StringField('Message', validators=[
        DataRequired(),
        Length(min=1, max=500)
    ])
    submit = SubmitField('Send') 