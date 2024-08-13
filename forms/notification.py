from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Length, DataRequired, ValidationError
from db import session
from models import User


class SendNotificationForm(FlaskForm):
    def validate_login_as(self,username):
        entered_user = session.query(User).filter_by(
            username=username.data).first()
        if entered_user:
            raise ValidationError(
                    'User is does not exist')
        

    username = StringField(label='User Name', validators=[
                           Length(min=4, max=30), DataRequired()])
    messages = StringField(label='Notification MSG', validators=[
        Length(min=20, max=200), DataRequired()])

    category=SelectField('Select User Type',choices=[
        ('success','Normal'),
        ('danger', 'Urgent'),
        ('warning', 'Warning'),
        ('info', 'Info')
        ])
    submit = SubmitField('Send Message')
