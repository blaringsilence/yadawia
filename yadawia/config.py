from yadawia import app

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://mariam:tiger@localhost/yadawia'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SECRET_KEY = 'secret key'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
UPLOADED_PHOTOS_DEST = app.static_folder + '/uploads'
UPLOADED_PHOTOS_URL = '/photos/'
CSRF_ENABLED = True