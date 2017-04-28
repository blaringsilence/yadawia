"""
App
---
Initialize configuration and put all the parts together.

"""
from flask import Flask, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue
from flask_assets import Environment, Bundle
import re

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
jsglue = JSGlue(app)
assets = Environment(app)

# import other necessary modules
import yadawia.errorhandlers
import yadawia.views
import yadawia.classes
import yadawia.helpers

js = Bundle(*yadawia.helpers.assetsList(app), filters='slimit', output='js/all.js')
css = Bundle(*yadawia.helpers.assetsList(app, folder='css', extension='css'), filters='cssmin', output='css/all.css')
assets.register('js_all', js)
assets.register('css_all', css)

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
    return yadawia.classes.Country.query.filter_by(id=country_id).first().value

@app.template_filter('sender')
def sender(thread_id):
	userId = session['userId']
	return yadawia.classes.MessageThread.query.filter_by(id=thread_id).first().otherUser(userId)

@app.template_filter('name_or_username')
def name_or_username(userId):
	return yadawia.classes.User.query.filter_by(id=userId).first().name_or_username()

@app.template_filter('upload_url')
def upload_url(filename):
    return yadawia.helpers.get_upload_url(filename)

@app.template_filter('paragraph')
def paragraph(text):
    return text.replace('\n', '<br />')



app.jinja_env.globals['csrf_token'] = yadawia.helpers.generate_csrf_token
"""Whenever `{{ csrf_token() }}` is used in a Jinja2 template, it returns the result of the function `generate_csrf_token()` """