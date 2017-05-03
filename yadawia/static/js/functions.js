var generateMessage = function (type, selector, message, append) {
	var error = "<div class='alert alert-" + type + " alert-dismissable fade in' role='alert'>" 
		+ "<a class='close' data-dismiss='alert' aria-label='close'>&times;</a>"
		+ message
		+ "</div>";
	if(append) $(selector).append(error);
	else $(selector).html(error);
};


var Cart = {
	products: [],
	locked: false,
	add: function(product) {
		if(!this.locked){
			for(var i=0; i<this.products.length; i++){
				if(this.products[i].isEqual(product)) {
					throw 'This item was already added. You can edit it from your cart.';
				}
			}
			this.products.push(product);
			this.triggerChange();
		} else {
			throw 'Cannot add items. Your cart is locked until you continue (or cancel) <a href="' 
			+ Flask.url_for('checkout') 
			+ '">checkout</a>.';
		}
	},
	remove: function(productID, varietyID, noTrigger) {
		if(!this.locked){
			var index = this.find(productID, varietyID);
			if(index !== -1){ this.products.splice(index, 1); }
			else { console.log('Not found'); }
			this.triggerChange(noTrigger);
		} else {
			throw 'Cannot remove items. Your cart is locked until you continue (or cancel) <a href="' 
			+ Flask.url_for('checkout') 
			+ '">checkout</a>.';
		}
	},
	find: function(productID, varietyID) {
		var temp = new Product({id: productID, quantity:0, variety_id: varietyID });
		for(var i=0; i<this.products.length; i++) {
			if(this.products[i].isEqual(temp)) {
				return i;
			}
		}
		return -1;
	},
	clear: function() {
		if(!this.locked){
			this.products = [];
			this.triggerChange();
		} else {
			throw 'Cannot clear cart. Your cart is locked until you continue (or cancel) <a href="' 
			+ Flask.url_for('checkout') 
			+ '">checkout</a>.';
		}
	},
	size: function() {
		return this.products.length;
	},
	isEmpty: function() {
		return this.size() === 0;
	},
	triggerChange: function(noTrigger) {
		window.localStorage.setItem('cart', JSON.stringify(this.products));
		window.localStorage.setItem('cart_lock', JSON.stringify(this.locked));
		var trigger = noTrigger ? false : true;
		if(trigger) $(document).trigger('cartChange');
	},
	update: function() {
		if(window.localStorage.getItem('cart')){
			var arr = JSON.parse(window.localStorage.getItem('cart'));
			var locked = JSON.parse(window.localStorage.getItem('cart_lock'));
			this.locked = locked;
			var products = [];
			for(var i=0; i<arr.length; i++){
				var temp = new Product({
										   id: arr[i].id,
										   quantity: arr[i].quantity,
										   variety_id: arr[i].variety_id, 
										   remarks: arr[i].remarks, 
										   date_added: new Date(arr[i].date_added)
										});
				products.push(temp);
			}
			this.products = products;
		}
	},
	lock: function() {
		this.locked = true;
		this.triggerChange();
	},
	unlock: function() {
		this.locked = false;
		this.triggerChange();
	}
};

function Product(options) {
	var self = this;
	self.id = options.id;
	self.quantity = options.quantity;
	self.remarks = options.remarks ? options.remarks : null;
	self.variety_id = options.variety_id;
	self.date_added = options.date_added ? options.date_added : new Date();
	self.isEqual = function(otherProduct) {
		return otherProduct.id == self.id && otherProduct.variety_id == self.variety_id;
	};
}

var momentDate = function(date) {
	var moment_date = moment.utc(date).local();
	return { formatted:  moment_date.format('MMMM Do YYYY, h:mm:ss a'), fromNow: moment_date.fromNow() };
};

var colorUntil = function(pos){
	for(var i=1; i<=5; i++){
		var elem = $('#star-' + i);
		if(i <= pos){
			$(elem).removeClass('fa-star-o').addClass('fa-star');
		} else {
			$(elem).removeClass('fa-star').addClass('fa-star-o');
		}
	}
};

