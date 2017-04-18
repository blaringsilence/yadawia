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

	$('#password', '#register-form').blur(function(){
		var field = this;
		var field_id = '#password';
		var feedback_elem = field_id + '-feedback';
		var error_elem = field_id + '-error-msg';
		if($(field)[0].checkValidity()) {
			$(field).data('valid', true);
			$(feedback_elem).html(successful_icon);
			$(error_elem).html('');
		} else {
			$(field).data('valid', false);
			$(feedback_elem).html(error_icon);
			$(error_elem).html('Password must be at least 6 characters long.');
		}
	});

	$('#password2', '#register-form').blur(function(){
		var field = this;
		var field_id = '#' + $(field).attr('id');
		var feedback_elem = field_id + '-feedback';
		var error_elem = field_id + '-error-msg';
		var password1 = $('#password', '#register-form').val();
		var password2 = $(field).val();
		if(password1 === password2) {
			$(field).data('valid', true);
			$(feedback_elem).html(successful_icon);
			$(error_elem).html('');
		} else {
			$(field).data('valid', false);
			$(feedback_elem).html(error_icon);
			$(error_elem).html('Passwords do not match.');
		}
	});

	// SUBMIT FORM
	$('#register-form').submit(function(e){
		e.preventDefault();
		var form = this;
		var valid = $(form)[0].checkValidity();
		var valid_feedback = true;
			$('.feedback-elem, #password2').each(function(){
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