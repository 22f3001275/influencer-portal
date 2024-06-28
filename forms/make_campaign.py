from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField,IntegerField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
import datetime

class MakeCampaign(FlaskForm):
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
    start_date = DateField(label='Start Date: ',default=datetime.datetime.now())
    end_date = DateField(label='End Date: ',  default=(datetime.datetime.now()+datetime.timedelta(days=7)))
    cost = IntegerField(label='Budget to Offer: ', validators=[DataRequired()])
    visibility  = SelectField('Select Visibility', choices=[
        ('public', 'Public'),
        ('private', 'Private'),
    ])
    goals = TextAreaField(label='Describe Your Goals Here: ',
                          validators=[DataRequired()])
    category = SelectField('Select your Category', choices=[
        ('Technology', 'Technology'),
        ('Others', 'Others'),
    ])

    submit = SubmitField('Create Campaign')
