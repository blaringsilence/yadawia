"""
Classes
-------
Contains all the classes (database, exceptions, etc) created for this app.

"""
from yadawia import app, db
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash
import re


class DBException(Exception):
    """Custom exceptions raised on the ORM level. In its 0th arg,\
    has a human-readable message and a code."""
    pass

class LoginException(Exception):
    """Custom exceptions raised on when logging in. In its 0th arg,\
    has a human-readable message and a code."""
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
    picture = db.Column(db.String)
    location = db.Column(db.String)

    def __init__(self, username, email, password, name='', location=''):
        """Initialize a User using the required fields: username, email, password."""
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.location = location

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Hashes and sets the password if >= 6 chars, otherwise raises a DBException."""
        if len(value) >= 6:
            self._password = generate_password_hash(value, method='pbkdf2:sha512:10000')
        else:
            raise DBException({'message': 'Password cannot be less than 6 characters long.',\
                                'code': 'password'})

    @validates('name')
    def validate_name(self, key, name_input):
        """Validate that the name contains anything but numbers and special characters.
        Raises a DBException if invalid.
        """
        if not no_special_chars(name_input):
            raise DBException({'message': 'Name cannot contain numbers or special characters.',\
                             'code': 'name'})
        return name_input

    @validates('location')
    def validate_location(self, key, loc):
        """Validate that the location contains anything but special characters.
        Raises a DBException if invalid.
        """
        if not no_special_chars(loc, allowNumbers=True):
            raise DBException({'message': 'Name cannot contain numbers or special characters.',\
                             'code': 'location'})
        return loc       

    @validates('email')
    def validate_email(self, key, em):
        """Validate that the email has an @ and characters before and after it.
        Raises a DBException if invalid.
        """
        w3c_pattern = re.compile('^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')
        if not w3c_pattern.match(em):
            raise DBException({'message': 'Email must be valid.', 'code': 'email'})
        return em

    @validates('username')
    def validate_username(self, key, usr):
        """Validates that the username begins with a letter, is at least 2 chars long,
        and can only ever contain letters, numbers, or underscores.
        Raises a DBException if invalid.
        """
        pattern = re.compile('^[a-zA-Z][\w]+$')
        if not pattern.match(usr):
            raise DBException({'message': 'Username must be 2 characters (number, letter, or underscore) long, and begin with a letter.'})
        return usr

from yadawia.helpers import no_special_chars