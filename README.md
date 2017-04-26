# Yadawia
Web platform for buying and selling handmade products. Built with Flask and PostgreSQL.

## Quick Install

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
5. Update your venv activation script venv/bin/activate by making it set the DATABASE_URL environment variable to your database string by adding the following line:
    ```bash
      export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@localhost/yadawia"
    ```
6. Create the tables.
    ```bash
      $ chmod a+x create_db.py
      $ ./create_db.py
    ```
7. Run the app.
    ```bash
      $ gunicorn yadawia:app
    ```
