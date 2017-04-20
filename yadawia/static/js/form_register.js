$(function(){
	$('#nextVal', '#register-form').val(window.location.href);

	// SELECTORS	
	var main_error_place = $('.main-error-msg', '#register-form');

	$('#password', '#register-form').blur(function(){
		offline_check(this, $(this)[0].checkValidity(), 'Password must be at least 6 characters long.');
	});

	$('#password2', '#register-form').blur(function(){
		password2 = $(this);
		password1 = $('#password', '#register-form');
		if(password1[0].checkValidity())
			offline_check(this, password1.val() === password2.val(), 'Passwords do not match.');
	});


	// SUBMIT FORM
	$('#register-form').submit(function(e){
		e.preventDefault();
		var form = this;
		validate_and_send(form, 'register', '#password2');	
	});

});