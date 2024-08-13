
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from flask_migrate import Migrate
import logging


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/main.db'
app.config['SECRET_KEY'] = '1ab8d586c99c02b70dc1c1de'
app.config['razorpay_key_id'] = 'rzp_test_wz4kj09Gic9m7E'
app.config['razorpay_key_secret'] = 'Yy6owjvMFwsJIDwRA47DBaAj'
app.config['deployement_url'] = 'http://127.0.0.1:5000'
app.config['UPLOAD_FOLDER']='/profile'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view='login_page'
login_manager.login_message_category='info'


app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('log/app.log')
app.logger.addHandler(handler)



import routes