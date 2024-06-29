from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from db import session
from models import User


class MakeAdRequest(FlaskForm):
    def validate_inf_username(self, inf_username):
        user = session.query(User).filter_by(
            username=inf_username.data).first()
        if not user:
            raise ValidationError(
                'Username does not exists! Please try a different username')

    inf_username = StringField(label='Influencer Username', validators=[
        Length(min=4, max=30), DataRequired()])
    messages = StringField(label='Describe Your Request', validators=[
        Length(min=20, max=200), DataRequired()])
    
    payment_amount = IntegerField(
        label='Offer Amount: ', validators=[DataRequired()])
    requirements = TextAreaField(label='Describe You Requirements here ',
                          validators=[DataRequired()])

    submit = SubmitField('Create Ad Create')
