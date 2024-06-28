from app import app, login_manager
from flask import render_template, flash, redirect, url_for,request
from forms import RegisterForm, LoginForm, CompleteRegInf, CompleteRegSponsor,MakeCampaign
from models import User, Sponsor, Influencer,Campaign
from db import session
from flask_login import login_user, current_user, logout_user, login_required
import re
from helpers import generate_completion_codes,checkpoints






@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/test')
def test_page():
    return render_template('more/test.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        flash('User is already Logged in', category='info')
        return redirect(url_for('dashboard_page'))
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            name=form.name.data,
            email_address=form.email_address.data,
            password=form.password.data,
        )
        session.add(new_user)
        session.commit()
        login_user(new_user)
        if form.register_as.data == 'influencer':
            return redirect(url_for('complete_reg_inf'))
        elif form.register_as.data == 'sponsor':
            return redirect(url_for('complete_reg_sponsor'))

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        flash('User is already Logged in',category='info')
        return redirect(url_for('dashboard_page'))
    form = LoginForm()
    if form.validate_on_submit():
        entered_user = session.query(User).filter_by(
            username=form.username.data).first()
        if entered_user and entered_user.is_password_correct(entered_password=form.password.data):
            login_user(entered_user)
            current_user.current_role = form.login_as.data
            flash(
                f'Login SuccessFul. You are logged in as {entered_user.username}', category='success')
            session.commit()
            current_user.current_role = form.login_as.data
            return redirect(url_for('dashboard_page'))
        else:
            flash(f'Username and Password do not Match', category='danger')

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error}', category='danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard_page():

    return render_template('dashboard.html', progress=80)


@app.route('/add/campaign', methods=['GET', 'POST'])
@login_required
def add_campaign_page():
    if current_user.is_sponsor:
        form = MakeCampaign()
        if form.validate_on_submit():
            if current_user.wallet < form.cost.data:
                flash(
                    'Please Recharge! You do not have enough balance to create this campaign.', category='danger')
                return redirect('recharge_wallet_page')
            progress = generate_completion_codes(form.goals.data)
            new_campaign = Campaign(
                sponsor_id=current_user.sponsor.id,
                name=form.name.data,
                description=form.description.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                cost=form.cost.data,
                visibility=(form.visibility.data == 'public'),
                goals=form.goals.data,
                category=form.category.data,
                status='Incomplete',
                secret_code=progress['completion_keys'],
                checkpoint_weights=progress['checkpoint_weight'],
                spare=progress['spare'],

            )
            session.add(new_campaign)
            session.commit()
            current_user.deduct_balance(form.cost.data)
            flash('Campaign Incomplete! Kindly add a Ad request',category='danger')
            return redirect(url_for('view_campaign_page', campaign=new_campaign.id))

        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error}', category='danger')
        return render_template('/add/campaign.html', form=form)
    else:
        flash('OOPS! Become a Sponsor to start creating Campaigns', category='danger')
        return redirect(url_for('dashboard_page'))


@app.route('/view/campaign', methods=['GET', 'POST'])
@login_required
def view_campaign_page():
    if current_user.is_sponsor:
        campaign_id = request.args['campaign']
        if campaign_id:
            campaign = session.query(Campaign).get(campaign_id)
            if campaign:
                if campaign.sponsor_id == current_user.sponsor.id:
                    goals_list = re.split(';', campaign.goals)
                    goals_list = [re.split('=', goal)[0]
                                  for goal in goals_list]
                    checkpoints_list = checkpoints(
                        campaign.goals, campaign.secret_code, campaign.checkpoint_weights, campaign.spare)
                    return render_template('/view/campaign.html', campaign=campaign, goals_list=goals_list,progress =60,checkpoints=checkpoints_list)
                else:
                    flash('Not Your Campaign', category='info')
                    return redirect(url_for('dashboard_page'))
                
            else:
                flash('Campaign Not Found', category='info')
                return redirect(url_for('dashboard_page'))
            
        else:
            flash('Campaign ID Not Found', category='info')
            return redirect(url_for('dashboard_page'))
    else:
        flash('OOPS! Become a Sponsor to start Campaigning', category='danger')
        return redirect(url_for('dashboard_page'))



@app.route('/influencer/complete_registration', methods=['GET', 'POST'])
def complete_reg_inf():
    if current_user.is_influencer:
        return redirect(url_for('dashboard_page'))
    else:
        form = CompleteRegInf()
        if form.validate_on_submit():
            new_influencer = Influencer(
                influencer_id=current_user.id,
                user = current_user,
                category = form.category.data,
                niche=form.niche.data,
                reach=form.reach.data,
            )
            session.add(new_influencer)
            current_user.is_influencer=True
            current_user.currently_logged_in_as = False
            session.commit()
            return redirect(url_for('dashboard_page'))

        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error}', category='danger')

        return render_template('/influencer/complete_registration.html', form= form)


@app.route('/sponsor/complete_registration', methods=['GET', 'POST'])
def complete_reg_sponsor():
    if current_user.is_sponsor:
        return redirect(url_for('dashboard_page'))
    else:
        form = CompleteRegSponsor()
        if form.validate_on_submit():
            new_sponsor = Sponsor(
                sponsor_id=current_user.id,
                user=current_user,
                sponsor_type=form.sponsor_type.data,
                industry=form.industry.data
            )
            session.add(new_sponsor)
            current_user.is_sponsor = True
            current_user.currently_logged_in_as = True
            session.commit()
            return redirect(url_for('dashboard_page'))

        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error}', category='danger')
        return render_template('/sponsor/complete_registration.html', form = form)


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash('Logout Successful', category='info')
    return redirect(url_for('home_page'))
