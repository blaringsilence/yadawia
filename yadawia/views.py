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
                            is_allowed_in_thread, disable_user,\
                            create_edit_product, valid_photo,\
                            get_presigned_post
from sqlalchemy import exc, or_, and_
from flask import request, render_template, session, redirect, url_for, abort, flash, jsonify, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
from sqlalchemy.sql import func
import uuid
import os

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
    kwargs = {} if is_current_users_profile else { 'available': True }

    return render_template('profile.html', user=user,\
                            is_curr_user=is_current_users_profile,\
                            avg_rating=avg_rating,\
                            products=user.products.filter_by(**kwargs)\
                                    .order_by(Product.update_date.desc()).all(),\
                            report_reasons=report_reasons)

@app.route('/upload/profile-pic', methods=['POST'])
@authenticate
def upload_avatar():
    photo_url = request.form['photo_url']
    user = User.query.filter_by(username=session['username']).first()
    user.picture = photo_url
    db.session.commit()
    return redirect(url_for('profile', username=session['username']))

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
        disable_user(user.username)
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
        return create_edit_product(create=True)
    elif request.method == 'GET':
        categories = Category.query.order_by(Category.name).all()
        currencies = Currency.query.order_by(Currency.name).all()
        return render_template('create_product.html', categories=categories, currencies=currencies)

@app.route('/product/<int:productID>')
def product(productID):
    productID = productID
    product = Product.query.filter_by(id=productID).outerjoin(Review).order_by(Review.create_date.desc()).first()
    if product is None or\
    (not product.available and ('logged_in' not in session or product.seller_id != session['userId'])):
        abort(404)
    categories = Category.query.all()
    currencies = Currency.query.all()
    return render_template('product.html', product=product, categories=categories, currencies=currencies)

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

@app.route('/messages')
@authenticate
def messages():
    user_id = session['userId']
    threads = MessageThread.query.join(Message)\
            .filter(or_(MessageThread.user1 == user_id, MessageThread.user2 == user_id))\
            .order_by(Message.date.desc()).all()
    return render_template('messages.html', threads=threads)

@app.route('/see-message/<int:threadID>', methods=['POST'])
@authenticate
def see_message(threadID):
    if is_allowed_in_thread(threadID):
        error = None
        user_id = session['userId']
        messages = Message.query.filter(Message.sender_id != user_id).all()
        try:
            for message in messages:
                message.see(user_id)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            error = e.message
        return jsonify(success=True) if not error else jsonify(error=error)
    abort(400)

@app.route('/messages/<int:threadID>/reply', methods=['POST'])
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


@app.route('/messages/<int:threadID>')
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

@app.route('/product/<int:productID>/review/new', methods=['POST'])
@authenticate
def new_review(productID):
    error = None
    text = request.form['text']
    rating = float(request.form['rating'])
    user_id = session['userId']
    title = request.form['title']
    try:
        review = Review(user_id, productID, rating, title=title, text=text)
        db.session.add(review)
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except (exc.IntegrityError, exc.SQLAlchemyError) as e:
        error = e.message
    return jsonify(success=True) if error is None else jsonify(error=error)

@app.route('/product/<int:productID>/review/edit', methods=['POST'])
@authenticate
def edit_review(productID):
    error = None
    text = request.form['text']
    rating = float(request.form['rating'])
    user_id = session['userId']
    title = request.form['title']
    try:
        review = Review.query.filter_by(product_id=productID, user_id=user_id).first()
        if review is None:
            abort(400)
        review.text = text
        review.rating = rating
        review.title = title
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except (exc.IntegrityError, exc.SQLAlchemyError) as e:
        error = e.message
    return jsonify(success=True) if error is None else jsonify(error=error)

@app.route('/product/<int:productID>/review/delete', methods=['POST'])
@authenticate
def delete_review(productID):
    error = None
    user_id = session['userId']
    try:
        review = Review.query.filter_by(product_id=productID, user_id=user_id).first()
        if review is None:
            abort(400)
        db.session.delete(review)
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except (exc.IntegrityError, exc.SQLAlchemyError) as e:
        error = e.message
    flash_msg = error if error is not None else 'Successfully deleted your review.'
    return redirect(url_for('product', productID=productID))

@app.route('/product/<int:productID>/toggle', methods=['POST'])
@authenticate
def toggle_availability(productID):
    error = None
    user_id = session['userId']
    try:
        product = Product.query.filter_by(id=productID, seller_id=user_id).first()
        if product is None:
            abort(400)
        product.available = not product.available
        db.session.commit()
    except DBException as dbe:
        error = dbe.args[0]['message']
    except (exc.IntegrityError, exc.SQLAlchemyError) as e:
        error = e.message
    return jsonify(success=True) if error is None else jsonify(error=error)

@app.route('/product/<int:productID>/edit-pics', methods=['POST'])
@authenticate
def edit_product_pics(productID):
    product = Product.query.filter_by(id=productID, seller_id=session['userId']).first()
    pic_ids = request.form.getlist('pic_id')
    pic_orders = request.form.getlist('pic_order')
    for i in range(len(pic_ids)):
        temp_pic = product.uploads.filter_by(id=pic_ids[i]).first()
        if temp_pic is not None:
            order = pic_orders[i]
            if order == 'remove':
                db.session.delete(temp_pic)
            else:
                temp_pic.order = pic_orders[i]
    db.session.commit()
    if product is None:
        abort(400)
    return redirect(url_for('product', productID=productID))

@app.route('/product/<int:productID>/edit', methods=['POST'])
@authenticate
def edit_product(productID):
    product = Product.query.filter_by(id=productID, seller_id=session['userId']).first() 
    if product is not None:
        return create_edit_product(create=False, productID=productID)
    else:
        abort(400)

@app.route('/sign_s3', methods=['GET'])
@authenticate
def sign_s3():
    S3_BUCKET = os.environ.get('S3_BUCKET')
    user_id = session['userId']
    photo_name = request.args.getlist('photo_name[]')
    photo_type = request.args.getlist('photo_type[]')
    photo_size_mb = request.args.getlist('photo_size_mb[]')
    posts = []
    urls = []
    for i in range(len(photo_type)):
        if not valid_photo(photo_type[i], float(photo_size_mb[i])):
            return jsonify(error= photo_name[i] + ' is not a valid photo under 10 MBs.')
        else:
            new_name = uuid.uuid4().hex + '_' + str(user_id) + os.path.splitext(photo_name[i])[1]
            posts.append(get_presigned_post(new_name, photo_type[i]))
            urls.append('https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, new_name))
    return jsonify(data=posts, urls=urls)
