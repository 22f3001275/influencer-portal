from app import app, login_manager
from flask import render_template, flash, redirect, url_for
from forms import RegisterForm, LoginForm, CompleteRegInf, CompleteRegSponsor
from models import User, Sponsor, Influencer
from db import session
from flask_login import login_user, current_user, logout_user, login_required


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
            flash(f'Username and Password do not Match', category=danger)

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error}', category='danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard_page():
    
    return render_template('dashboard.html',progress=80)


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
