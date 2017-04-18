"""
Views
-------
Contains all the view logic/endpoints for this app.

"""
from yadawia import app, db
from yadawia.classes import DBException, LoginException, User
from yadawia.helpers import login_user, is_safe, redirect_back, authenticate, anonymous_only, public, curr_user
from sqlalchemy import exc
from flask import request, render_template, session, redirect, url_for, abort, flash, jsonify

@app.route('/')
def home():
    """View function for home."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@anonymous_only
def login():
    """View function for Login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            login_user(username, password)
        except LoginException as e:
            error_msg = e.args[0]['message']
            flash(error_msg)
            return redirect_back('login')
        return redirect_back('home')
    return render_template('login.html')

@app.route('/logout')
@authenticate
def logout():
    """Log user out."""
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userId', None)
    return redirect_back('home')

@app.route('/register', methods=['GET', 'POST'])
@anonymous_only
def register():
    """View function for Registeration."""
    if request.method == 'POST':
        username = request.form['username'].lower()
        email = request.form['email'].lower()
        password = request.form['password']
        location = request.form['location']
        name = request.form['name']
        error = None
        try:
            user = User(username, email, password, name, location)
            db.session.add(user)
            db.session.commit()
            login_user(username, password)
        except exc.IntegrityError as ex:
            reason = ex.message
            if reason.endswith('is not unique'):
                error = "%s is already in use." % ex.params[0] 
            else:
                error = reason
            db.session.rollback()
        except (DBException, LoginException) as e:
            error = e.args[0]['message']
        return jsonify(success=True) if error is None else jsonify(error=error)
    return render_template('register.html')

@app.route('/_validateField', methods=['GET'])
@anonymous_only
def validate_field():
    """Check availability of username. For use in registeration form."""
    field_type = request.args.get('type', 0, type=str)
    if field_type not in ['email', 'username']:
        abort(400)
    field = request.args.get('field', 0, type=str)
    kwargs = { field_type: field.lower() }
    existing = User.query.filter_by(**kwargs).first()
    available = 'false' if existing else 'true'
    return jsonify(available=available)

@app.route('/profile')
@app.route('/p/<username>')
def profile(username=None):
    if username is None:
        if 'username' in session:
            username = session['username']
        else:
            abort(404)
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    is_current_users_profile = curr_user(username)
    filtered_user = public(user, ['password', 'email'])
    return render_template('profile.html', user=filtered_user, is_curr_user=is_current_users_profile)