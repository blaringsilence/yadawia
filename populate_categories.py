#!/usr/bin/env python3

from yadawia import db
from yadawia.classes import Category

CATEGORIES = ['Food and Drinks',
			'Clothes - General',
			'Clothes - Women', 
			'Clothes - Men', 
			'Clothes - Children',
			'Clothes - Unisex',
			'Customized Product',
			'Accessories - General',
			'Accessories - Women',
			'Accessories - Men',
			'Accessories - Children',
			'Accessories - Unisex',
			'Accessories - Technology',
			'Accessories - Cars',
			'Shoes - General',
			'Shoes - Women',
			'Shoes - Men',
			'Shoes - Children',
			'Bath and Body',
			'Art - General',
			'Art - Supplies',
			'For Pets',
			'Home and Decoration',
			'Kitchen',
			'Woodwork',
			'Sports',
			'Stationary - Notebooks',
			'Stationary - Writing Tools',
			'Stationary - General',
			'Books and Literature',
			'Technology',
			'Service']

for name in CATEGORIES:
	category = Category(name)
	db.session.add(category)
db.session.commit()
