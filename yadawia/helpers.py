"""
Helpers
-------
Contains helper functions (decorators, others) used by other parts of the app.

"""
from yadawia import db
from yadawia.classes import User, LoginException, DBException, MessageThread
from flask import session, url_for, redirect, request, flash
from urllib.parse import urlparse, urljoin
from functools import wraps
import re
import string
import random

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
    user = User.query.filter_by(username=username.lower()).first()
    if user is not None:
        if not user.isPassword(password):
            raise LoginException({'message': 'Password is incorrect.', 'code': 'password'})
        if user.suspended:
            raise LoginException({'message': 'Your account has been suspended.', 'code': 'suspend'})
        elif user.disabled:
            enable_user(username)
            flash('Welcome back!')
        session['logged_in'] = True
        session['username'] = username.lower()
        session['userId'] = user.id
        generate_csrf_token(force=True)
    else:
        raise LoginException({'message': 'Username does not exist.', 'code': 'username'})

def suspend_user(username):
    """Suspend a user.""" # TODO cancel orders, refund people etc
    disable_user(username, suspended=True)

def unsuspend_user(username):
    """Unsuspend a user."""
    enable_user(username, was_suspended=True)

def disable_user(username, suspended=False):
    """Disable a user."""
    user = User.query.filter_by(username=username.lower()).first()
    if user is not None:
        user.suspended = suspended
        user.disabled = True
        prods = user.products.filter_by(available=True).all()
        for prod in prods:
            prod.available = False
            prod.force_unavailable = True
        db.session.commit()

def enable_user(username, was_suspended=False):
    """Enable a user."""
    user = User.query.filter_by(username=username.lower()).first()
    if user is not None:
        if was_suspended:
            user.suspended = False
        user.disabled = False
        prods = user.products.filter_by(force_unavailable=True).all()
        for prod in prods:
            prod.available = True
            prod.force_unavailable = False
        db.session.commit()

def get_random_string(length=32):
    """Generate a random string of length 32, used in ``generate_csrf_token()``"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def generate_csrf_token(force=False):
    """Create a CSRF-protection token if one doesn't already exist in the user's session (or force it, as done per login) and put it there."""
    if force or '_csrf_token' not in session:
        session['_csrf_token'] = get_random_string()
    return session['_csrf_token']

def is_allowed_in_thread(threadID):
    thread = MessageThread.query.filter_by(id=threadID).first()
    return thread is not None and thread.isParticipant(session['userId'])

def is_safe(url):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def redirect_back(endpoint, **values):
    """Helper function to redirect to 'next' URL if it exists. Otherwise, redirect to an endpoint."""
    target = request.form['next'] if request.method == 'POST' else request.args.get('next', 0, type=str)
    if not target or not is_safe(target):
        target = url_for(endpoint, **values)
    return redirect(target)

def logout_user():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userId', None)
    generate_csrf_token(force=True)

def no_special_chars(string, allowNumbers=False, optional=True, allowComma=False):
    nums = '0-9' if not allowNumbers else ''
    postfix = '*' if optional else '+'
    comma = '\,' if not allowComma else ''
    pattern = re.compile('^([^' + nums + '\_\+' + comma + '\@\!\#\$\%\^\&\*\(\)\;\\\/\|\<\>\"\'\:\?\=\+])' + postfix + '$')
    return pattern.match(string)

def validate_name_pattern(name_input, allowNumbers=False, optional=True):
    if not no_special_chars(name_input, allowNumbers=allowNumbers, optional=optional):
        raise DBException({'message': 'Name cannot contain numbers or special characters.',\
                         'code': 'name'})

def public(obj, keys):
    """Pass a db class object and a list of keys you don't want returned
    (e.g. password hash, etc) and get a filtered dict.
    """
    d = dict((col, getattr(obj, col)) for col in obj.__table__.columns.keys())
    return {x: d[x] for x in d if x not in keys}

def curr_user(username):
    """True if this username is that of the logged in user, false otherwise."""
    return 'username' in session and session['username'] == username

def get_upload_url(filename):
    """Return url to uploaded file."""
    return url_for('static', filename='uploads/' + filename) if filename else None

def is_logged_in():
    """Is the user logged in?"""
    return 'logged_in' in session and session['logged_in'] == True and 'userId' in session

def user_exists():
    """Given user is logged in, do they exist in db?"""
    return User.query.filter_by(id=session['userId']).first() is not None

def authenticate(f):
    """Decorator function to ensure user is logged in before a page is visited."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or not user_exists():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_only(f):
    """Decorator function to ensure user is NOT logged in before a page is visited."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_logged_in():
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
