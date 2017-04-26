"""
Classes
-------
Contains all the classes (database, exceptions, etc) created for this app.

"""
# -*- coding: utf-8 -*-
from yadawia import app, db
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import re
import datetime

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
    password = db.Column(db.String(157), nullable=False) # 128 + salt + algo info
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    picture = db.Column(db.String)
    location = db.Column(db.String)
    about = db.Column(db.String(200))
    disabled = db.Column(db.Boolean, unique=False, default=False)
    suspended = db.Column(db.Boolean, unique=False, default=False)
    addresses = db.relationship('Address', backref='user', lazy='dynamic',\
                cascade='save-update, merge, delete')
    products = db.relationship('Product', backref='seller', lazy='dynamic',\
                cascade='save-update, merge, delete')
    reviews = db.relationship('Review', backref='user', lazy='dynamic',\
                cascade='save-update, merge, delete')
    orders = db.relationship('Order', backref='user', lazy='dynamic',\
                cascade='save-update, merge, delete')

    def __init__(self, username, email, password, name=None, location=None):
        """Initialize a User using the required fields: username, email, password."""
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.location = location

    def isPassword(self, pw):
        return check_password_hash(self.password, pw)

    def name_or_username(self):
        if self.name:
            return self.name
        return self.username

    def bought(self, productID):
        return self.orders.join(OrderProduct).join(Product).filter(Product.id == productID).count() > 0

    @validates('password')
    def validate_password(self, key, pw):
        if len(pw) < 6:
            raise DBException({'message': 'Password cannot be less than 6 characters long.',\
                                'code': 'password'})
        return generate_password_hash(pw, method='pbkdf2:sha512:10000')

    @validates('name')
    def validate_name(self, key, name_input):
        """Validate that the name contains anything but numbers and special characters.
        Raises a DBException if invalid.
        """
        validate_name_pattern(name_input)
        return name_input

    @validates('location')
    def validate_location(self, key, loc):
        """Validate that the location contains anything but special characters.
        Raises a DBException if invalid.
        """
        if not no_special_chars(loc, allowNumbers=True, allowComma=True):
            raise DBException({'message': 'Location cannot contain special characters.',\
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
        return em.lower()

    @validates('username')
    def validate_username(self, key, usr):
        """Validates that the username begins with a letter, is at least 2 chars long,
        and can only ever contain letters, numbers, or underscores.
        Raises a DBException if invalid.
        """
        pattern = re.compile('^[a-zA-Z][\w]+$')
        if not pattern.match(usr):
            raise DBException({'message': 'Username must be 2 characters (number, letter, or underscore) long, and begin with a letter.'})
        return usr.lower()

class Address(db.Model):
    """Database model for addresses (physical). Contains:

        - id: int, auto-incremented.
        - name: name to assign to this address (every user can have multiple addresses).
        - user_id: int, foreign key.
        - country_id: string, ISO 3166-1 code, foreign key.
        - city: string.
        - zip/postal code: string.
        - phone: string.
        - text: string.
    """
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default='Default')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    country_id = db.Column(db.String(2), db.ForeignKey('countries.id'))
    code = db.Column(db.String)
    _phone = db.Column(db.String)
    text = db.Column(db.String, nullable=False)
    orders = db.relationship('Order', backref='address', lazy='dynamic')

    def __init__(self, name, user_id, text, country_id, code=None, phone=None):
        self.name = name
        self.user_id = user_id
        self.country_id = country_id
        self.code = code
        self.phone = phone
        self.text = text

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        pattern = re.compile('[^\d\+x]') # all but digits, +, and x (for extensions)
        stripped = re.sub(pattern, '', value)
        self._phone = stripped

    @validates('name')
    def validate_name(self, key, name_input):
        """Makes sure the name doesn't have any numbers or special chars.
        Raises a DBException otherwise.
        """
        validate_name_pattern(name_input, allowNumbers=True)
        return name_input

class Product(db.Model):
    """Database model for products. Contains:
        
        - id: int, auto-incremented.
        - name: string.
        - seller_id: int, foreign key.
        - update_date: date.
        - create_date: date.
        - description: string.
        - price: float.
        - available: boolean, default: True.
    """

    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    description = db.Column(db.String)
    currency_id = db.Column(db.String(3), db.ForeignKey('currencies.id'))
    price = db.Column(db.Float)
    categories = db.relationship('Category', secondary='product_category',\
                                back_populates='products', lazy='dynamic')
    varieties = db.relationship('Variety', backref='product', lazy='dynamic',\
                                cascade='save-update, merge, delete')
    uploads = db.relationship('Upload', backref='product', lazy='dynamic',\
                                cascade='save-update, merge, delete')
    reviews = db.relationship('Review', backref='product', lazy='dynamic',\
                                cascade='save-update, merge, delete')
    orders = db.relationship('Order', secondary='order_product',\
                                back_populates='products', lazy='dynamic')
    available = db.Column(db.Boolean, default=True, nullable=False)
    force_unavailable = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, name, seller_id, description=None, price=None, currency_id=None):
        self.name = name
        self.seller_id = seller_id
        self.description = description
        self.price = price
        self.currency_id = currency_id

    def first_picture(self):
        return get_upload_url(self.uploads.order_by(Upload.order).first().filename)

    
    def avg_rating(self):
        return db.session.query(func.avg(Review.rating).label('average')).\
                join(Product).filter(Product.id == self.id).first()[0]

    @validates('price')
    def validate_price(self, key, p):
        """Makes sure the price is not less than 0."""
        if p is not None and p < 0:
            raise DBException({'message': 'Default price cannot be less than zero.', 'code': 'price'})
        return p