var uploadPicsToS3 = function(files, url_elem, valid_elem) {
	getSignedRequest(files, function(data){
		if(!data.error) {
			for(var i=0; i<data.data.length; i++){
				var postData = new FormData();
				for(key in data.data[i].fields){
				  postData.append(key, data.data[i].fields[key]);
				}
				postData.append('file', files[i]);
				$.ajax({
					url: data.data[i].url,
					data: postData,
					method: 'POST',
					processData: false,
					contentType: false,
					indexValue: i,
					success: function(d) {
						$(url_elem).append('<input type="hidden" name="photo_url" value="' 
										+ data.urls[this.indexValue] + '">');
						if($(url_elem).children().length === Number($(url_elem).data('number'))) {
							$(valid_elem).val('true').trigger('change');
						}
					}
				});
			}
		}
	});
};

var getSignedRequest = function(files, callback) {
	var data = getFileData(files);
	$.getJSON(Flask.url_for('sign_s3'), {
		photo_name: data.photo_name,
		photo_type: data.photo_type,
		photo_size_mb: data.photo_size_mb
	}, function (d) {
		callback(d);
	});
};

var getFileData = function(files) {
	var photo_name = [];
	var photo_type = [];
	var photo_size_mb = [];
	for(var i=0; i<files.length; i++){
		photo_name.push(files[i].name);
		photo_type.push(files[i].type);
		photo_size_mb.push(files[i].size * 0.000001);
	}
	return { photo_name: photo_name, photo_type: photo_type, photo_size_mb: photo_size_mb };
};

var generateHidden = function(name, value, form, class_name) {
	$(form).append('<input type="hidden" class="' + class_name + '" name="' + name + '" value="' + value + '">');
};

// FEEDBACK ICONS
var successful_icon = '<i class="fa fa-check success-check"></i>';
var error_icon = '<i class="fa fa-times error-check"></i>';
var loading_icon = '<i class="fa fa-circle-o-notch fa-spin loading-check"></i>';

var name_regexp = function (allowNums, allowCommas) {
	var nums = allowNums ? '' : '0-9';
	var commas = allowCommas ? '' : '\,';
	return new RegExp('^([^' + nums + '\_\+' + commas + '\@\!\#\$\%\^\&\*\(\)\;\\\/\|\<\>\"\'\:\?\=\+])*$');
}

var getURLParameter = function (name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
}

var offline_check = function (field, check, message) {
	var field_id = '#' + $(field).attr('id');
	var feedback_elem = field_id + '-feedback';
	var error_elem = field_id + '-error-msg';
	if(check) {
		$(field).data('valid', true);
		$(feedback_elem).html(successful_icon);
		$(error_elem).html('');
	} else {
		$(field).data('valid', false);
		$(feedback_elem).html(error_icon);
		$(error_elem).html(message);
	}
}

var hide_feedback_elem = function(field) {
	var field_id = '#' + $(field).attr('id');
	var feedback_elem = field_id + '-feedback';
	var error_elem = field_id + '-error-msg';
	$(error_elem).html('');
	$(feedback_elem).html('');
}

var validate_and_send = function(form, endpoint, extra_field_check, refresh_to, url_params) {
	var valid = $(form)[0].checkValidity();
	var url_params = url_params ? url_params : {};
	var extra = extra_field_check ? ', ' + extra_field_check : '';
	var valid_feedback = true;
		$('.feedback-elem, input[name="name"], input[name="location"]' + extra, form).each(function(){
		var elem = this;
		$(elem).blur();
		if(!$(elem).data('valid')) {
			valid_feedback = false;
		}
	});
	var main_error_place = $('.main-error-msg', form);	
	if (valid && valid_feedback) {
		$.ajax({
			url: Flask.url_for(endpoint, url_params),
			type: 'POST',
			data: $(form).serialize(),
			success: function(data) {
				if(data.error){
					generateMessage('warning', main_error_place, data.error);
				} else if (data.message){ 
					generateMessage('success', main_error_place, data.message);
					$(form)[0].reset();
					$('.form-control-feedback', form).html('');
					$('.error-msg', form).html('');
				} else if(refresh_to) {
					window.location.href = refresh_to;
				} else {
					window.location.reload();
				}
			}
		});
	}
}

