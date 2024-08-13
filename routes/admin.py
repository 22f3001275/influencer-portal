from app import app
from flask import render_template, flash, request, redirect, url_for
from helpers import compile_metrics
from forms import BanUserForm, SearchForm, ChangeRedeemStatusForm
from db import session
from models import User, Campaign, RedeemRequest
from helpers import search_campaign, search_username
from flask_login import current_user, login_required
import datetime


def check_privilege():
    if not bool(current_user.is_admin):
        flash('You are not an Admin',category='danger')
        return redirect(url_for('dashboard_page'))


@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard_page():
    if not bool(current_user.is_admin):
        flash('You are not an Admin', category='danger')
        return redirect(url_for('dashboard_page'))
    form = BanUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            entered_user = session.query(User).filter_by(
                username=form.username.data).first()
            entered_user.banned_till = form.date.data
            session.commit()
            flash(f'{entered_user.username} banned till {form.date.data}',
                  category='success')
        return redirect(url_for('admin_dashboard_page'))

    if request.method == 'GET':
        return render_template('/admin/dashboard.html', data=compile_metrics(), ban_user_form=form)


@app.route('/admin/find', methods=['GET', 'POST'])
@login_required
def admin_find_page():
    if not bool(current_user.is_admin):
        flash('You are not an Admin', category='danger')
        return redirect(url_for('dashboard_page'))
    form = SearchForm()
    ban_user_form = BanUserForm()
    if request.method == 'POST':
        if request.form['btn'] == 'ban':
            if ban_user_form.submit and ban_user_form.validate_on_submit():
                entered_user = session.query(User).filter_by(
                    username=ban_user_form.username.data).first()
                entered_user.banned_till = ban_user_form.date.data
                session.commit()
                flash(f'{entered_user.username} banned till {ban_user_form.date.data}',
                      category='success')
                return redirect(request.full_path)

        if request.form['btn'] == 'search':
            if form.submit and form.validate_on_submit():
                if form.choice.data == 'user':
                    return redirect(url_for('admin_find_page', user=form.query.data))
                if form.choice.data == 'campaign':
                    return redirect(url_for('admin_find_page', campaign=form.query.data))
    if request.method == 'GET':

        data = []
        data_type = -1
        if 'user' in request.args:
            data = search_username(request.args['user'])
            form.query.default = request.args['user']
            form.choice.default = 'user'
            form.process()
            data_type = 1
        elif 'campaign' in request.args:
            data = search_campaign(request.args['campaign'],isAdmin=True)
            form.query.default = request.args['campaign']
            form.choice.default = 'campaign'
            form.process()
            data_type = 2

        ALLOWED_ARGS = {'user', 'campaign'}
        unwanted_args = [
            arg for arg in request.args if arg not in ALLOWED_ARGS]
        if unwanted_args:
            data_type = 3

        return render_template('/admin/find.html', data=data, form=form, data_type=data_type, ban_user_form=ban_user_form, dt=datetime)


@app.route('/admin/ban_campaign/<int:campaign_id>', methods=['GET'])
@login_required
def admin_ban_route(campaign_id):
    if not bool(current_user.is_admin):
        flash('You are not an Admin', category='danger')
        return redirect(url_for('dashboard_page'))
    if current_user.is_admin:
        campaign = session.query(Campaign).get(campaign_id)
        if campaign.status == 'closed_by_admin':

            campaign.status = 'pending'
            campaign.sponsor.user.notify(
                f'Your Campaign: {campaign.name} is Unbanned by Admin', category='success')

        else:
            campaign.status = 'closed_by_admin'
            campaign.sponsor.user.notify(
                f'Your Campaign: {campaign.name} is Banned by Admin', category='danger')
        session.commit()
        return redirect(url_for('admin_find_page'))
    else:
        flash('You are not an admin', category='warning')
    return redirect(url_for('dashboard_page'))


@app.route('/admin/redeem', methods=['GET', 'POST'])
@login_required
def admin_redeem_page():
    if not bool(current_user.is_admin):
        flash('You are not an Admin', category='danger')
        return redirect(url_for('dashboard_page'))
    form = ChangeRedeemStatusForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            redeem_request_id = request.form.get('redeem_request_id')
            redeem_request = session.query(
                RedeemRequest).get(redeem_request_id)
            redeem_request.status = form.choice.data
            redeem_request.user.notify(
                notification=f'Redeem Request Processed. Current Status: {redeem_request.status} Remarks: {form.remarks.data}', category='info')
            session.commit()
            flash('Status Changed', category='success')
            return redirect(url_for('admin_redeem_page'))
    if request.method == 'GET':
        redeem_requests = session.query(RedeemRequest).order_by(
            RedeemRequest.status != 'Pending').all()
        return render_template('admin/redeem.html', form=form, redeem_requests=redeem_requests)
