from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import  DataRequired, ValidationError



class AddMoney(FlaskForm):
    def validate_payment_amount(self, amount):
        if amount.data<100:
            raise ValidationError(
                'We currently do not support Payments less than ₹ 100')

    payment_amount = IntegerField(
        label='Enter Amount: ', validators=[DataRequired()])

    submit = SubmitField('Add Money')