class Category(db.Model):
    """Database model for categories. Contains:
    
        - id: int, auto-incremented.
        - name: string.
    """
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    products = db.relationship('Product', secondary='product_category',\
                                back_populates='categories', lazy='dynamic')


    def __init__(self, name):
        self.name = name

    @validates('name')
    def validate_name(self, key, name_input):
        """Makes sure the name doesn't have any numbers or special chars.
        Raises a DBException otherwise.
        """
        validate_name_pattern(name_input, optional=False)
        return name_input

class ProductCategory(db.Model):
    """Database model for the relationship between products and categories (many-to-many). Contains:
        
        - product_id: int, foreign key.
        - category_id: int, foreign key.
    """
    __tablename__ = 'product_category'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)

    def __init__(self, product_id, category_id):
        self.product_id = product_id
        self.category_id = category_id

class Variety(db.Model):
    """Database model for varieties in products (sizes, etc). Contains:
        
        - id: int, auto-incremented.
        - product_id: int, foreign key.
        - name: string. What is this variety? (e.g. Size small) No validation.
        - price: float.
        - available: boolean, default: True.
    """
    __tablename__ = 'varieties'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=True)
    available = db.Column(db.Boolean, default=True)
    uploads = db.relationship('Upload', backref='variety', lazy='dynamic')
    orders = db.relationship('OrderProduct', backref='variety', lazy='dynamic')

    def __init__(self, name, product_id, price=None, available=True):
        self.name = name
        self.product_id = product_id
        self.price = price
        self.available = available

    @validates('price')
    def validate_price(self, key, pr):
        if pr is not None and pr < 0:
            raise DBException({'message': 'Variety price cannot be less than zero.', 'code': 'price'})
        return pr

class Upload(db.Model):
    """Database model for product-related uploads (photo, video). Contains:

        - id: int, auto-increment.
        - filename: string.
        - date: upload date.
        - product_id: int, foreign key.
        - variety_id: int, foreign key. Optional.
        - order: int, default: 0
    """
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    filename = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    variety_id = db.Column(db.Integer, db.ForeignKey('varieties.id'))
    order = db.Column(db.Integer, default=0)

    def __init__(self, filename, product_id, variety_id=None, order=0):
        self.filename = filename
        self.product_id = product_id
        self.variety_id = variety_id
        self.order = order

    def url(self):
        return get_upload_url(self.filename)

class Review(db.Model):
    """Database model for reviews on products. Contains:
        
        - id: int, auto-increment.
        - user_id: int, foreign key.
        - product_id: int, foreign key.
        - rating: float.
        - title: string.
        - text: string.
        - create_date: review date.
        - update_date: update date.
    """
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    rating = db.Column(db.Float, nullable=False)
    title = db.Column(db.String)
    text = db.Column(db.String)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, user_id, product_id, rating, title=None, text=None):
        self.user_id = user_id
        self.product_id = product_id
        self.rating = rating
        self.title = title
        self.text = text

    @validates('rating')
    def validate_rating(self, key, r):
        """Makes sure the rating is between 1 and 5 with 0.5 increments only."""
        half_or_full = r % 1 == 0 or r % 1 == 0.5
        if r < 1 or r > 5 or not half_or_full:
            raise DBException({'message': 'Rating must be between 1 and 5, with 0.5 increments only.',\
                            'code': 'rating'})
        return r

class Order(db.Model):
    """Database model for orders. Contains:
        
        - id: int, auto-increment.
        - user_id: int, foreign key.
        - create_date: date.
        - update_date: date.
        - status: string.
        - address_id: int, foreign key.
    """
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = db.Column(db.String, default='New')
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    products = db.relationship('Product', secondary='order_product',\
                                back_populates='orders', lazy='dynamic')
    message_threads = db.relationship('MessageThread', backref='order', lazy='dynamic')

    def __init__(self, user_id):
        self.user_id = user_id

