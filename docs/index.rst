.. yadawia documentation master file, created by
   sphinx-quickstart on Sat Apr 29 01:10:02 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Yadawia
=======

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. _intro:

Introduction
------------
Built for CCIT's E-Business Fundementals course (IS371), because building an e-commerce system is apparently a rite of passage for every CS student out there. Its idea is simple: customer-to-customer buying and selling of goods and services, if and only if those goods and services in question are handmade.

This documentation focuses on the technical side of things rather than the business side.

Quick summary of what people should be able to do with this platform:

	- Create, edit, and deactivate accounts.
	- Sell handmade products.
	- Buy handmade products.
	- Communicate special requests to sellers.
	- Search for products by their attributes.

The difference between this and a regular e-commerce platform to the user is the flexibility in making and receiving orders regarding schedules, requests, etc.

`Logo Credit`_.

Tools
-----
This project uses:

	- Flask (Python) for the back-end.
	- AWS S3 for image uploads.
	- PostgreSQL for the database.


Installation
------------
1. Clone the github repo.
::
	$ git clone https://github.com/blaringsilence/yadawia.git
	$ cd yadawia

2. Install virtualenv and activate it.
::
	$ pip install virtualenv
	$ virtualenv -p python3 venv
	$ . venv/bin/activate

3. Install requirements.
::
	$ pip install -r requirements.txt

4. Install PostgreSQL (see `download page`_) and create a user and a database.
::
	$ sudo -u postgres createuser -s $USER -P
	$ createdb -U $USER snowdonia

5. Set environment variables (if running locally, add them to your venv/bin/activate script as follows):
::
	export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@localhost/yadawia"
  	export AWS_ACCESS_KEY_ID="YOUR/YOUR IAM USER'S AWS ACCESS KEY"
  	export AWS_SECRET_ACCESS_KEY="YOUR/YOUR IAM USER'S SECRET ACCESS KEY"
  	export S3_BUCKET="YOUR BUCKET NAME HERE"

6. Create the tables, then populate them with the initial values (chmod a+x FILENAME before executing if file does not have execution permissions).
::
	$ ./create_db.py
	$ ./populate_countries.py
	$ ./populate_currencies.py
	$ ./populate_reasons.py
	$ ./populate_categories.py

7. Run the app.
::
	$ gunicorn yadawia:app

.. _docs:

Docs
----
.. automodule:: yadawia
	:members:

.. automodule:: yadawia.views
	:members:

.. automodule:: yadawia.classes
	:members:

.. automodule:: yadawia.helpers
	:members:

.. automodule:: yadawia.errorhandlers
	:members:


.. _Logo Credit: http://www.freepik.com
.. _download page: http://www.postgresql.org/download/