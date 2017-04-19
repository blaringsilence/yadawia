"""
Views
-------
Contains all the view logic/endpoints for this app.

"""
from yadawia import app, db, photos
from yadawia.classes import DBException, LoginException, User
from yadawia.helpers import login_user, is_safe, redirect_back, \
                            authenticate, anonymous_only, public, curr_user, get_upload_url
from sqlalchemy import exc
from flask import request, render_template, session, redirect, url_for, abort, flash, jsonify, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
import uuid

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
def validate_field():
    """Check availability of username. For use in registeration form."""
    field_type = request.args.get('type', 0, type=str)
    if field_type not in ['email', 'username']:
        abort(400)
    field = request.args.get('field', 0, type=str)
    kwargs = { field_type: field.lower() }
    existing = User.query.filter_by(**kwargs).first()
    is_taken = existing if not (existing and curr_user(existing.username)) else False
    available = 'false' if is_taken else 'true'
    return jsonify(available=available)

@app.route('/profile')
@app.route('/p/<username>')
def profile(username=None):
    if username is None:
        if 'username' in session:
            username = session['username']
        else:
            abort(404)
    user = User.query.filter_by(username=username.lower()).first()
    if user is None:
        abort(404)
    is_current_users_profile = curr_user(username.lower())
    filtered_user = public(user, ['password', 'picture'])
    filtered_user['picture_url'] = get_upload_url(user.picture)
    return render_template('profile.html', user=filtered_user, is_curr_user=is_current_users_profile)

@app.route('/upload/profile-pic', methods=['POST'])
@authenticate
def upload_avatar():
    if 'photo' in request.files:
        rand_name = uuid.uuid4().hex + '.'
        try:
            filename = photos.save(request.files['photo'], name=rand_name)
            user = User.query.filter_by(username=session['username']).first()
            user.picture = filename
            db.session.commit()
        except UploadNotAllowed as e:
            flash('Upload not allowed. Must be an image under 16 megabytes.')
        return redirect(url_for('profile', username=session['username']))
    abort(400)

@app.route('/edit/profile', methods=['POST'])
@authenticate
def edit_profile():
    user = User.query.filter_by(id=session['userId']).first()
    error = None
    try:
        user.name = request.form['name']
        user.username = request.form['username'].lower()
        user.about = request.form['about']
        user.location = request.form['location']
        db.session.commit()
        session['username'] = request.form['username'].lower()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except exc.IntegrityError as ex:
        reason = ex.message
        if reason.endswith('is not unique'):
            error = "%s is already in use." % ex.params[0] 
        else:
            error = reason
        db.session.rollback()
    return jsonify(success=True) if error is None else jsonify(error=error)



@app.route('/settings')
@authenticate
def settings():
    abort(404)