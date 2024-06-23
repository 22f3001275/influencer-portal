from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models import User


class RegisterForm(FlaskForm):
    # def validate_username(self, username_to_check):
    #     user = session.query(User).filter_by(
    #         username=username_to_check.data).first()
    #     if user:
    #         raise ValidationError(
    #             'Username already exists! Please try a different username')

    # def validate_email_address(self, email_address_to_check):
    #     user = session.query(User).filter_by(
    #         email_address=email_address_to_check.data).first()
    #     if user:
    #         raise ValidationError(
    #             'Email already exists! Please try a different email')

    username = StringField(label='Choose a Unique User Name', validators=[
                           Length(min=4, max=30), DataRequired()])
    name = StringField(label='Enter Company/Individual Name', validators=[
                           Length(min=3, max=30), DataRequired()])

    email_address = EmailField(label='Enter your Email', validators=[
                               Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[
        Length(min=6), DataRequired()])
    password_confirm = PasswordField(label='Confirm Password', validators=[
        EqualTo('password'), DataRequired()])
    register_as = SelectField('Select User Type', choices=[
        ('influencer', 'Influencer'),
        ('sponsor', 'Sponsor'),
        ('admin', 'Admin'),
    ])
    submit = SubmitField('Submit')
