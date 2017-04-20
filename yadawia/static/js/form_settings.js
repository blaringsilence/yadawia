$(function(){
	var selected_sec = getURLParameter('sel');
	if(selected_sec) {
		selected_sec = selected_sec.toLowerCase();
		var sec_id = selected_sec + '-settings';
		var button = $('button[data-section="' + sec_id + '"]');
		$('.settings-nav-button').removeClass('selected-btn');
		$('.settings-section-wrapper').hide();
		$('#' + sec_id).show();
		$(button).addClass('selected-btn');
	}

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
		validate_and_send(form, 'update_account', '#repeat-password', Flask.url_for('settings', { sel: 'account' }));
	});

	$('.settings-nav-button').click(function(){
		var selected = this;
		$('.settings-nav-button').removeClass('selected-btn');
		$('.settings-section-wrapper').hide();
		$(this).addClass('selected-btn');
		$(this).blur();
		var section_id = '#' + $(this).data('section');
		$(section_id).show();
	});

	$('input[name="city"]').blur(function(){
		var name = $(this).val();
		var regex = name_regexp(true);
		offline_check(this, regex.test(name), 'City can\'t have special characters.');
	});

	$('#address-update-form').submit(function(e){
		e.preventDefault();
		var form = this;
		validate_and_send(form, 'add_address', '', Flask.url_for('settings', { sel: 'address' }));
	});

	$('.addr-delete').click(function(){
		var address_id = $(this).data('aid');
		var address_name = $(this).data('aname');
		$('#address-name-del').text(address_name);
		$('#delete-btn', '#delete-address').unbind();
		$('#delete-btn', '#delete-address').click(function(){
			$.ajax({
				url: Flask.url_for('delete_address'),
				type: 'DELETE',
				data: { address_id: address_id },
				success: function(data) {
					if(data.error) {
						var error_place = $('.modal-error-msg', '#delete-address');
						generateMessage('danger', error_place, data.error);
					} else {
						window.location.href = Flask.url_for('settings', { sel: 'address' });
					}
				}
			});
		});
		$('#delete-address').modal('show');
	});
});

