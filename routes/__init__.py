from app import app, login_manager
from flask import render_template, flash, redirect, url_for
from forms import RegisterForm, LoginForm
from models import User
from db import session
from flask_login import login_user, current_user, logout_user


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/test')
def test_page():
    return render_template('more/test.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
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

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        entered_user = session.query(User).filter_by(
            username=form.username.data).first()
        if entered_user and entered_user.is_password_correct(entered_password=form.password.data):
            login_user(entered_user)
            current_user.current_role='sponsor'
            flash(
                f'Login SuccessFul. You are logged in as {entered_user.username}', category='success')
            session.commit()
            return redirect(url_for('dashboard_page'))
        else:
            flash(f'Username and Password do not Match', category=danger)

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error}', category='danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/influencer/complete_registration')
def complete_reg_inf():
    return render_template('/influencer/complete_registration.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash('Logout Successful', category='info')
    return redirect(url_for('home_page'))
