# Yadawia
[![Documentation Status](https://readthedocs.org/projects/yadawia/badge/?version=latest)](http://yadawia.readthedocs.io/en/latest/?badge=latest)

Web platform for buying and selling handmade products. Built with Flask and PostgreSQL.

## Quick Install

You will need:
  - PostgreSQL ([download page](https://www.postgresql.org/download/))
  - An AWS Account with an S3 Bucket (for more on how to set up permissions, see [this guide on Heroku](https://devcenter.heroku.com/articles/s3-upload-python))

1. Clone this repo.
    ```bash
      $ git clone https://github.com/blaringsilence/yadawia.git
      $ cd yadawia
    ```
2. Install and run virtualenv.
    ```bash
      $ pip install virtualenv
      $ virtualenv -p python3 venv
      $ . venv/bin/activate
    ```
3. Install requirements.
    ```bash
      $ pip install -r requirements.txt
    ```
4. Install PostgreSQL (see [download page](https://www.postgresql.org/download/)), then create a user, and a database.
    ```bash
      $ sudo -u postgres createuser -s $USER -P
      $ createdb -U $USER yadawia
    ```
5. Update your venv activation script venv/bin/activate by making it set the environment variables by adding the following lines:
    ```bash
      export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@localhost/yadawia"
      export AWS_ACCESS_KEY_ID="YOUR/YOUR IAM USER'S AWS ACCESS KEY"
      export AWS_SECRET_ACCESS_KEY="YOUR/YOUR IAM USER'S SECRET ACCESS KEY"
      export S3_BUCKET="YOUR BUCKET NAME HERE"
    ```
6. Create and populate the tables (if files don't have execution permissions `chmod a+x $FILENAME`.
    ```bash
      $ ./create_db.py
      $ ./populate_countries.py
      $ ./populate_currencies.py
      $ ./populate_reasons.py
      $ ./populate_categories.py
      $ ./populate_methods.py
    ```
7. Run the app.
    ```bash
      $ gunicorn yadawia:app
    ```
