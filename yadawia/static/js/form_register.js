$(function(){
	$('#nextVal', '#register-form').val(window.location.href);

	// FEEDBACK ICONS
	var successful_icon = '<i class="fa fa-check success-check"></i>';
	var error_icon = '<i class="fa fa-times error-check"></i>';
	var loading_icon = '<i class="fa fa-circle-o-notch fa-spin loading-check"></i>';

	// SELECTORS	
	var main_error_place = $('.main-error-msg', '#register-form');
	
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

	function offline_check(field, check, message) {
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

	$('#password', '#register-form').blur(function(){
		offline_check(this, $(this)[0].checkValidity(), 'Password must be at least 6 characters long.');
	});

	$('#password2', '#register-form').blur(function(){
		password1 = $(this).val();
		password2 = $('#password', '#register-form').val();
		offline_check(this, password1 === password2, 'Passwords do not match.');
	});

	$('#name', '#register-form').blur(function(){
		var name = $(this).val();
		var regex = new RegExp('^([^0-9\_\+\,\@\!\#\$\%\^\&\*\(\)\;\\\/\|\<\>\"\'\:\?\=\+])*$');
		offline_check(this, regex.test(name), 'Name can\'t have numbers or special characters.');
	});

	$('#location', '#register-form').blur(function(){
		var loc = $(this).val();
		var regex = new RegExp('^([^\_\+\,\@\!\#\$\%\^\&\*\(\)\;\\\/\|\<\>\"\'\:\?\=\+])*$');
		offline_check(this, regex.test(loc), 'Location can\'t have special characters.');
	});

	// SUBMIT FORM
	$('#register-form').submit(function(e){
		e.preventDefault();
		var form = this;
		var valid = $(form)[0].checkValidity();
		var valid_feedback = true;
			$('.feedback-elem, #password2, #name').each(function(){
			var elem = this;
			$(elem).blur();
			if(!$(elem).data('valid')) {
				valid_feedback = false;
			}
		});

		if (valid && valid_feedback) {
			$.ajax({
				url: Flask.url_for('register'),
				type: 'POST',
				data: $(form).serialize(),
				success: function(data) {
					if(data.error){
						generateMessage('warning', main_error_place, data.error);
					} else {
						window.location.reload();
					}
				}
			});
		}	
	});

});