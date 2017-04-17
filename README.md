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
      $ sudo -u postgres createuser -s $USER
      $ createdb -U $USER yadawia
    ```
5. Update [yadawia/config.py](yadawia/config.py) by replacing the username and password in the database URL with your database username and password.
6. Create the tables.
    ```bash
      $ chmod a+x create_db.py
      $ ./create_db.py
    ```
7. Run the app.
    ```bash
      $ gunicorn yadawia:app
    ```
