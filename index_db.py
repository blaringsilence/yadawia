#!/usr/bin/env python3

from yadawia import app
from flask_whooshalchemyplus import index_all

with app.app_context():
	index_all(app)