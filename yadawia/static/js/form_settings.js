$('#new-password', '#password-change-form').blur(function(){
	offline_check(this, $(this)[0].checkValidity(), 'Password cannot be less than 6 characters.');
});

$('#repeat-password', '#password-change-form').blur(function(){
	var password1 = $('#new-password', '#password-change-form');
	var password2 = $(this);
	if (password1[0].checkValidity())
		offline_check(this, password1.val() === password2.val(), 'Passwords do not match.');
});

$('#password-change-form, #email-change-form').submit(function(e){
	e.preventDefault();
	var form = this;
	var is_email_form = $(form).attr('id') == 'email-change-form';
	var preserve;
	if(is_email_form) {
		preserve = $('#new-email',form).val();
	}
	validate_and_send(form, 'update_account', '#repeat-password');
	if (is_email_form && $(form).data('success')) {
		$('#email', form).val(preserve);
	}
});