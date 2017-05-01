#!/usr/bin/env python3

from yadawia import db
from yadawia.classes import PaymentMethod

METHODS = [dict(name='Cash on Delivery')]

for one in METHODS:
	method = PaymentMethod(one['name'])
	db.session.add(method)
db.session.commit()