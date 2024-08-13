from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from db import session
from models import User


class LoginForm(FlaskForm):
    # def validate_login_as(self,choice):
    #     entered_user = session.query(User).filter_by(
    #         username=self.username.data).first()
    #     if entered_user:
    #         if not entered_user.is_sponsor and choice.data == 'sponsor':
    #             raise ValidationError(
    #                 'User is not a sponsor')
    #         if not entered_user.is_influencer and choice.data == 'influencer':
    #             raise ValidationError(
    #                 'User is not an influencer')
        

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
