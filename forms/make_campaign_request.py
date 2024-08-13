from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from db import session
from models import User


class MakeCampaignRequest(FlaskForm):
    messages = StringField(label='Describe Your Request', validators=[
        Length(min=20, max=200), DataRequired()])
    
    payment_amount = IntegerField(
        label='Offer Amount: ', validators=[DataRequired()])

    submit = SubmitField('Create Campaign Request')
