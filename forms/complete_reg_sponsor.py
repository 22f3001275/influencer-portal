from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError


class CompleteRegSponsor(FlaskForm):

    sponsor_type = SelectField('Are You', choices=[
        ('Individual', 'An Individual'),
        ('Company', 'A Company'),

    ])
    industry = SelectField('Select your Industry', choices=[
        ('Technology', 'Technology'),
        ('Others', 'Others'),

    ])
    submit = SubmitField('Complete Registration')
