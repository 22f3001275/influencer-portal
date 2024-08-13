from app import app
from forms import RedeemForm
from flask_login import login_required,current_user
from flask import render_template,flash,request,redirect,url_for
from models import RedeemRequest
from datetime import datetime as dt
from db import session


@app.route('/redeem', methods=['GET','POST'])
@login_required
def redeem_page():
    form =RedeemForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.wallet - form.payment_amount.data <1000:
                flash(f'Minimum balance after redeem should be at least ₹1000',category='danger')
                return redirect(url_for('redeem_page'))
            new_request= RedeemRequest(
                user_id=current_user.id,
                payment_amount= form.payment_amount.data,
                upi_id=form.upi.data,
                timestamp=dt.now()
            )
            current_user.deduct_balance(form.payment_amount.data)
            current_user.notify(
                notification=f'Your Redeem request for ₹ {form.payment_amount.data} has been received. It will be processed shortly ', category='success')


            flash(
                f'Your Redeem request for ₹ {form.payment_amount.data} has been received. It will be processed shortly ', category='success')

            session.add(new_request)
            session.commit()
        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error[0]}', category='danger')
        return redirect(url_for('redeem_page'))
        
    if request.method == 'GET':
        return render_template('redeem.html',form=form)