class OrderProduct(db.Model):
    """Database model for relationship between orders and models (many-to-many). Contains:
        
        - id: int, auto-incremented.
        - order_id: int, foreign key.
        - product_id: int, foreign key.
        - variety_id: int, foreign key.
        - quantity: int.
        - create_date: date.
        - update_date: date.
    """
    __tablename__ = 'order_product'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    variety_id = db.Column(db.Integer, db.ForeignKey('varieties.id'))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, order_id, product_id, variety_id, quantity=0):
        self.order_id = order_id
        self.product_id = product_id
        self.variety_id = variety_id
        self.quantity = quantity

    @validates('quantity')
    def validate_quantity(self, key, q):
        """Validate that quantity is more than 0."""
        if q < 0:
            raise DBException({'message': 'Quantity cannot be less than zero.', 'code': 'quantity'})
        return q

class MessageThread(db.Model):
    """Database model for message threads. Contains:
        
        - id: int, auto-incremented.
        - user1: int, foreign key.
        - user2: int, foreign key.
        - title: string. Optional.
        - order_id: int, foreign key (if about an order).
    """
    __tablename__ = 'message_threads'
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2 = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String, nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    messages = db.relationship('Message', backref='thread', lazy='dynamic')

    def __init__(self, user1, user2, title=None):
        self.user1 = user1
        self.user2 = user2
        self.title = title

    def isParticipant(self, user):
        return self.user1 == user or self.user2 == user

    def otherUser(self, user):
        if self.isParticipant(user):
            return self.user2 if self.user1 == user else self.user1
        return None

class Message(db.Model):
    """Database model for messages in a thread. Contains:
        
        - id: int, auto-incremented.
        - thread_id: int, foreign key.
        - sender_id: int, foreign key. No need for receiver because thread has info.
        - date: date.
        - text: string.
        - seen: date.
    """
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('message_threads.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    seen = db.Column(db.DateTime)

    def __init__(self, thread_id, sender_id, text):
        self.thread_id = thread_id
        self.sender_id = sender_id
        self.text = text

    def see(self, userId):
        thread = self.thread.first()
        if userId != self.sender_id and (thread.user1 == userId or thread.user2 == userId):
            self.seen = datetime.datetime.utcnow()
        



class Country(db.Model):
    """Database model for all countries. Contains:
        - id: string, ISO 3166-1 code.
        - value: string, name.
    """
    __tablename__ = 'countries'
    id = db.Column(db.String(2), primary_key=True)
    value = db.Column(db.String, unique=True)
    addresses = db.relationship('Address', backref='country', lazy='dynamic')

    def __init__(self, country_id, value):
        self.id = country_id
        self.value = value

class Currency(db.Model):
    """Database model for all supported currencies. Contains:

        - id: string, ISO-4217 code.
        - name: string.
        - symbol: string.
    """
    __tablename__ = 'currencies'
    id = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String, unique=True)
    symbol = db.Column(db.String, nullable=True)
    products = db.relationship('Product', backref='currency', lazy='dynamic')

    def __init__(self, curr_id, name, symbol=None):
        self.name = name
        self.id = curr_id
        self.symbol = symbol

class Reason(db.Model):
    """Database model for report reasons. Contains:
        
        - id: int, auto-incremented.
        - text: string.
    """
    __tablename__ = 'reasons'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, unique=True)
    reports = db.relationship('Report', backref='reason', lazy='dynamic')

    def __init__(self, text):
        self.text = text

class Report(db.Model):
    """Database model for reports to admins. Contains:

        - id: int, auto-incremented.
        - sender_id: int, foreign key.
        - about_id: int, foreign key.
        - reason: int, foreign key.
        - date: date.
    """
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    about_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reason_id = db.Column(db.Integer, db.ForeignKey('reasons.id'))
    message = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)

    def __init__(self, sender_id, about_id, reason_id, message):
        self.sender_id = sender_id
        self.about_id = about_id
        self.reason_id = reason_id
        self.message = message

    def getSender(self):
        return User.query.filter_by(id=self.sender_id).first()

    def getAbout(self):
        return User.query.filter_by(id=self.about_id).first()


class Admins(db.Model):
    """Database model for admins. Contains:
        
        - id: int, auto-incremented.
        - user_id: int, foreign key.
        - date: date.
    """
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

    def __init__(self, user_id):
        self.user_id = user_id


from yadawia.helpers import validate_name_pattern, no_special_chars, get_upload_url