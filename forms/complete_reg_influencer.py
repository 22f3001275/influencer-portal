from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError



class CompleteRegInf(FlaskForm):

    username = StringField(label='User Name', validators=[
                           Length(min=4, max=30), DataRequired()])
    password = PasswordField(label='Password', validators=[
        Length(min=6), DataRequired()])
    Category=SelectField('Select User Type',choices=[
        ('youtube','Youtube'),
        ('instagram', 'Instagram'),
        ('x', 'X, formely Twitter'),

        ])
    submit = SubmitField('Login')
