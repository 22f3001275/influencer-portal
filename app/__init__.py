
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = '1ab8d586c99c02b70dc1c1de'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


import routes