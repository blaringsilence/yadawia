var generateMessage = function (type, selector, message) {
	$(selector).html("<div class='alert alert-" + type + " alert-dismissable fade in' role='alert'>" 
		+ "<a class='close' data-dismiss='alert' aria-label='close'>&times;</a>"
		+ message
		+ "</div>"
	)
};

var generateHidden = function(name, value, form, class_name) {
	$(form).append('<input type="hidden" class="' + class_name + '" name="' + name + '" value="' + value + '">');
}

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

var validate_and_send = function(form, endpoint, extra_valid_check, refresh_to) {
	var valid = $(form)[0].checkValidity();
	var extra = extra_valid_check ? ', ' + extra_valid_check : '';
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
			url: Flask.url_for(endpoint),
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

$(function(){
	// Log in/out of all tabs if logged in/out in one.
	window.addEventListener('storage', function(event){
		if(event.key === 'logged_in')
	        window.location.reload();
	}, false)

	var logged_in = $('body').data('in');

	window.localStorage.setItem('logged_in', logged_in);

	var is_home = window.location.path === Flask.url_for('home');
	var logout_args = is_home ? {} : { next: window.location.href };
	$('#logout', '.menu').parent().attr('href', Flask.url_for('logout', { next: window.location.href }));

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
