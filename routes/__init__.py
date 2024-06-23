from app import app
from flask import render_template,flash
from forms import RegisterForm,LoginForm
from models import User
from db import session

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
         username= form.username.data,
         name=form.name.data,
         email_address=form.email_address.data,
         password=form.password.data,
      )
      session.add(new_user)
      session.commit()

      flash('Test Flash', category='danger')
   if form.errors != {}:
       for error in form.errors.values():
           flash(f'{error}', category='danger')

   return render_template('register.html', form=form)


@app.route('/login')
def login_page():
   form = LoginForm()
   return render_template('login.html', form=form)


@app.route('/influencer/complete_registration')
def complete_reg_inf():
   return render_template('/influencer/complete_registration.html')
