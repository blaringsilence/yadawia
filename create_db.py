#!/usr/bin/env python3
from yadawia import db

db.create_all()

with open('countries.sql', 'r') as country_file:
    script = country_file.read()

countries = db.engine.execute(script)