from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField,StringField,FileField
from wtforms.validators import DataRequired

class AdReqForm(FlaskForm):
    choice = SelectField('Select Action Type', choices=[
        ('accept', 'Accept Offer'),
        ('reject', 'Reject Offer'),
        ('reject_for_modification', 'Reject and Create new Campaign Request'),
    ])
    submit=SubmitField('Done')


class CampaignReqForm(FlaskForm):
    choice = SelectField('Select Action Type', choices=[
        ('accept', 'Accept Offer'),
        ('reject', 'Reject Offer'),
        ('reject_for_modification', 'Reject and Create new Ad Request'),
    ])
    submit = SubmitField('Done')


class VerifySecretKey(FlaskForm):
    secret_key = StringField(label='Enter Secret Key', validators=[
        DataRequired()])
    submit = SubmitField('Done')


class ProfilePicForm(FlaskForm):
    profile_pic = FileField('Profile Pic')
    submit = SubmitField('Done')

