#!/usr/bin/env python3

from yadawia import db
from yadawia.classes import Reason

REASONS = ['User is harrassing me.',
		   'User is displaying products that do not belong to them.',
		   'User is falsely advertising their products.',
		   'User has spammed.',
		   'User has violated my copyrights.',
		   'User is impersonating me/someone I know.',
		   'User is engaging in illegal practices on the website.',
		   'User is displaying inappropriate or mass-produced products.',
		   'Other (Please explain).']

for reason in REASONS:
	r = Reason(reason)
	db.session.add(r)
db.session.commit()