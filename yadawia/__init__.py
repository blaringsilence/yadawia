"""
App
---
Initialize configuration and put all the parts together.

"""
from flask import Flask, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
jsglue = JSGlue(app)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# import other necessary modules
import yadawia.errorhandlers
import yadawia.views
import yadawia.classes
import yadawia.helpers

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


app.jinja_env.globals['csrf_token'] = yadawia.helpers.generate_csrf_token
"""Whenever `{{ csrf_token() }}` is used in a Jinja2 template, it returns the result of the function `generate_csrf_token()` """