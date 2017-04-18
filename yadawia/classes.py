from yadawia import app, db
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash
import re


class DBException(Exception):
    pass

class LoginException(Exception):
    pass

class User(db.Model):
    """Database model for users. Contains:

        - id: int, auto-incremented.
        - username: string.
        - name: string. Optional.
        - email: string.
        - password: string.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.String(157), nullable=False) # 128 + salt + algo info
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if len(value) >= 6:
            self._password = generate_password_hash(value, method='pbkdf2:sha512:10000')
        else:
            raise DBException({'message': 'Password cannot be less than 6 characters long.',\
                                'code': 'password'})

    @validates('name')
    def validate_name(self, key, name_input):
        """Validate that the name contains anything but numbers and special characters."""
        pattern = re.compile('^([^0-9\_\+\,\@\!\#\$\%\^\&\*\(\)\;\\\/\|\<\>\"\'\:\?\=\+])+$')
        if not pattern.match(name_input):
            raise DBException({'message': 'Name cannot contain numbers or special characters.',\
                             'code': 'name'})
        return name_input

    @validates('email')
    def validate_email(self, key, em):
        """Validate that the email has an @ and characters before and after it."""
        w3c_pattern = re.compile('^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')
        if not w3c_pattern.match(em):
            raise DBException({'message': 'Email must be valid.', 'code': 'email'})
        return em

    @validates('username')
    def validate_username(self, key, usr):
        """Validates that the username begins with a letter, is at least 2 chars long,
        and can only ever contain letters, numbers, or underscores.
        """
        pattern = re.compile('^[a-zA-Z][\w]+$')
        if not pattern.match(usr):
            raise DBException({'message': 'Username must be 2 characters (number, letter, or underscore) long, and begin with a letter.'})
        return usr