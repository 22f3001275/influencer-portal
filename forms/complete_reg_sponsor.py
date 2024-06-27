from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError


class CompleteRegSponsor(FlaskForm):

    sponsor_type = SelectField('Are You', choices=[
        ('individual', 'An Individual'),
        ('company', 'A Company'),

    ])
    industry = SelectField('Select your Industry', choices=[
        ('tech', 'Technology'),
        ('others', 'Others'),

    ])
    submit = SubmitField('Complete Registration')
