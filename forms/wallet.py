from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField,PasswordField
from wtforms.validators import  DataRequired, ValidationError,Length
from flask_login import current_user
import requests,re



class AddMoney(FlaskForm):
    def validate_payment_amount(self, amount):
        if amount.data<100:
            raise ValidationError(
                'We currently do not support Payments less than ₹ 100')
        

    payment_amount = IntegerField(
        label='Enter Amount: ', validators=[DataRequired()])
    submit = SubmitField('Add Money')


class RedeemForm(FlaskForm):
    def validate_payment_amount(self, amount):
        if amount.data > current_user.wallet:
            raise ValidationError(
                'Not Enough Balance')
        if amount.data <100:
            raise ValidationError(
                'We currently do not support Redeem Requests less than ₹ 100')

    def validate_upi(self, upi):
        # response = requests.post(
        #     url="https://api.razorpay.com/v1/payments/validate/vpa"
        #     headers={
        #         "Content-Type": "application/json"
        #     }
        #     json={
        #         "vpa": "gauravkumar@exampleupi"
        #     }
        #     auth=HTTPBasicAuth(app.config['razorpay_key_id'],
        #                        app.config['razorpay_key_secret'])
        # )
        #! razorpay API not working right now. So temp Solution
        vpa_pattern = r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$'
        if not bool(re.match(vpa_pattern, upi.data)):
            raise ValidationError(
                'Invalid UPI ID')
        


    payment_amount = IntegerField(
        label='Enter Amount: ', validators=[DataRequired()])

    upi = PasswordField(label='UPI ID', validators=[
        Length(min=2), DataRequired()])
    submit = SubmitField('Redeem')
