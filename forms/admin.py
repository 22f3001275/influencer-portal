from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField,SelectField
from wtforms.validators import Length, DataRequired, ValidationError
from db import session
from models import User
import datetime

class BanUserForm(FlaskForm):
    def validate_username(self, username):
        user = session.query(User).filter_by(
            username=username.data).first()

        if not user:
            raise ValidationError(
                'Username does not exists! Please try a different username')

    username = StringField(label='Influencer Username', validators=[
        Length(min=4, max=30), DataRequired()])
    date = DateField(label='End Date: ',  default=(
        datetime.datetime.now()+datetime.timedelta(days=7)))
    submit = SubmitField('Impose Ban')


class BanCampaignForm(FlaskForm):

    submit = SubmitField('Impose Ban')


class ChangeRedeemStatusForm(FlaskForm):
    choice = SelectField('Select User Type', choices=[
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
        ('Processed', 'Processed'),
    ])
    remarks = StringField(label='Remarks If any',default='Thank You')
    submit = SubmitField('Change Status')
