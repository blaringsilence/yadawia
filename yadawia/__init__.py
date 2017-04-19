"""
App
---
Initialize configuration and put all the parts together.

"""
from flask import Flask
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
