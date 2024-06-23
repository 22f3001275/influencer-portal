from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError



class LoginForm(FlaskForm):

    username = StringField(label='User Name', validators=[
                           Length(min=4, max=30), DataRequired()])
    password = PasswordField(label='Password', validators=[
        Length(min=6), DataRequired()])
    login_as=SelectField('Select User Type',choices=[
        ('influencer','Influencer'),
        ('sponsor', 'Sponsor'),
        ('admin', 'Admin'),
        ])
    submit = SubmitField('Login')
