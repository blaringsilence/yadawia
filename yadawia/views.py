"""
Views
-------
Contains all the view logic/endpoints for this app.

"""
from yadawia import app, db, photos
from yadawia.classes import DBException, LoginException, User, Address,\
                             Country, Review, Product, Category, Currency,\
                              Variety, ProductCategory, Upload, MessageThread,\
                              Message, Reason, Report
from yadawia.helpers import login_user, is_safe, redirect_back, \
                            authenticate, anonymous_only, public,\
                            curr_user, get_upload_url, logout_user,\
                            is_allowed_in_thread
from sqlalchemy import exc
from flask import request, render_template, session, redirect, url_for, abort, flash, jsonify, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
from sqlalchemy.sql import func
import uuid

@app.route('/')
def home():
    """View function for home."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@anonymous_only
def login():
    """View function for Login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            login_user(username, password)
        except LoginException as e:
            error_msg = e.args[0]['message']
            flash(error_msg)
            return redirect_back('login')
        return redirect_back('home')
    return render_template('login.html')

@app.route('/logout')
@authenticate
def logout():
    """Log user out."""
    logout_user()
    return redirect_back('home')

@app.route('/register', methods=['GET', 'POST'])
@anonymous_only
def register():
    """View function for Registeration."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        location = request.form['location']
        name = request.form['name']
        error = None
        try:
            user = User(username, email, password, name, location)
            db.session.add(user)
            db.session.commit()
            login_user(username, password)
        except exc.IntegrityError as ex:
            reason = ex.message
            if reason.endswith('is not unique'):
                error = "%s is already in use." % ex.params[0] 
            else:
                error = reason
            db.session.rollback()
        except (DBException, LoginException) as e:
            error = e.args[0]['message']
        return jsonify(success=True) if error is None else jsonify(error=error)
    return render_template('register.html')

@app.route('/_validateField', methods=['GET'])
def validate_field():
    """Check availability of username. For use in registeration form."""
    field_type = request.args.get('type', 0, type=str)
    if field_type not in ['email', 'username']:
        abort(400)
    field = request.args.get('field', 0, type=str)
    kwargs = { field_type: field.lower() }
    existing = User.query.filter_by(**kwargs).first()
    is_taken = existing if not (existing and curr_user(existing.username)) else False
    available = 'false' if is_taken else 'true'
    return jsonify(available=available)

@app.route('/profile')
@app.route('/p/<username>')
def profile(username=None):
    if username is None:
        if 'username' in session:
            username = session['username']
        else:
            abort(404)

    user = User.query.filter_by(username=username.lower(), disabled=False).first()

    if user is None:
        abort(404)
    rating = db.session.query(func.avg(Review.rating).label('average'))\
            .join(Product).join(User).filter(User.id == user.id).first()[0]
    avg_rating = round(rating,2) if rating is not None else None
    report_reasons = Reason.query.order_by(Reason.text).all()

    is_current_users_profile = curr_user(username.lower())

    return render_template('profile.html', user=user,\
                            picture_url=get_upload_url(user.picture),\
                            is_curr_user=is_current_users_profile,\
                            avg_rating=avg_rating,\
                            products=user.products.filter_by(available=True)\
                                    .order_by(Product.create_date.desc()).all(),\
                            report_reasons=report_reasons)

@app.route('/upload/profile-pic', methods=['POST'])
@authenticate
def upload_avatar():
    if 'photo' in request.files:
        rand_name = uuid.uuid4().hex + '.'
        try:
            filename = photos.save(request.files['photo'], name=rand_name)
            user = User.query.filter_by(username=session['username']).first()
            user.picture = filename
            db.session.commit()
        except UploadNotAllowed as e:
            flash('Upload not allowed. Must be an image under 16 megabytes.')
        return redirect(url_for('profile', username=session['username']))
    abort(400)

@app.route('/edit/profile', methods=['POST'])
@authenticate
def edit_profile():
    user = User.query.filter_by(id=session['userId']).first()
    error = None
    try:
        user.name = request.form['name']
        user.username = request.form['username']
        user.about = request.form['about']
        user.location = request.form['location']
        db.session.commit()
        session['username'] = request.form['username'].lower()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except exc.IntegrityError as ex:
        reason = ex.message
        if reason.endswith('is not unique'):
            error = "%s is already in use." % ex.params[0] 
        else:
            error = reason
        db.session.rollback()
    return jsonify(success=True) if error is None else jsonify(error=error)

@app.route('/settings')
@authenticate
def settings():
    user = User.query.filter_by(username=session['username']).first()
    countries = Country.query.order_by(Country.value).all()
    return render_template('settings.html', user=user, addresses=user.addresses.all(), countries=countries)

@app.route('/settings/account', methods=['POST'])
@authenticate
def update_account():
    field_type = request.form['type']
    error = None
    if field_type in ['password', 'email']:
        old_password = request.form['password']
        new_value = request.form['new_' + field_type]
        user = User.query.filter_by(username=session['username']).first()
        if user.isPassword(old_password):
            try:
                setattr(user, field_type, new_value)
                db.session.commit()
            except DBException as dbe:
                error = dbe.args[0]['message'] 
        else:
            error = 'Current password is incorrect.'
        return jsonify(success=True, message='Successfully changed ' + field_type + '.')\
                 if error is None else jsonify(error=error)
    abort(400)

@app.route('/settings/deactivate', methods=['POST'])
@authenticate
def deactivate_account(): # TODO prevent deactivate if ongoing orders.
    password = request.form['password']
    user = User.query.filter_by(username=session['username']).first()
    if user.isPassword(password):
        user.disabled = True
        db.session.commit()
        flash('Your account has been deactivated. Login again to reactivate it!')
        logout_user()
        return redirect(url_for('home'))
    flash('The password you entered was incorrect.')
    return redirect(url_for('settings'))

@app.route('/settings/addresses/add', methods=['POST'])
@authenticate
def add_address():
    error = None
    name = request.form['name']
    text = request.form['text']
    city = request.form['city']
    country_id = request.form['country']
    code = request.form['code']
    phone = request.form['phone']
    user_id = session['userId']
    try:
        address = Address(name, user_id, text, country_id, code, phone)
        db.session.add(address)
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except exc.SQLAlchemyError as e:
        error = e.message
        db.session.rollback()
    return jsonify(success=True) if not error else jsonify(error=error)


@app.route('/settings/addresses/delete', methods=['DELETE'])
@authenticate
def delete_address():
    error = None
    user = User.query.filter_by(username=session['username']).first()
    address_id = int(request.form['address_id'])
    address = Address.query.filter_by(id=address_id).first()
    if address is not None and address.user_id == user.id:
        try:
            db.session.delete(address)
            db.session.commit()
        except exc.IntegrityError as e: # TODO check if ongoing orders or just history
            error = 'Cannot delete an address currently used in ongoing orders.'
        return jsonify(success=True) if not error else jsonify(error=error) 
    abort(400)

@app.route('/product/create', methods=['GET', 'POST'])
@authenticate
def create_product():
    if request.method == 'POST':
        error = None
        name = request.form['pname']
        seller_id = session['userId']
        description = request.form['description']
        currency = request.form['currency']
        price = int(request.form['price']) if request.form['price'] is not None else None
        categories = request.form.getlist('categories')
        variety_titles = request.form.getlist('variety_title')
        variety_prices = request.form.getlist('variety_price')
        pictures = request.files.getlist('photo')
        try:
            product = Product(name, seller_id, description, price, currency)
            db.session.add(product)
            db.session.flush() # to access product ID
            for category_id in categories:
                prodCat = ProductCategory(product.id, category_id)
                db.session.add(prodCat)
            for i in range(1, len(variety_titles)):
                vtitle = variety_titles[i]
                vprice = int(variety_prices[i]) if variety_prices[i] != 'Default' else None
                variety = Variety(vtitle, product.id, vprice)
                db.session.add(variety)
            for pic in pictures:
                rand_name = uuid.uuid4().hex + '.'
                filename = photos.save(pic, name=rand_name)
                upload = Upload(filename, product.id)
                db.session.add(upload)
            db.session.commit()
        except DBException as dbe:
            error = dbe.args[0]['message']
        except (exc.IntegrityError, exc.SQLAlchemyError) as e:
            error = e.message
        if error:
            flash(error)
            return redirect(url_for('create_product'))
        else:
            return redirect(url_for('product', productID=product.id))
    elif request.method == 'GET':
        categories = Category.query.order_by(Category.name).all()
        currencies = Currency.query.order_by(Currency.name).all()
        return render_template('create_product.html', categories=categories, currencies=currencies)

@app.route('/product/<productID>')
def product(productID):
    productID = int(productID)
    product = Product.query.filter_by(id=productID).first()
    if product is None:
        abort(404)
    return render_template('product.html', product=product)

@app.route('/message/create', methods=['POST'])
@authenticate
def new_message():
    error = None
    title = request.form['subject']
    message = request.form['message']
    user1 = session['userId']
    user2 = User.query.filter_by(username=request.form['send_to']).first().id
    if user2 is None:
        abort(400)
    try:
        thread = MessageThread(user1, user2, title)
        db.session.add(thread)
        db.session.flush()
        message = Message(thread.id, user1, message)
        db.session.add(message)
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except (exc.IntegrityError, exc.SQLAlchemyError) as e:
        error = e.message
    if error:
        flash(error)
        return redirect(url_for('profile', username=request.form['send_to']))
    else:
        return redirect(url_for('message_thread', threadID=thread.id))

@app.route('/messages/<threadID>/reply', methods=['POST'])
@authenticate
def reply(threadID):
    if is_allowed_in_thread(threadID):
        error = None
        message = request.form['message']
        sender_id = session['userId']
        try:
            msg = Message(int(threadID), sender_id, message)
            db.session.add(msg)
            db.session.commit()
        except DBException as dbe:
            error = dbe.args[0]['message']
        except (exc.IntegrityError, exc.SQLAlchemyError) as e:
            error = e.message
        if error:
            flash(error)
        redirect(url_for('message_thread', threadID=threadID))
    abort(400)


@app.route('/messages/<threadID>')
@authenticate
def message_thread(threadID): # TODO: PAGE
    if is_allowed_in_thread(threadID): # checks if thread exists and user is allowed in
        thread = MessageThread.query.filter_by(id=int(threadID)).first()
        other_user_id = thread.user2 if thread.user1 == session['userId'] else thread.user1
        other_user = User.query.filter_by(id=other_user_id).first()
        return render_template('message_thread.html',\
                             thread=thread, other_user=other_user)
    abort(400)

@app.route('/report/new', methods=['POST'])
@authenticate
def report_user():
    error = None
    sender_id = session['userId']
    about_username = request.form['reported_user']
    about_user = User.query.filter_by(username=about_username).first()
    if about_user is None:
        abort(400)
    about_id = about_user.id
    reason_id = int(request.form['reason'])
    message = request.form['message']
    try:
        report = Report(sender_id, about_id, reason_id, message)
        db.session.add(report)
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except (exc.IntegrityError, exc.SQLAlchemyError) as e:
        error = e.message
    flash_msg = error if error else 'Thank you for reporting this user. Someone will review this report and take the appropriate action if needed.'
    flash(flash_msg)
    return redirect(url_for('profile', username=about_username))