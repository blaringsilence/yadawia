#!/usr/bin/env python3

from yadawia import db
from yadawia.classes import Currency

CURRENCIES = [dict(id='EGP', name='Egyptian Pound', symbol=None), dict(id='USD', name='US Dollar', symbol='$')]

for one in CURRENCIES:
	currency = Currency(one['id'], one['name'], one['symbol'])
	db.session.add(currency)
db.session.commit()