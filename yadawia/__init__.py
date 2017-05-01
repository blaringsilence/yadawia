"""
App
---
Initialize configuration for the whole app and put all the parts together.

"""
from flask import Flask, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue
from flask_assets import Environment, Bundle
from sqlalchemy_searchable import make_searchable
import re

app = Flask(__name__)
"""Initialize app."""
app.config.from_pyfile('config.py')
"""Get app configuration from the file config.py."""
db = SQLAlchemy(app)
"""Use SQLAlchemy as an ORM."""
jsglue = JSGlue(app)
"""Initialize Flask-JSGlue which allows us to use Flask.url_for in un-rendered JavaScript."""
assets = Environment(app)
"""Initialize assets in app."""
make_searchable()
"""Activates SQLAlchemy-Searchable"""

# import other necessary modules
import yadawia.errorhandlers
import yadawia.views
import yadawia.classes
import yadawia.helpers


js = Bundle(*yadawia.helpers.assetsList(app), filters='slimit', output='js/all.js')
"""Bundle all JavaScript files and minify them."""
css_libs = Bundle(*yadawia.helpers.assetsList(app, folder='css', extension='css',
                                              exclusions=['css/layout.css']), filters='cssmin', output='css/all.css')
"""Bundle library css files and minify them."""
assets.register('js_all', js)
assets.register('css_libs', css_libs)


@app.before_request
def csrf_protect():
    """Check for csrf token in POST and DELETE requests. CSRF tokens are generated per session/login.
    If there's no token or the token is not equal to the one from the form, abort the request.
    """
    if (request.method == 'POST' or request.method == 'DELETE') and app.config['CSRF_ENABLED']:
        token = session['_csrf_token']
        if not token or token != request.form.get('_csrf_token'):
            abort(400)


@app.template_filter('country_name')
def country_name_filter(country_id):
    """TEMPLATE FILTER: Get country name from country ID."""
    return yadawia.classes.Country.query.filter_by(id=country_id).first().value


@app.template_filter('sender')
def sender(thread_id):
    """TEMPLATE FILTER: Get sender in a 2-person message from threadID and logged in session."""
    userId = session['userId']
    return yadawia.classes.MessageThread.query.filter_by(id=thread_id).first().otherUser(userId)


@app.template_filter('name_or_username')
def name_or_username(userId):
    """TEMPLATE FILTER: Get someone's name if set, if not then username."""
    return yadawia.classes.User.query.filter_by(id=userId).first().name_or_username()


@app.template_filter('paragraph')
def paragraph(text):
    """TEMPLATE FILTER: Replace newlines with <br /> in html."""
    return text.replace('\n', '<br />')


app.jinja_env.globals['csrf_token'] = yadawia.helpers.generate_csrf_token
"""Whenever `{{ csrf_token() }}` is used in a Jinja2 template, it returns the result of the function `generate_csrf_token()` """
