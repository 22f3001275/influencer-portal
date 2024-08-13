from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
import datetime
from db import session
from models import User



class EditCampaign(FlaskForm):
    # def validate_goals(self, goals):
    #     goals_list = re.split(';', goals)
    #     total_weights = 0
    #     for goal in goals_list:
    #         total_weights= int(re.split('=', goal)[1])
    #     if total_weights>100:
    #         raise ValidationError(
    #             '')

    name = StringField(label='Name Your Campaign', validators=[
        Length(min=4, max=30), DataRequired()])
    description = StringField(label='Describe Your Campaign', validators=[
        Length(min=20, max=200), DataRequired()])
    start_date = DateField(label='Start Date: ',
                           default=datetime.datetime.now())
    end_date = DateField(label='End Date: ',  default=(
        datetime.datetime.now()+datetime.timedelta(days=7)))
    cost = IntegerField(label='Budget to Offer: ', validators=[DataRequired()])
    visibility = SelectField('Select Visibility', choices=[
        ('public', 'Public'),
        ('private', 'Private'),
    ])
    goals = TextAreaField(label='Describe Your Goals Here: ',
                          validators=[DataRequired()])
    category = SelectField('Select your Category', choices=[
        ('Technology', 'Technology'),
        ('Others', 'Others'),
    ])

    submit = SubmitField('Edit Campaign')


class EditAdRequest(FlaskForm):
    def validate_inf_username(self, inf_username):
        user = session.query(User).filter_by(
            username=inf_username.data).first()

        if not user:
            raise ValidationError(
                'Username does not exists! Please try a different username')
        elif not user.is_influencer:
            raise ValidationError(
                'User is not an influencer')

    inf_username = StringField(label='Influencer Username', validators=[
        Length(min=4, max=30), DataRequired()])
    messages = StringField(label='Describe Your Request', validators=[
        Length(min=20, max=200), DataRequired()])

    payment_amount = IntegerField(
        label='Offer Amount: ', validators=[DataRequired()])
    requirements = TextAreaField(label='Describe You Requirements here ',
                                 validators=[DataRequired()])

    submit = SubmitField('Edit Ad Create')
