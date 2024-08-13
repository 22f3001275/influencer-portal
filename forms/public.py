from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Length, DataRequired


class SearchForm(FlaskForm):

    query = StringField(label='User Name', validators=[
                           Length(min=0, max=30)])

    choice = SelectField('Select User Type', choices=[
        ('user', 'User'),
        ('campaign', 'Campaign')
    ])
    submit = SubmitField('Search Query')
