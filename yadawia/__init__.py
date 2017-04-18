"""
App
---
Initialize configuration and put all the parts together.

"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
jsglue = JSGlue(app)

# import other necessary modules
import yadawia.errorhandlers
import yadawia.views
import yadawia.classes
import yadawia.helpers