var cart_num = function(num) { return '<span class="cart-number">' + num + '</span>'; }
var updateCartIcon = function() {
	if(cart_num(Cart.size()) !== $('.cart-icon-wrapper').first().html()) {
		$('.cart-icon-wrapper').each(function(){ $(this).html(''); });
		if(!Cart.isEmpty()) {
			$('.cart-icon-wrapper').each(function() { $(this).html(cart_num(Cart.size())); });
		}
	}
}

var getCartProductInfo = function(callback) {
	var data = formatCartData(Cart.products);
	$.getJSON(Flask.url_for('cart_products'), {
		product_id: data.pid,
		product_variety: data.pvar,
		product_quantity: data.pq
	}, function (d) {
		callback(d);
	});
}


$(function(){
	Cart.update();
	updateCartIcon();
	// Log in/out of all tabs if logged in/out in one.
	window.addEventListener('storage', function(event){
		if(event.key === 'logged_in'){
	        window.location.reload();
	        Cart.locked = false;
	        Cart.clear();
		}
	    else if(event.key === 'cart' || event.key === 'cart_lock'){
	    	Cart.update();
	    	updateCartIcon();
	    }
	}, false)
	$(document).on('cartChange', updateCartIcon);

	var logged_in = $('body').data('in');

	window.localStorage.setItem('logged_in', logged_in);
	if (window.localStorage.getItem('logged_in') === 'false') {
		Cart.locked = false;
		Cart.clear();
	}

	$('#logout', '.menu').parent().attr('href', Flask.url_for('logout', { next: window.location.href }));

	$('.date-to-now').each(function(){
		var md = momentDate($(this).text());
		$(this).attr('title', md.formatted);
		$(this).text(md.fromNow);
	});

	// CHECK AVAILABILITY (FOR EMAIL AND USERNAME FIELDS)
	$('.feedback-elem').bind('blur', function(){
		var field = this;
		var field_id = '#' + $(field).attr('id');
		var feedback_elem = field_id + '-feedback';
		var endpoint = $(field).data('endpoint');
		var type = $(field).data('type');
		var error_elem = field_id + '-error-msg';
		$(error_elem).html('');
		$(feedback_elem).html(loading_icon);
		if ($(this)[0].checkValidity()){
			$.getJSON(Flask.url_for(endpoint), {
			 field: $(field).val(),
			 type: type
			}, function(data) {
				var thing = type.charAt(0).toUpperCase() + type.substr(1);
				if(data.available == 'false') {
					$(feedback_elem).html(error_icon);
					$(error_elem).html('Already in use.');
					$(field).data('valid', false);
				} else {
					$(feedback_elem).html(successful_icon);
					$(error_elem).html('');
					$(field).data('valid', true);
				}
			});
		} else {
			$(feedback_elem).html(error_icon);
			$(error_elem).html('Invalid value.');
			$(field).data('valid', false);
		}
	});

	$('input[name="name"]').blur(function(){
		var name = $(this).val();
		var has_nums = $(this).data('nums');
		var regex = name_regexp(has_nums);
		var ext = has_nums ? '' : 'numbers or '
		offline_check(this, regex.test(name), 'Name can\'t have ' + ext + 'special characters.');
		if(name === '') { hide_feedback_elem(this); }
	});

	$('input[name="location"]').blur(function(){
		var loc = $(this).val();
		var regex = name_regexp(true, true);
		offline_check(this, regex.test(loc), 'Location can\'t have special characters.');
		if(loc === '') { hide_feedback_elem(this); }
	});

	// for layout page/footer
	$(function () { $('#year', '.footer').text(new Date().getFullYear()); });
});
