from flask import Flask, request, render_template, session, redirect, url_for, abort, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class User(db.Model):
	"""Database model for users. Contains:

		- id: int, auto-incremented.
		- username: string.
		- name: string. Optional.
		- email: string.
		- password: string.
	"""
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True, nullable=False)
	password = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String, unique=True, nullable=False)

class LoginException(Exception):
	pass

def login_user(username, password):
	"""Function to login user through their username.
	Sets:

		- session['logged_in'] to True.
		- session['username'] to the username.
		- session['userId'] to the user ID.

	Raises LoginException (represented as e here) if:

		- User with that username does not exist (e.args[0]['code'] = 'username')
		- Password is incorrect (e.args[0]['code'] = 'password')
	"""
	user = User.query.filter_by(username=username).first()
	if record is not None:
		if check_password_hash(password, user.password) == False:
			raise LoginException({'message': 'Password is incorrect.', 'code': 'password'})
		uid = record.id
		session['logged_in'] = True
		session['username'] = username
		session['userId'] = user.id
	raise LoginException({'message': 'Username does not exist.', 'code': 'username'})

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target:
        target = url_for(endpoint, **values)
    return redirect(target)

def authenticate(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session['logged_in']:
			return redirect(url_for('login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

def anonymous_only(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'logged_in' in session and session['logged_in'] == True:
			abort(401)
		return f(*args, **kwargs)
	return decorated_function

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@anonymous_only
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		try:
			login_user(username, password)
		except LoginException as e:
			error_msg = e.args[0]['message']
			flash(error_msg)
			return jsonify(error=error_msg)
		return redirect_back('home')
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@anonymous_only
def register():
	if request.method == 'POST':
		pass
	return render_template('register.html')