"""
Helpers
-------
Contains helper functions (decorators, others) used by other parts of the app.

"""
from yadawia.classes import User, LoginException
from flask import session, url_for, redirect, request
from urllib.parse import urlparse, urljoin
from functools import wraps
from werkzeug.security import check_password_hash

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
        if check_password_hash(user.password, password) == False:
            raise LoginException({'message': 'Password is incorrect.', 'code': 'password'})
        session['logged_in'] = True
        session['username'] = username.lower()
        session['userId'] = user.id
    else:
        raise LoginException({'message': 'Username does not exist.', 'code': 'username'})


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

def authenticate(f):
    """Decorator function to ensure user is logged in before a page is visited."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_only(f):
    """Decorator function to ensure user is NOT logged in before a page is visited."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session and session['logged_in'] == True:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function