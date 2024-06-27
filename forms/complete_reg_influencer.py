from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField, IntegerField
from wtforms.validators import  DataRequired, ValidationError

class CompleteRegInf(FlaskForm):

    category = SelectField('Select you Presence', choices=[
        ('Youtube', 'Youtube'),
        ('Instagram', 'Instagram'),
        ('X Platform', 'X Platform'),

    ])
    niche = SelectField('Select your Niche', choices=[
        ('Technology', 'Technology'),
        ('Others', 'Others'),

    ])
    reach = IntegerField(label='Enter your Approximate Reach', validators=[
        DataRequired()])

    submit = SubmitField('Complete Registration')
